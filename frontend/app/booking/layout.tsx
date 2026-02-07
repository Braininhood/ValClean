'use client'

/**
 * Booking layout: show auth banner on all booking steps so users know
 * whether they're guest or logged in.
 */
import { BookingAuthBanner } from '@/components/booking/BookingAuthBanner'

export default function BookingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto p-4 md:p-6">
        <BookingAuthBanner />
        {children}
      </div>
    </div>
  )
}
