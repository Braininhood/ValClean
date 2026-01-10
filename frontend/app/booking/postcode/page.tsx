'use client'

/**
 * Booking Step 1: Postcode Entry
 * Route: /booking/postcode (Public - Guest Checkout)
 * 
 * This is the first step of the booking flow.
 * No login/registration required.
 */
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useBookingStore } from '@/store/booking-store'
import { validateUKPostcode, formatPostcode } from '@/lib/utils'

export default function PostcodePage() {
  const router = useRouter()
  const { postcode, setPostcode } = useBookingStore()
  const [inputValue, setInputValue] = useState(postcode || '')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const formatted = formatPostcode(inputValue)
    
    if (!validateUKPostcode(formatted)) {
      setError('Please enter a valid UK postcode (e.g., SW1A 1AA)')
      return
    }

    setPostcode(formatted)
    router.push('/booking/services')
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Book Your Service</h1>
          <p className="text-muted-foreground">
            Enter your postcode to see available services in your area
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="postcode" className="block text-sm font-medium mb-2">
              Your Postcode
            </label>
            <input
              id="postcode"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value.toUpperCase())}
              placeholder="e.g., SW1A 1AA"
              required
              className="w-full px-4 py-3 text-lg border border-border rounded-lg focus:ring-2 focus:ring-ring focus:border-ring"
              autoFocus
            />
            <p className="mt-2 text-sm text-muted-foreground">
              We'll show you services available in your area
            </p>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            Continue
          </button>
        </form>

        <div className="text-center text-sm text-muted-foreground">
          <p>
            <span className="font-medium">No login required!</span> You can book as a guest.
          </p>
        </div>
      </div>
    </div>
  )
}
