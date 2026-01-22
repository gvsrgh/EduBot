/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api',
  },
  
  // Production optimizations
  swcMinify: true,
  
  // Image optimization
  images: {
    domains: [],
  },
}

module.exports = nextConfig
