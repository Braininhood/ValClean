/**
 * SEO config and helpers (Phase 5).
 * Used for metadata, Open Graph, JSON-LD.
 */
const siteName = 'VALClean'
const siteTagline = 'Professional booking system for cleaning services'
const defaultTitle = `${siteName} Booking System`
const defaultDescription = `${siteTagline}. Book cleaning services online.`

export const siteConfig = {
  name: siteName,
  tagline: siteTagline,
  title: defaultTitle,
  description: defaultDescription,
  /** Base URL for canonical and Open Graph (set NEXT_PUBLIC_APP_URL in production). */
  url:
    typeof process !== 'undefined' && process.env.NEXT_PUBLIC_APP_URL
      ? process.env.NEXT_PUBLIC_APP_URL.replace(/\/$/, '')
      : typeof process !== 'undefined' && process.env.VERCEL_URL
        ? `https://${process.env.VERCEL_URL}`
        : 'http://localhost:3000',
  locale: 'en_GB',
  twitterHandle: '',
}

export function getAbsoluteUrl(path: string): string {
  const base = siteConfig.url
  const p = path.startsWith('/') ? path : `/${path}`
  return base.replace(/\/$/, '') + p
}

/** JSON-LD Organization for home/booking pages. */
export function jsonLdOrganization() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: siteConfig.name,
    description: siteConfig.description,
    url: siteConfig.url,
  }
}

/** JSON-LD WebSite with search action (for sitelinks search box). */
export function jsonLdWebSite() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: siteConfig.name,
    description: siteConfig.description,
    url: siteConfig.url,
    potentialAction: {
      '@type': 'SearchAction',
      target: { '@type': 'EntryPoint', urlTemplate: siteConfig.url + '/booking?q={search_term_string}' },
      'query-input': 'required name=search_term_string',
    },
  }
}

/** JSON-LD LocalBusiness (optional – use if you have a physical location). */
export function jsonLdLocalBusiness(overrides?: Record<string, unknown>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: siteConfig.name,
    description: siteConfig.description,
    url: siteConfig.url,
    ...overrides,
  }
}
