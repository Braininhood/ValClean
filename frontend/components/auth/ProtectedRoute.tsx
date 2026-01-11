/**
 * Protected Route Component
 * 
 * Protects routes based on authentication and role requirements.
 */
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthContext } from './AuthProvider'
import type { UserRole } from '@/types/auth'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: UserRole | UserRole[]
  redirectTo?: string
}

export function ProtectedRoute({ 
  children, 
  requiredRole,
  redirectTo = '/login'
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuthContext()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading) {
      // Check authentication
      if (!isAuthenticated || !user) {
        router.push(redirectTo)
        return
      }

      // Check role requirement
      if (requiredRole) {
        const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
        if (!allowedRoles.includes(user.role)) {
          // Redirect to appropriate dashboard based on user's role
          const rolePrefix = getRolePrefix(user.role)
          router.push(`/${rolePrefix}/dashboard`)
          return
        }
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole, router, redirectTo])

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // Show nothing while redirecting
  if (!isAuthenticated || !user) {
    return null
  }

  // Check role if required
  if (requiredRole) {
    const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
    if (!allowedRoles.includes(user.role)) {
      return null
    }
  }

  return <>{children}</>
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
