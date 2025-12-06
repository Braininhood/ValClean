"""
Payment processing services for different payment gateways.
All API keys are stored in environment variables and loaded from settings.
"""
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import Payment


class PaymentService:
    """Base payment service class."""
    
    def __init__(self):
        self.gateway_name = None
    
    def create_payment(self, amount, customer_email, customer_name, description, metadata=None):
        """
        Create a payment intent/transaction.
        
        Args:
            amount: Decimal amount to charge
            customer_email: Customer email
            customer_name: Customer name
            description: Payment description
            metadata: Additional metadata dict
        
        Returns:
            dict with 'success', 'payment_id', 'redirect_url', 'error'
        """
        raise NotImplementedError("Subclasses must implement create_payment")
    
    def process_payment(self, payment_id, payment_data=None):
        """
        Process/confirm a payment.
        
        Args:
            payment_id: Payment intent/transaction ID
            payment_data: Additional payment data
        
        Returns:
            dict with 'success', 'status', 'transaction_id', 'error'
        """
        raise NotImplementedError("Subclasses must implement process_payment")
    
    def refund_payment(self, transaction_id, amount=None):
        """
        Refund a payment.
        
        Args:
            transaction_id: Original transaction ID
            amount: Amount to refund (None for full refund)
        
        Returns:
            dict with 'success', 'refund_id', 'error'
        """
        raise NotImplementedError("Subclasses must implement refund_payment")


class StripePaymentService(PaymentService):
    """Stripe payment service."""
    
    def __init__(self):
        super().__init__()
        self.gateway_name = 'stripe'
        # API keys will be loaded from settings
        # self.api_key = settings.STRIPE_SECRET_KEY
        # self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    
    def create_payment(self, amount, customer_email, customer_name, description, metadata=None):
        """
        Create Stripe Payment Intent.
        
        Note: Requires STRIPE_SECRET_KEY in settings.
        """
        # Check if Stripe is configured
        if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
            return {
                'success': False,
                'error': 'Stripe is not configured. Please add STRIPE_SECRET_KEY to settings.'
            }
        
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(float(amount) * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='gbp',  # British Pounds
                description=description,
                metadata={
                    'customer_email': customer_email,
                    'customer_name': customer_name,
                    **(metadata or {})
                },
                receipt_email=customer_email,
            )
            
            return {
                'success': True,
                'payment_id': intent.id,
                'client_secret': intent.client_secret,
                'redirect_url': None,  # Stripe uses client-side confirmation
            }
        except ImportError:
            return {
                'success': False,
                'error': 'Stripe library not installed. Install with: pip install stripe'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Stripe error: {str(e)}'
            }
    
    def process_payment(self, payment_id, payment_data=None):
        """Confirm Stripe Payment Intent."""
        if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
            return {
                'success': False,
                'error': 'Stripe is not configured.'
            }
        
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            intent = stripe.PaymentIntent.retrieve(payment_id)
            
            if intent.status == 'succeeded':
                return {
                    'success': True,
                    'status': 'completed',
                    'transaction_id': intent.id,
                }
            elif intent.status == 'requires_payment_method':
                return {
                    'success': False,
                    'status': 'pending',
                    'error': 'Payment requires additional authentication.'
                }
            else:
                return {
                    'success': False,
                    'status': intent.status,
                    'error': f'Payment status: {intent.status}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Stripe error: {str(e)}'
            }
    
    def refund_payment(self, transaction_id, amount=None):
        """Refund Stripe payment."""
        if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
            return {
                'success': False,
                'error': 'Stripe is not configured.'
            }
        
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            refund_params = {'payment_intent': transaction_id}
            if amount:
                refund_params['amount'] = int(float(amount) * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': Decimal(refund.amount) / 100,
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Stripe refund error: {str(e)}'
            }


class PayPalPaymentService(PaymentService):
    """PayPal payment service."""
    
    def __init__(self):
        super().__init__()
        self.gateway_name = 'paypal'
        # API credentials will be loaded from settings
        # self.client_id = settings.PAYPAL_CLIENT_ID
        # self.client_secret = settings.PAYPAL_CLIENT_SECRET
        # self.mode = settings.PAYPAL_MODE  # 'sandbox' or 'live'
    
    def get_access_token(self):
        """Get PayPal OAuth access token."""
        if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not settings.PAYPAL_CLIENT_ID:
            return None
        
        try:
            import requests
            
            mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
            base_url = 'https://api.sandbox.paypal.com' if mode == 'sandbox' else 'https://api.paypal.com'
            
            auth_url = f'{base_url}/v1/oauth2/token'
            auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
            headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(auth_url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            return response.json().get('access_token')
        except Exception as e:
            return None
    
    def create_payment(self, amount, customer_email, customer_name, description, metadata=None):
        """
        Create PayPal order.
        
        Note: Requires PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in settings.
        """
        if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not settings.PAYPAL_CLIENT_ID:
            return {
                'success': False,
                'error': 'PayPal is not configured. Please add PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET to settings.'
            }
        
        try:
            import requests
            
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to authenticate with PayPal.'
                }
            
            mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
            base_url = 'https://api.sandbox.paypal.com' if mode == 'sandbox' else 'https://api.paypal.com'
            
            # Create order
            order_url = f'{base_url}/v2/checkout/orders'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            order_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': 'GBP',
                        'value': str(amount)
                    },
                    'description': description,
                }],
                'application_context': {
                    'brand_name': getattr(settings, 'PAYPAL_BRAND_NAME', 'Booking System'),
                    'landing_page': 'BILLING',
                    'user_action': 'PAY_NOW',
                    'return_url': settings.PAYPAL_RETURN_URL,
                    'cancel_url': settings.PAYPAL_CANCEL_URL,
                }
            }
            
            response = requests.post(order_url, json=order_data, headers=headers)
            response.raise_for_status()
            
            order = response.json()
            
            # Find approval URL
            approval_url = None
            for link in order.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            return {
                'success': True,
                'payment_id': order['id'],
                'redirect_url': approval_url,
            }
        except ImportError:
            return {
                'success': False,
                'error': 'Requests library not installed. Install with: pip install requests'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'PayPal error: {str(e)}'
            }
    
    def process_payment(self, payment_id, payment_data=None):
        """Capture PayPal order."""
        if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not settings.PAYPAL_CLIENT_ID:
            return {
                'success': False,
                'error': 'PayPal is not configured.'
            }
        
        try:
            import requests
            
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to authenticate with PayPal.'
                }
            
            mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
            base_url = 'https://api.sandbox.paypal.com' if mode == 'sandbox' else 'https://api.paypal.com'
            
            # Capture order
            capture_url = f'{base_url}/v2/checkout/orders/{payment_id}/capture'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.post(capture_url, headers=headers)
            response.raise_for_status()
            
            capture = response.json()
            
            if capture.get('status') == 'COMPLETED':
                # Get transaction ID from capture
                transaction_id = None
                for purchase_unit in capture.get('purchase_units', []):
                    for capture_data in purchase_unit.get('payments', {}).get('captures', []):
                        transaction_id = capture_data.get('id')
                        break
                
                return {
                    'success': True,
                    'status': 'completed',
                    'transaction_id': transaction_id or payment_id,
                }
            else:
                return {
                    'success': False,
                    'status': capture.get('status', 'unknown'),
                    'error': f'PayPal order status: {capture.get("status")}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'PayPal error: {str(e)}'
            }
    
    def refund_payment(self, transaction_id, amount=None):
        """Refund PayPal payment."""
        if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not settings.PAYPAL_CLIENT_ID:
            return {
                'success': False,
                'error': 'PayPal is not configured.'
            }
        
        try:
            import requests
            
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to authenticate with PayPal.'
                }
            
            mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')
            base_url = 'https://api.sandbox.paypal.com' if mode == 'sandbox' else 'https://api.paypal.com'
            
            # Create refund
            refund_url = f'{base_url}/v2/payments/captures/{transaction_id}/refund'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            refund_data = {}
            if amount:
                refund_data['amount'] = {
                    'value': str(amount),
                    'currency_code': 'GBP'
                }
            
            response = requests.post(refund_url, json=refund_data, headers=headers)
            response.raise_for_status()
            
            refund = response.json()
            
            return {
                'success': True,
                'refund_id': refund.get('id'),
                'amount': Decimal(refund.get('amount', {}).get('value', 0)),
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'PayPal refund error: {str(e)}'
            }


class LocalPaymentService(PaymentService):
    """Local payment service (Pay on Site)."""
    
    def __init__(self):
        super().__init__()
        self.gateway_name = 'local'
    
    def create_payment(self, amount, customer_email, customer_name, description, metadata=None):
        """Create local payment record (no gateway processing)."""
        return {
            'success': True,
            'payment_id': None,
            'redirect_url': None,
        }
    
    def process_payment(self, payment_id, payment_data=None):
        """Local payments are marked as pending (to be completed manually)."""
        return {
            'success': True,
            'status': 'pending',
            'transaction_id': None,
        }
    
    def refund_payment(self, transaction_id, amount=None):
        """Local payments cannot be refunded through gateway."""
        return {
            'success': False,
            'error': 'Local payments cannot be refunded through gateway.'
        }


def get_payment_service(payment_type):
    """
    Get payment service instance for the given payment type.
    
    Args:
        payment_type: Payment type ('stripe', 'paypal', 'local', etc.)
    
    Returns:
        PaymentService instance
    """
    services = {
        Payment.TYPE_STRIPE: StripePaymentService,
        Payment.TYPE_PAYPAL: PayPalPaymentService,
        Payment.TYPE_LOCAL: LocalPaymentService,
    }
    
    service_class = services.get(payment_type)
    if service_class:
        return service_class()
    else:
        return LocalPaymentService()  # Default to local payment

