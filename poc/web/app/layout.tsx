import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Strategy Review — GF Hackathon PoC",
  description:
    "Query global health strategy documents using AI-powered analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
