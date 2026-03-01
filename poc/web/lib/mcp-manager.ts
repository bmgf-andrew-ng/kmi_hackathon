/**
 * MCP Client Manager — spawns strategy-review and neo4j MCP servers as child
 * processes using StdioClientTransport and routes tool calls to them.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import type { Tool } from "@anthropic-ai/sdk/resources/messages.mjs";

type McpServerConfig = {
  command: string;
  args: string[];
  env: Record<string, string>;
};

type ConnectedServer = {
  client: Client;
  transport: StdioClientTransport;
  tools: Map<string, { name: string; description: string; inputSchema: object }>;
};

// Resolve MCP server configs from environment — mirrors .mcp.json but uses
// Docker service hostnames (set via containerEnv in devcontainer.json).
function getServerConfigs(): Record<string, McpServerConfig> {
  const workspaceRoot =
    process.env.WORKSPACE_ROOT || "/workspaces/gf-hackathon";

  return {
    "strategy-review": {
      command: `${workspaceRoot}/poc/.venv/bin/uv`,
      args: [
        "run",
        "--directory",
        `${workspaceRoot}/poc/mcp-servers/strategy-review`,
        "strategy-review-mcp",
      ],
      env: {
        OPENSEARCH_URL: process.env.OPENSEARCH_URL || "http://opensearch:9200",
        OPENSEARCH_USER: process.env.OPENSEARCH_USER || "admin",
        OPENSEARCH_PASSWORD: process.env.OPENSEARCH_PASSWORD || "admin",
        AZURE_STORAGE_BLOB_ENDPOINT:
          process.env.AZURE_STORAGE_BLOB_ENDPOINT ||
          "http://azurite:10000/devstoreaccount1",
        AZURE_STORAGE_CONTAINER:
          process.env.AZURE_STORAGE_CONTAINER || "strategy-pages",
      },
    },
    neo4j: {
      command: `${workspaceRoot}/poc/.venv/bin/uvx`,
      args: ["mcp-neo4j-cypher"],
      env: {
        NEO4J_URI: process.env.NEO4J_URI || "bolt://neo4j:7687",
        NEO4J_USERNAME: process.env.NEO4J_USER || "neo4j",
        NEO4J_PASSWORD: process.env.NEO4J_PASSWORD || "password",
        NEO4J_DATABASE: "neo4j",
      },
    },
  };
}

class McpManager {
  private servers = new Map<string, ConnectedServer>();
  private initialising: Promise<void> | null = null;

  /** Ensure all servers are connected. Idempotent — safe to call repeatedly. */
  async initialise(): Promise<void> {
    if (this.initialising) return this.initialising;
    this.initialising = this._connect();
    return this.initialising;
  }

  private async _connect(): Promise<void> {
    const configs = getServerConfigs();

    const results = await Promise.allSettled(
      Object.entries(configs).map(async ([name, config]) => {
        if (this.servers.has(name)) return;

        console.log(`[mcp-manager] Connecting to ${name}...`);

        const transport = new StdioClientTransport({
          command: config.command,
          args: config.args,
          env: { ...process.env, ...config.env } as Record<string, string>,
        });

        const client = new Client(
          { name: `web-${name}`, version: "1.0.0" },
          { capabilities: {} }
        );

        await client.connect(transport);

        const { tools: toolList } = await client.listTools();
        const tools = new Map(
          toolList.map((t) => [
            t.name,
            {
              name: t.name,
              description: t.description || "",
              inputSchema: t.inputSchema,
            },
          ])
        );

        this.servers.set(name, { client, transport, tools });
        console.log(
          `[mcp-manager] ${name} connected — ${tools.size} tools: ${[...tools.keys()].join(", ")}`
        );
      })
    );

    for (const result of results) {
      if (result.status === "rejected") {
        console.error("[mcp-manager] Server connection failed:", result.reason);
      }
    }
  }

  /** Get all tool definitions formatted for the Anthropic API. */
  getToolDefinitions(): Tool[] {
    const tools: Tool[] = [];
    for (const [serverName, server] of this.servers) {
      for (const [, tool] of server.tools) {
        tools.push({
          name: `${serverName}__${tool.name}`,
          description: `[${serverName}] ${tool.description}`,
          input_schema: tool.inputSchema as Tool.InputSchema,
        });
      }
    }
    return tools;
  }

  /** Call a tool on the appropriate MCP server. Tool name format: serverName__toolName */
  async callTool(
    prefixedName: string,
    args: Record<string, unknown>
  ): Promise<unknown> {
    const separatorIndex = prefixedName.indexOf("__");
    if (separatorIndex === -1) {
      throw new Error(`Invalid tool name format: ${prefixedName}`);
    }

    const serverName = prefixedName.slice(0, separatorIndex);
    const toolName = prefixedName.slice(separatorIndex + 2);

    const server = this.servers.get(serverName);
    if (!server) {
      throw new Error(`MCP server not found: ${serverName}`);
    }

    console.log(`[mcp-manager] Calling ${serverName}.${toolName}`, args);

    const result = await server.client.callTool({
      name: toolName,
      arguments: args,
    });

    return result.content;
  }

  /** Gracefully shut down all MCP servers. */
  async shutdown(): Promise<void> {
    for (const [name, server] of this.servers) {
      try {
        await server.client.close();
        console.log(`[mcp-manager] ${name} disconnected`);
      } catch (e) {
        console.error(`[mcp-manager] Error shutting down ${name}:`, e);
      }
    }
    this.servers.clear();
    this.initialising = null;
  }
}

// Module-level singleton — lives for the lifetime of the Next.js process.
// In dev mode, use globalThis to survive hot reloads.
const globalForMcp = globalThis as unknown as {
  mcpManager?: McpManager;
  mcpShutdownRegistered?: boolean;
};
export const mcpManager = globalForMcp.mcpManager ?? new McpManager();
if (process.env.NODE_ENV !== "production") {
  globalForMcp.mcpManager = mcpManager;
}

// Graceful shutdown — clean up child processes on SIGTERM/SIGINT.
// Guard against re-registering on hot reloads.
if (!globalForMcp.mcpShutdownRegistered) {
  const shutdown = () => {
    mcpManager.shutdown().finally(() => process.exit(0));
  };
  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);
  globalForMcp.mcpShutdownRegistered = true;
}
