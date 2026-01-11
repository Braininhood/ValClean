'use client'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'

/**
 * Staff Dashboard
 * Route: /st/dashboard (Security: /st/)
 */
export default function StaffDashboard() {
  return (
    <ProtectedRoute requiredRole="staff">
      <DashboardLayout>
        <div className="container mx-auto p-8">
          <h1 className="text-3xl font-bold mb-8">Staff Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your staff dashboard. View your assigned jobs and manage your schedule here.
          </p>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
