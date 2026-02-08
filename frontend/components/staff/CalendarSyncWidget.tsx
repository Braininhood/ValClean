'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api/client'
import { CALENDAR_ENDPOINTS } from '@/lib/api/endpoints'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface CalendarStatus {
  calendar_sync_enabled: boolean
  calendar_provider: 'none' | 'google' | 'outlook' | 'apple'
  has_access_token: boolean
  has_refresh_token: boolean
  last_sync_at: string | null
  last_sync_error: string | null
}

export function CalendarSyncWidget() {
  const _router = useRouter()
  const [status, setStatus] = useState<CalendarStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    fetchStatus()
  }, [])

  const fetchStatus = async () => {
    try {
      setLoading(true)
      const res = await apiClient.get(CALENDAR_ENDPOINTS.STATUS)
      if (res.data.success && res.data.data) {
        setStatus(res.data.data)
      }
    } catch (_e: unknown) {
      // If status fetch fails, assume not connected
      setStatus({
        calendar_sync_enabled: false,
        calendar_provider: 'none',
        has_access_token: false,
        has_refresh_token: false,
        last_sync_at: null,
        last_sync_error: null,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    try {
      setSyncing(true)
      const res = await apiClient.post(CALENDAR_ENDPOINTS.SYNC)
      if (res.data.success) {
        fetchStatus() // Refresh status
      }
    } catch (_e: unknown) {
      console.error('Sync failed:', _e)
    } finally {
      setSyncing(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-card border rounded-lg p-4">
        <div className="text-sm text-muted-foreground">Loading calendar status...</div>
      </div>
    )
  }

  const isConnected = status?.calendar_sync_enabled && status.calendar_provider !== 'none'

  return (
    <div className="bg-card border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold">Calendar Sync</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Sync your jobs with your calendar
          </p>
        </div>
        <Link href="/st/calendar/settings">
          <Button variant="outline" size="sm">
            Settings
          </Button>
        </Link>
      </div>

      {isConnected ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${status.has_access_token ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            <span className="text-muted-foreground">
              Connected to {status.calendar_provider === 'google' ? 'Google Calendar' : 
                           status.calendar_provider === 'outlook' ? 'Microsoft Outlook' : 
                           'Apple Calendar'}
            </span>
          </div>
          {status.last_sync_at && (
            <div className="text-xs text-muted-foreground">
              Last sync: {new Date(status.last_sync_at).toLocaleString()}
            </div>
          )}
          {status.last_sync_error && (
            <div className="text-xs text-destructive">
              Error: {status.last_sync_error}
            </div>
          )}
          <Button 
            onClick={handleSync} 
            disabled={syncing}
            size="sm"
            variant="outline"
            className="w-full mt-2"
          >
            {syncing ? 'Syncing...' : 'Sync Now'}
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            No calendar connected
          </p>
          <Link href="/st/calendar/settings">
            <Button size="sm" className="w-full">
              Connect Calendar
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}
