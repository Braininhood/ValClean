/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // API proxy for development (optional - frontend and backend run separately)
  // Note: Frontend makes direct API calls, so rewrites are not needed
  // async rewrites() {
  //   const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: `${apiUrl}/:path*`,
  //     },
  //   ];
  // },
  
  // Image domains (for external images if needed)
  images: {
    domains: ['localhost', 'valclean.uk'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.googleusercontent.com',
      },
      {
        protocol: 'https',
        hostname: '**.googleapis.com',
      },
    ],
  },
  
  // Environment variables available on client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
};

module.exports = nextConfig;
