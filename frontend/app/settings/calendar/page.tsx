'use client'

/**
 * Calendar Sync Settings (all roles).
 * Route: /settings/calendar
 * Staff are redirected to /st/calendar/settings for role-specific URL.
 * OAuth callbacks redirect here with ?connected=google|outlook or ?error=...
 */
import { Suspense, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { useAuthContext } from '@/components/auth/AuthProvider'
import { CalendarSettingsContent } from '@/components/calendar/CalendarSettingsContent'

function CalendarSettingsPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuthContext()

  // Staff use role-specific URL /st/calendar/settings (same API, scoped by backend)
  useEffect(() => {
    if (user?.role === 'staff') {
      const q = searchParams?.toString()
      router.replace(q ? `/st/calendar/settings?${q}` : '/st/calendar/settings')
    }
  }, [user?.role, router, searchParams])

  if (user?.role === 'staff') {
    return null // redirecting to /st/calendar/settings
  }

  return (
    <ProtectedRoute requiredRole={['admin', 'manager', 'staff', 'customer']}>
      <CalendarSettingsContent />
    </ProtectedRoute>
  )
}

export default function CalendarSettingsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p className="text-muted-foreground">Loading...</p></div>}>
      <CalendarSettingsPageContent />
    </Suspense>
  )
}
