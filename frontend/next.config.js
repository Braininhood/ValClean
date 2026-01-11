/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // WebSocket configuration for HMR (Hot Module Reload)
  // Suppress WebSocket errors in development
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Suppress WebSocket connection errors in browser console
      config.watchOptions = {
        ...config.watchOptions,
        poll: 1000, // Check for changes every second as fallback
        aggregateTimeout: 300,
      };
      // Ignore WebSocket connection errors in console
      config.ignoreWarnings = [
        { module: /node_modules/ },
        { message: /Failed to parse source map/ },
        { message: /can't establish a connection/ },
        { message: /websocket/i },
        { message: /webpack-hmr/i },
        { message: /WebSocket/i },
      ];
    }
    return config;
  },
  
  // Suppress WebSocket connection warnings
  devIndicators: {
    buildActivity: false,
  },
  
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
  
  // Allow cross-origin requests in development (fixes blocked _next/* resource warnings)
  allowedDevOrigins: [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    '127.0.0.1:3000',
    'localhost:3000',
  ],
};

module.exports = nextConfig;
