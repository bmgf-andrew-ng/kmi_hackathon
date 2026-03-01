"use client";

import { useState, useRef, useEffect } from "react";
import { MessageBubble } from "@/components/message";
import type { Message } from "@/app/page";

export function Chat({
  messages,
  isLoading,
  onSend,
  onClear,
}: {
  messages: Message[];
  isLoading: boolean;
  onSend: (message: string) => void;
  onClear: () => void;
}) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    setInput("");
    onSend(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <>
      {/* Message list */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "1rem 0",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "var(--text-muted)",
              textAlign: "center",
              gap: "0.75rem",
            }}
          >
            <p style={{ fontSize: "1.1rem" }}>
              Ask a question about global health strategies
            </p>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.4rem",
                fontSize: "0.85rem",
              }}
            >
              <p>&quot;What funding is allocated to TB elimination?&quot;</p>
              <p>&quot;What does the GH Strategy say about malaria prevention?&quot;</p>
              <p>&quot;Which countries prioritise maternal health?&quot;</p>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {isLoading &&
          messages[messages.length - 1]?.role !== "assistant" && (
            <div
              style={{
                padding: "0.75rem 1rem",
                color: "var(--text-muted)",
                fontSize: "0.85rem",
              }}
            >
              Thinking...
            </div>
          )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          gap: "0.5rem",
          padding: "0.75rem 0 1rem",
          borderTop: "1px solid var(--border)",
          flexShrink: 0,
        }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about global health strategies..."
          disabled={isLoading}
          rows={1}
          style={{
            flex: 1,
            padding: "0.6rem 0.75rem",
            fontSize: "0.9rem",
            fontFamily: "var(--font-sans)",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            color: "var(--text-primary)",
            resize: "none",
            outline: "none",
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          style={{
            padding: "0.6rem 1.25rem",
            fontSize: "0.85rem",
            fontWeight: 500,
            background:
              isLoading || !input.trim()
                ? "var(--bg-tertiary)"
                : "var(--accent)",
            color:
              isLoading || !input.trim()
                ? "var(--text-muted)"
                : "#ffffff",
            border: "none",
            borderRadius: "var(--radius)",
            cursor:
              isLoading || !input.trim() ? "not-allowed" : "pointer",
          }}
        >
          Send
        </button>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            disabled={isLoading}
            style={{
              padding: "0.6rem 0.75rem",
              fontSize: "0.85rem",
              background: "var(--bg-secondary)",
              color: "var(--text-secondary)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              cursor: isLoading ? "not-allowed" : "pointer",
            }}
          >
            Clear
          </button>
        )}
      </form>
    </>
  );
}
