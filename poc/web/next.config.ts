import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // MCP servers are spawned as child processes — need long API route timeouts
  serverExternalPackages: ["@modelcontextprotocol/sdk"],
};

export default nextConfig;
