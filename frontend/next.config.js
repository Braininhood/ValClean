/** @type {import('next').NextConfig} */

// Build CSP connect-src: allow API and Supabase
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const apiOrigin = apiUrl ? new URL(apiUrl).origin : 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Allow build to complete while ESLint warnings are cleaned up (remove when ready)
  eslint: { ignoreDuringBuilds: true },

  // Allow 127.0.0.1 in dev so _next/* and webpack-hmr work when opening app at http://127.0.0.1:3000
  allowedDevOrigins: [
    '127.0.0.1', 'localhost',
    'http://127.0.0.1:3000', 'http://localhost:3000',
    '13.135.109.229', 'ec2-13-135-109-229.eu-west-2.compute.amazonaws.com',
    'https://13.135.109.229', 'https://ec2-13-135-109-229.eu-west-2.compute.amazonaws.com',
  ],

  // Content-Security-Policy and other security headers
  async headers() {
    const isProd = process.env.NODE_ENV === 'production';
    const cspParts = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: blob: https:",
      "font-src 'self' data: https://fonts.gstatic.com https://fonts.googleapis.com",
      `connect-src 'self' ${apiOrigin} https://*.supabase.co wss://*.supabase.co https://accounts.google.com https://*.googleapis.com`,
      "frame-src 'self' https://accounts.google.com https://*.supabase.co",
      "frame-ancestors 'self'",
      "base-uri 'self'",
      "form-action 'self'",
      "object-src 'none'",
    ];
    if (isProd) {
      cspParts.push("upgrade-insecure-requests");
    }
    const csp = cspParts.join('; ');

    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(self)' },
          { key: 'Content-Security-Policy', value: csp },
        ],
      },
    ];
  },

  // WebSocket configuration for HMR (Hot Module Reload)
  // Configure WebSocket server for HMR to work properly
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Use polling for file watching (more reliable than WebSockets on some systems)
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300,
        ignored: /node_modules/,
      };
      // Avoid eval-source-map on Windows: multiline banner comments + CRLF can cause
      // "unterminated comment" in layout.js. Use cheap-module-source-map so chunks parse.
      config.devtool = 'cheap-module-source-map';
    }
    return config;
  },
  
  // Suppress WebSocket connection warnings
  devIndicators: {
    buildActivity: false,
  },
  
  // Experimental features for better HMR support
  experimental: {
    webpackBuildWorker: false,
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
    domains: ['localhost', 'valclean.uk', '13.135.109.229', 'ec2-13-135-109-229.eu-west-2.compute.amazonaws.com'],
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
  
  // PWA configuration
  // Note: Service worker and offline support can be added with next-pwa package if needed
  
  // Allow cross-origin requests in development (fixes blocked _next/* resource warnings)
  // Note: This is a Next.js 14+ feature
  // The warning about blocked cross-origin requests is usually harmless in development
};

module.exports = nextConfig;
