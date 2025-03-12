import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  compress: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
