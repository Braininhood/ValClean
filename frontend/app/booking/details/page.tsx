'use client'

/**
 * Booking Step 5: Guest Details & Payment
 * Route: /booking/details (Public - Guest Checkout)
 * 
 * NO LOGIN/REGISTRATION REQUIRED
 * Perfect for elderly customers who don't want to register.
 */
export default function GuestDetailsPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">Your Details</h1>
      <p className="text-muted-foreground mb-8">
        Complete your booking - <span className="font-medium">No account required!</span>
      </p>

      <div className="space-y-6">
        <p className="text-muted-foreground">
          Guest checkout form will be implemented in Week 3.
          Includes:
          - Name, email, phone
          - Address (Google Places autocomplete)
          - Payment details
          - Special instructions (optional)
        </p>

        <div className="p-6 bg-muted rounded-lg">
          <h3 className="font-semibold mb-2">Guest Checkout Benefits:</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
            <li>No login or registration required</li>
            <li>Perfect for elderly customers</li>
            <li>All features work without an account</li>
            <li>Optional account linking after order completion</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
