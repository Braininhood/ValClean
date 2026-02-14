import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/auth/AuthProvider'

const inter = Inter({ subsets: ['latin'], preload: false })

// Use only string literals in metadata so the serialized layout.js never contains
// unescaped quotes or dynamic values (fixes "literal not terminated" when logged in).
const METADATA_BASE = 'http://localhost:3000'

export const metadata: Metadata = {
  metadataBase: new URL(METADATA_BASE),
  title: {
    default: 'VALClean Booking System',
    template: '%s | VALClean',
  },
  description: 'Professional booking system for cleaning services. Book cleaning services online.',
  icons: { icon: '/favicon.ico' },
  manifest: '/manifest.json',
  appleWebApp: { capable: true, statusBarStyle: 'default', title: 'VALClean' },
  openGraph: {
    type: 'website',
    locale: 'en_GB',
    url: METADATA_BASE,
    siteName: 'VALClean',
    title: 'VALClean Booking System',
    description: 'Professional booking system for cleaning services. Book cleaning services online.',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VALClean Booking System',
    description: 'Professional booking system for cleaning services. Book cleaning services online.',
  },
  robots: { index: true, follow: true, googleBot: { index: true, follow: true } },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: '#000000',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
