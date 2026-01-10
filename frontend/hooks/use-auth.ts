/**
 * Authentication Hook
 * 
 * Manages authentication state and provides auth methods.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api/client'
import { PUBLIC_ENDPOINTS } from '@/lib/api/endpoints'
import type { LoginRequest, RegisterRequest, User } from '@/types/auth'

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Check authentication status on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setIsAuthenticated(false)
        setIsLoading(false)
        return
      }

      // Verify token by making a request to user profile
      // This will be implemented in Week 2 when auth endpoints are ready
      setIsAuthenticated(true)
      setIsLoading(false)
    } catch (error) {
      setIsAuthenticated(false)
      setIsLoading(false)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await apiClient.login(credentials.email, credentials.password)
      setUser(response.user)
      setIsAuthenticated(true)
      router.push(`/${getRolePrefix(response.user.role)}/dashboard`)
      return response
    } catch (error: any) {
      throw error.response?.data || error
    }
  }

  const register = async (data: RegisterRequest) => {
    try {
      const response = await apiClient.post(PUBLIC_ENDPOINTS.AUTH.REGISTER, data)
      // After registration, automatically login
      if (response.data.access) {
        await login({ email: data.email, password: data.password })
      }
      return response.data
    } catch (error: any) {
      throw error.response?.data || error
    }
  }

  const logout = async () => {
    await apiClient.logout()
    setUser(null)
    setIsAuthenticated(false)
    router.push('/login')
  }

  const getRolePrefix = (role: UserRole): string => {
    const roleMap: Record<UserRole, string> = {
      customer: 'cus',
      staff: 'st',
      manager: 'man',
      admin: 'ad',
    }
    return roleMap[role]
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
  }
}
