'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'

export default function RegisterPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { register, isLoading } = useAuth()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    password_confirm: '',
  })
  const [error, setError] = useState<string | null>(null)

  // Pre-fill email from query parameter (when redirected from login)
  useEffect(() => {
    const emailParam = searchParams.get('email')
    if (emailParam) {
      setFormData(prev => ({ ...prev, email: emailParam }))
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!formData.name || !formData.email || !formData.password) {
      setError('Please fill in all required fields')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match')
      return
    }

    try {
      const response = await register({
        email: formData.email,
        password: formData.password,
        name: formData.name,
        phone: formData.phone,
        role: 'customer',
      })
      
      // SECURITY: Check if backend returned redirect_to_login flag (email already exists)
      // This prevents user enumeration - backend returns 200 OK for both cases
      if (response.redirect_to_login || response.data?.redirect_to_login) {
        router.push(`/login?email=${encodeURIComponent(formData.email)}&message=${encodeURIComponent('This email is already registered. Please login instead.')}`)
        return
      }
      
      // Check if user is customer (this page is only for customers)
      if (response.user && response.user.role !== 'customer') {
        setError('Registration failed. Please use the correct registration page for your role.')
        return
      }
      
      // Redirect to customer dashboard
      router.push('/cus/dashboard')
    } catch (err: any) {
      // Handle other validation errors (password mismatch, invalid role, etc.)
      // Note: Email duplicates are now handled by redirect_to_login flag (returns 200 OK)
      const errorCode = err?.error?.code || err?.code
      const errorMessage = err?.error?.message || err?.message || 'Registration failed. Please try again.'
      
      // Extract field-specific errors from DRF validation errors
      const responseData = err?.response?.data || err
      let displayMessage = errorMessage
      
      // Check for field-specific validation errors (password, role, etc.)
      if (responseData) {
        const fieldErrors: string[] = []
        Object.keys(responseData).forEach(key => {
          if (Array.isArray(responseData[key])) {
            fieldErrors.push(`${key}: ${responseData[key][0]}`)
          } else if (typeof responseData[key] === 'string') {
            fieldErrors.push(responseData[key])
          }
        })
        if (fieldErrors.length > 0) {
          displayMessage = fieldErrors.join(', ')
        }
      }
      
      setError(displayMessage)
    }
  }

  const emailFromLogin = searchParams.get('email')

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-center">Create Account</h2>
          <p className="mt-2 text-center text-muted-foreground">
            Register for VALClean booking system
          </p>
          {emailFromLogin && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                This email is not registered. Please create an account to continue.
              </p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              Full Name
            </label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring"
            />
          </div>

          <div>
            <label htmlFor="phone" className="block text-sm font-medium mb-2">
              Phone (Optional)
            </label>
            <input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring"
            />
          </div>

          <div>
            <label htmlFor="password_confirm" className="block text-sm font-medium mb-2">
              Confirm Password
            </label>
            <input
              id="password_confirm"
              type="password"
              value={formData.password_confirm}
              onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })}
              required
              className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <div className="text-center text-sm text-muted-foreground">
          <p>
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:underline">
              Login
            </Link>
          </p>
          <p className="mt-2">
            <Link href="/forgot-password" className="text-primary hover:underline">
              Forgot password?
            </Link>
          </p>
          <p className="mt-4">
            <Link href="/booking" className="text-primary hover:underline">
              Continue as guest (No registration required)
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
