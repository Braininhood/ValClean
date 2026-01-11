'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login, isLoading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  // Read URL params once on mount (safely handle searchParams)
  useEffect(() => {
    try {
      if (searchParams) {
        const emailParam = searchParams.get('email')
        const messageParam = searchParams.get('message')
        
        if (emailParam) {
          setEmail(emailParam)
        }
        if (messageParam) {
          setMessage(messageParam)
        }
      }
    } catch (err) {
      // Silently handle any errors reading search params
      console.debug('Error reading search params:', err)
    }
    // Only run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!email || !password) {
      setError('Please enter both email and password')
      return
    }

    try {
      const response = await login({ email, password })
      // Check if user is customer (this page is only for customers)
      if (response.user.role !== 'customer') {
        setError('This login is only for customers. Please use the correct login page for your role.')
        return
      }
      // Redirect handled by useAuth hook (will go to /cus/dashboard)
    } catch (err: any) {
      // SECURITY: Backend always returns "Invalid email or password" for both cases
      // (email not found OR wrong password) to prevent user enumeration
      // Frontend shows the generic error message without revealing which case it is
      const errorCode = err?.error?.code || err?.code
      const errorMessage = err?.error?.message || err?.message || 'Invalid email or password'
      
      // Show generic error message (prevents user enumeration)
      // Always shows "Invalid email or password" regardless of actual issue
      setError(errorMessage)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-center">Login</h2>
          <p className="mt-2 text-center text-muted-foreground">
            Access your VALClean account
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {message && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">{message}</p>
            </div>
          )}
          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring"
            />
          </div>

          <div className="flex items-center justify-between">
            <Link
              href="/forgot-password"
              className="text-sm text-primary hover:underline"
            >
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="text-center text-sm text-muted-foreground">
          <p>
            Don't have an account?{' '}
            <Link href="/register" className="text-primary hover:underline">
              Register
            </Link>
          </p>
          <p className="mt-4">
            <Link href="/booking" className="text-primary hover:underline">
              Continue as guest (No login required)
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
