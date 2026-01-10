'use client'

/**
 * Booking Step 2: Service Selection
 * Route: /booking/services (Public - Guest Checkout)
 * 
 * Shows services available in the selected postcode area.
 */
'use client'

import { useBookingStore } from '@/store/booking-store'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ServicesPage() {
  const router = useRouter()
  const { postcode, setSelectedService, setBookingType } = useBookingStore()

  useEffect(() => {
    if (!postcode) {
      router.push('/booking/postcode')
    }
  }, [postcode, router])

  const handleServiceSelect = (serviceId: number) => {
    setSelectedService(serviceId)
    router.push('/booking/date-time')
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">Select a Service</h1>
      <p className="text-muted-foreground mb-8">
        Services available in {postcode}
      </p>

      <div className="space-y-4">
        <p className="text-muted-foreground">
          Service listing will be implemented in Week 3.
          Services will be filtered by postcode area.
        </p>
      </div>
    </div>
  )
}
