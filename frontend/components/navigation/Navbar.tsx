/**
 * Navigation Bar Component
 * 
 * Role-based navigation with logout functionality.
 */
'use client'

import Link from 'next/link'
import { useAuthContext } from '@/components/auth/AuthProvider'
import { RoleBasedRoute } from '@/components/auth/RoleBasedRoute'
import type { UserRole } from '@/types/auth'

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuthContext()

  if (!isAuthenticated || !user) {
    return (
      <nav className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold">
            VALClean
          </Link>
          <div className="flex gap-4">
            <Link href="/login" className="text-sm hover:underline">
              Login
            </Link>
            <Link href="/register" className="text-sm hover:underline">
              Register
            </Link>
            <Link href="/booking" className="text-sm hover:underline">
              Book Now
            </Link>
          </div>
        </div>
      </nav>
    )
  }

  const rolePrefix = getRolePrefix(user.role)
  const userDisplayName = user.first_name && user.last_name 
    ? `${user.first_name} ${user.last_name}`
    : user.email

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href={`/${rolePrefix}/dashboard`} className="text-xl font-bold">
          VALClean
        </Link>
        <div className="flex gap-6 items-center">
          {/* Role-based navigation links */}
          <RoleBasedRoute allowedRoles="customer">
            <Link href="/cus/dashboard" className="text-sm hover:underline">
              Dashboard
            </Link>
            <Link href="/cus/bookings" className="text-sm hover:underline">
              Bookings
            </Link>
            <Link href="/cus/subscriptions" className="text-sm hover:underline">
              Subscriptions
            </Link>
            <Link href="/cus/orders" className="text-sm hover:underline">
              Orders
            </Link>
            <Link href="/cus/profile" className="text-sm hover:underline">
              Profile
            </Link>
          </RoleBasedRoute>

          <RoleBasedRoute allowedRoles="staff">
            <Link href="/st/dashboard" className="text-sm hover:underline">
              Dashboard
            </Link>
            <Link href="/st/jobs" className="text-sm hover:underline">
              Jobs
            </Link>
            <Link href="/st/schedule" className="text-sm hover:underline">
              Schedule
            </Link>
          </RoleBasedRoute>

          <RoleBasedRoute allowedRoles="manager">
            <Link href="/man/dashboard" className="text-sm hover:underline">
              Dashboard
            </Link>
            <Link href="/man/appointments" className="text-sm hover:underline">
              Appointments
            </Link>
            <Link href="/man/staff" className="text-sm hover:underline">
              Staff
            </Link>
            <Link href="/man/customers" className="text-sm hover:underline">
              Customers
            </Link>
          </RoleBasedRoute>

          <RoleBasedRoute allowedRoles="admin">
            <Link href="/ad/dashboard" className="text-sm hover:underline">
              Dashboard
            </Link>
            <Link href="/ad/appointments" className="text-sm hover:underline">
              Appointments
            </Link>
            <Link href="/ad/staff" className="text-sm hover:underline">
              Staff
            </Link>
            <Link href="/ad/customers" className="text-sm hover:underline">
              Customers
            </Link>
            <Link href="/ad/managers" className="text-sm hover:underline">
              Managers
            </Link>
          </RoleBasedRoute>

          {/* User info and logout */}
          <div className="flex items-center gap-4 border-l pl-4">
            <span className="text-sm text-muted-foreground">
              {userDisplayName}
            </span>
            <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">
              {user.role.toUpperCase()}
            </span>
            <button
              onClick={() => logout()}
              className="text-sm text-destructive hover:underline"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

function getRolePrefix(role: UserRole): string {
  const roleMap: Record<UserRole, string> = {
    customer: 'cus',
    staff: 'st',
    manager: 'man',
    admin: 'ad',
  }
  return roleMap[role] || 'cus'
}
