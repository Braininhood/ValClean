'use client'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'

/**
 * Customer Dashboard
 * Route: /cus/dashboard (Security: /cus/)
 */
export default function CustomerDashboard() {
  return (
    <ProtectedRoute requiredRole="customer">
      <DashboardLayout>
        <div className="container mx-auto p-8">
          <h1 className="text-3xl font-bold mb-8">Customer Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your customer dashboard. Manage your appointments, subscriptions, and orders here.
          </p>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
