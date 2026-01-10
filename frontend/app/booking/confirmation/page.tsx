'use client'

/**
 * Booking Step 6: Confirmation & Account Linking
 * Route: /booking/confirmation (Public - Guest Checkout)
 * 
 * After order completion:
 * - Show confirmation with order number
 * - Option to login and link order to account (if email matches)
 * - Option to register (pre-filled details)
 * - Option to skip (guest order continues to work)
 */
export default function ConfirmationPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">Booking Confirmed!</h1>
      
      <div className="space-y-6">
        <div className="p-6 bg-muted rounded-lg">
          <p className="text-muted-foreground mb-4">
            Confirmation page will be implemented in Week 3.
          </p>
          <p className="font-medium">Features:</p>
          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground mt-2">
            <li>Order number and tracking token</li>
            <li>Email confirmation sent</li>
            <li>Account linking prompt (optional):
              <ul className="list-disc list-inside ml-4 mt-1">
                <li>If email matches existing account: "Login to link this order?"</li>
                <li>If email is new: "Create an account? (Optional)"</li>
                <li>"Skip" option - guest order continues to work</li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
