import { jsonLdOrganization, jsonLdWebSite } from '@/lib/seo'
import { HomeCTA } from '@/components/home/HomeCTA'

export default function Home() {
  const orgJsonLd = jsonLdOrganization()
  const webJsonLd = jsonLdWebSite()

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Structured data (Phase 5: SEO) */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webJsonLd) }}
      />
      <div className="text-center space-y-8">
        <h1 className="text-4xl font-bold">VALClean Booking System</h1>
        <p className="text-xl text-muted-foreground">
          Professional booking system for cleaning services
        </p>

        <HomeCTA />
      </div>
    </main>
  )
}
