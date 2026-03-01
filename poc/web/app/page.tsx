"use client";

import { useState, useCallback } from "react";
import { Chat } from "@/components/chat";
import { SkillSelector, type Skill } from "@/components/skill-selector";

export type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [skill, setSkill] = useState<Skill>("strategy-review");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = useCallback(
    async (userMessage: string) => {
      const newMessages: Message[] = [
        ...messages,
        { role: "user", content: userMessage },
      ];
      setMessages(newMessages);
      setIsLoading(true);

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: newMessages, skill }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API error ${response.status}: ${errorText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No response stream");

        const decoder = new TextDecoder();
        let assistantContent = "";

        setMessages([...newMessages, { role: "assistant", content: "" }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") break;
              try {
                const parsed = JSON.parse(data);
                if (parsed.type === "text") {
                  assistantContent += parsed.content;
                  setMessages([
                    ...newMessages,
                    { role: "assistant", content: assistantContent },
                  ]);
                } else if (parsed.type === "error") {
                  assistantContent += `\n\n**Error:** ${parsed.content}`;
                  setMessages([
                    ...newMessages,
                    { role: "assistant", content: assistantContent },
                  ]);
                }
              } catch {
                // Skip malformed JSON lines
              }
            }
          }
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";
        setMessages([
          ...newMessages,
          {
            role: "assistant",
            content: `**Error:** ${errorMessage}`,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, skill]
  );

  const handleClear = useCallback(() => {
    setMessages([]);
  }, []);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        maxWidth: "900px",
        margin: "0 auto",
        padding: "0 1rem",
      }}
    >
      <header
        style={{
          padding: "1rem 0",
          borderBottom: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
          flexShrink: 0,
        }}
      >
        <h1
          style={{
            fontSize: "1.1rem",
            fontWeight: 600,
            whiteSpace: "nowrap",
          }}
        >
          Strategy Review
        </h1>
        <SkillSelector selected={skill} onSelect={setSkill} />
      </header>

      <Chat
        messages={messages}
        isLoading={isLoading}
        onSend={handleSend}
        onClear={handleClear}
      />
    </div>
  );
}
