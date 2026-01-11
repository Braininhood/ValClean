'use client'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'

/**
 * Admin Dashboard
 * Route: /ad/dashboard (Security: /ad/)
 */
export default function AdminDashboard() {
  return (
    <ProtectedRoute requiredRole="admin">
      <DashboardLayout>
        <div className="container mx-auto p-8">
          <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to your admin dashboard. Manage the entire system, including staff, managers, customers, and appointments.
          </p>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
