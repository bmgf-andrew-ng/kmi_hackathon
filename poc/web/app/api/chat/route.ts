/**
 * POST /api/chat — Streaming API route with tool use loop.
 *
 * 1. Receives { messages, skill } from the frontend
 * 2. Selects system prompt based on skill
 * 3. Gets MCP tool definitions
 * 4. Calls AWS Bedrock (Claude Sonnet) with streaming
 * 5. On tool_use → routes to MCP server → returns tool_result → continues
 * 6. Streams text tokens to the browser via SSE
 */

import AnthropicBedrock from "@anthropic-ai/bedrock-sdk";
import type {
  MessageParam,
  ContentBlockParam,
  ToolResultBlockParam,
  ToolUseBlock,
} from "@anthropic-ai/sdk/resources/messages.mjs";
import { mcpManager } from "@/lib/mcp-manager";
import { getSystemPrompt } from "@/lib/system-prompts";
import type { Skill } from "@/components/skill-selector";

const MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0";
const MAX_TOOL_ROUNDS = 10;

function getBedrock(): AnthropicBedrock {
  const awsAccessKey = process.env.AWS_ACCESS_KEY_ID;
  const awsSecretKey = process.env.AWS_SECRET_ACCESS_KEY;
  if (!awsAccessKey || !awsSecretKey) {
    throw new Error(
      "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set"
    );
  }
  return new AnthropicBedrock({
    awsAccessKey,
    awsSecretKey,
    awsRegion: process.env.AWS_REGION || "us-east-1",
  });
}

export async function POST(request: Request) {
  const { messages, skill } = (await request.json()) as {
    messages: { role: "user" | "assistant"; content: string }[];
    skill: Skill;
  };

  if (!messages || messages.length === 0) {
    return new Response("Messages required", { status: 400 });
  }

  // Ensure MCP servers are connected
  await mcpManager.initialise();

  const bedrock = getBedrock();
  const systemPrompt = getSystemPrompt(skill);
  const tools = mcpManager.getToolDefinitions();

  // Build Anthropic-format messages
  const apiMessages: MessageParam[] = messages.map((m) => ({
    role: m.role,
    content: m.content,
  }));

  // Create a streaming response using SSE
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (type: string, content: string) => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type, content })}\n\n`)
        );
      };

      try {
        let currentMessages = [...apiMessages];
        let toolRounds = 0;

        while (toolRounds < MAX_TOOL_ROUNDS) {
          const response = await bedrock.messages.create({
            model: MODEL_ID,
            max_tokens: 4096,
            system: systemPrompt,
            messages: currentMessages,
            tools: tools.length > 0 ? tools : undefined,
            stream: true,
          });

          let currentToolUses: ToolUseBlock[] = [];
          let hasToolUse = false;

          for await (const event of response) {
            if (
              event.type === "content_block_delta" &&
              event.delta.type === "text_delta"
            ) {
              send("text", event.delta.text);
            }

            if (
              event.type === "content_block_start" &&
              event.content_block.type === "tool_use"
            ) {
              hasToolUse = true;
              currentToolUses.push({
                type: "tool_use",
                id: event.content_block.id,
                name: event.content_block.name,
                input: {},
              });
            }

            // Accumulate tool input JSON from deltas
            if (
              event.type === "content_block_delta" &&
              event.delta.type === "input_json_delta" &&
              currentToolUses.length > 0
            ) {
              const last = currentToolUses[currentToolUses.length - 1];
              // Accumulate raw JSON string — parse after block ends
              (last as unknown as { _rawInput: string })._rawInput =
                ((last as unknown as { _rawInput?: string })._rawInput || "") +
                event.delta.partial_json;
            }

            // Parse accumulated JSON when the block ends
            if (event.type === "content_block_stop" && currentToolUses.length > 0) {
              const last = currentToolUses[currentToolUses.length - 1];
              const raw = (last as unknown as { _rawInput?: string })._rawInput;
              if (raw) {
                try {
                  last.input = JSON.parse(raw);
                } catch {
                  // Leave input as empty object if parse fails
                }
                delete (last as unknown as { _rawInput?: string })._rawInput;
              }
            }
          }

          // If no tool use, we're done
          if (!hasToolUse) break;

          toolRounds++;

          // Execute all tool calls and build tool results
          const toolResults: ToolResultBlockParam[] = await Promise.all(
            currentToolUses.map(async (toolUse) => {
              try {
                send("text", `\n\n*Querying ${toolUse.name}...*\n\n`);
                const result = await mcpManager.callTool(
                  toolUse.name,
                  toolUse.input as Record<string, unknown>
                );
                return {
                  type: "tool_result" as const,
                  tool_use_id: toolUse.id,
                  content: JSON.stringify(result),
                };
              } catch (error) {
                const msg =
                  error instanceof Error ? error.message : String(error);
                return {
                  type: "tool_result" as const,
                  tool_use_id: toolUse.id,
                  content: `Tool call failed: ${msg}`,
                  is_error: true,
                };
              }
            })
          );

          // Build the assistant message content for the conversation history
          const assistantContent: ContentBlockParam[] = currentToolUses.map(
            (tu) => ({
              type: "tool_use" as const,
              id: tu.id,
              name: tu.name,
              input: tu.input as Record<string, unknown>,
            })
          );

          // Append assistant + tool_result messages and loop
          currentMessages = [
            ...currentMessages,
            { role: "assistant", content: assistantContent },
            { role: "user", content: toolResults },
          ];

          currentToolUses = [];
        }

        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
      } catch (error) {
        const msg = error instanceof Error ? error.message : String(error);
        console.error("[api/chat] Error:", msg);
        send("error", msg);
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
