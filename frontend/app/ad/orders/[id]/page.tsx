'use client'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api/client'
import { ADMIN_ENDPOINTS } from '@/lib/api/endpoints'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'

interface OrderItem {
  id: number
  service: { id: number; name: string }
  staff: { id: number; name: string } | null
  quantity: number
  unit_price: string
  total_price: string
  status: string
}

interface Order {
  id: number
  order_number: string
  status: string
  total_price: string
  payment_status: string
  scheduled_date: string | null
  scheduled_time: string | null
  address_line1: string
  address_line2: string | null
  city: string
  postcode: string
  country: string
  guest_email: string | null
  guest_name: string | null
  customer: { id: number; name: string; email: string } | null
  items: OrderItem[]
  created_at: string
}

/**
 * Admin Order Detail
 * Route: /ad/orders/[id] (Security: /ad/)
 */
export default function AdminOrderDetailPage() {
  const params = useParams()
  const id = params.id as string
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const res = await apiClient.get(ADMIN_ENDPOINTS.ORDERS.DETAIL(id))
        if (res.data.success && res.data.data) setOrder(res.data.data)
        else setError('Failed to load order')
      } catch (e) {
        setError((e as { message?: string })?.message ?? 'Failed to load order')
      } finally {
        setLoading(false)
      }
    }
    fetchOrder()
  }, [id])

  const name = order?.customer?.name ?? order?.guest_name ?? 'Guest'

  return (
    <ProtectedRoute requiredRole="admin">
      <DashboardLayout>
        <div className="container mx-auto p-8">
          <div className="flex items-center gap-4 mb-8">
            <Button variant="outline" asChild>
              <Link href="/ad/orders">← Orders</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/ad/dashboard">Dashboard</Link>
            </Button>
          </div>
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-lg">{error}</div>
          )}
          {loading ? (
            <div className="animate-pulse">Loading…</div>
          ) : order ? (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <h1 className="text-2xl font-bold">{order.order_number}</h1>
                <span className="capitalize px-3 py-1 rounded-full bg-muted">{order.status}</span>
              </div>
              <div className="grid md:grid-cols-2 gap-6 rounded-lg border border-border p-6">
                <div>
                  <h2 className="font-semibold mb-2">Customer</h2>
                  <p>{name}</p>
                  {(order.customer?.email ?? order.guest_email) && (
                    <p className="text-sm text-muted-foreground">
                      {order.customer?.email ?? order.guest_email}
                    </p>
                  )}
                </div>
                <div>
                  <h2 className="font-semibold mb-2">Schedule</h2>
                  <p>
                    {order.scheduled_date
                      ? new Date(order.scheduled_date).toLocaleDateString('en-GB', {
                          weekday: 'long',
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                        })
                      : '—'}
                  </p>
                  {order.scheduled_time && (
                    <p className="text-muted-foreground">{order.scheduled_time.slice(0, 5)}</p>
                  )}
                </div>
                <div className="md:col-span-2">
                  <h2 className="font-semibold mb-2">Address</h2>
                  <p>
                    {order.address_line1}
                    {order.address_line2 && `, ${order.address_line2}`}
                    <br />
                    {order.city}, {order.postcode} {order.country && `, ${order.country}`}
                  </p>
                </div>
              </div>
              <div className="rounded-lg border border-border p-6">
                <h2 className="font-semibold mb-4">Items</h2>
                <ul className="space-y-2">
                  {order.items.map((item) => (
                    <li key={item.id} className="flex justify-between py-2 border-b border-border last:border-0">
                      <span>
                        {item.service.name} × {item.quantity}
                        {item.staff && ` — ${item.staff.name}`}
                      </span>
                      <span>£{parseFloat(item.total_price).toFixed(2)}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-4 pt-4 border-t border-border font-semibold flex justify-between">
                  <span>Total</span>
                  <span>£{parseFloat(order.total_price).toFixed(2)}</span>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
