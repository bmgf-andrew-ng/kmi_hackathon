"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "@/app/page";

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        padding: "0.5rem 0",
      }}
    >
      <div
        style={{
          maxWidth: isUser ? "75%" : "90%",
          padding: "0.75rem 1rem",
          borderRadius: "var(--radius)",
          background: isUser ? "var(--accent-subtle)" : "var(--bg-secondary)",
          border: `1px solid ${isUser ? "var(--accent)" : "var(--border)"}`,
          fontSize: "0.9rem",
          lineHeight: 1.6,
        }}
      >
        {isUser ? (
          <p style={{ margin: 0 }}>{message.content}</p>
        ) : (
          <div className="markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
