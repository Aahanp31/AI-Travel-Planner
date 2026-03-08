import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  compress: true,            // Enable gzip compression
  poweredByHeader: false,    // Remove X-Powered-By header for security
  reactStrictMode: true,     // Enable React strict mode for better error detection
};

export default nextConfig;
