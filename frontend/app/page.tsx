import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center space-y-8">
        <h1 className="text-4xl font-bold">VALClean Booking System</h1>
        <p className="text-xl text-muted-foreground">
          Professional booking system for cleaning services
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
          <Link
            href="/booking"
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            Book Now
          </Link>
          <Link
            href="/login"
            className="px-6 py-3 border border-border rounded-lg hover:bg-accent transition-colors"
          >
            Login
          </Link>
        </div>

        <div className="mt-12 text-sm text-muted-foreground">
          <p>Development: Frontend (localhost:3000) + Backend (localhost:8000)</p>
        </div>
      </div>
    </main>
  )
}
