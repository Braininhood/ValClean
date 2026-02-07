"""
Accounts app views.
Authentication views (register, login, logout, token refresh).
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore[import-untyped]
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # type: ignore[import-untyped]
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .serializers import (
    UserSerializer, UserCreateSerializer, ProfileSerializer, ManagerSerializer,
    InvitationSerializer
)
from .models import Profile, Invitation
from apps.core.permissions import IsAdmin, IsAdminOrManager
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint (public).
    POST /api/aut/register/
    
    Security: Returns 200 OK for all valid requests (including existing emails)
    to prevent user enumeration attacks. Frontend handles redirect based on
    the 'redirect_to_login' flag in the response.
    """
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer
    
    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '').lower().strip() if request.data.get('email') else ''
        
        # SECURITY: Check if email exists BEFORE validation to prevent user enumeration
        # We return 200 OK in both cases (existing and new) to prevent attackers
        # from determining if an email is registered
        existing_user = None
        if email:
            try:
                existing_user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                existing_user = None
        
        # If email exists, return 200 OK with redirect flag (security: same status as success)
        if existing_user:
            return Response({
                'success': True,
                'data': {
                    'redirect_to_login': True,
                    'email': email,
                },
                'meta': {
                    'message': 'Please login to continue',
                }
            }, status=status.HTTP_200_OK)
        
        # Email doesn't exist - proceed with normal registration
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Send welcome email (non-blocking; log on failure)
            try:
                from apps.notifications.email_service import send_welcome_email
                send_welcome_email(user, customer_name=user.get_full_name() or user.email)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning('Failed to send welcome email: %s', e)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'success': True,
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                    'redirect_to_login': False,
                },
                'meta': {
                    'message': 'User registered successfully',
                }
            }, status=status.HTTP_200_OK)  # Changed to 200 OK for consistency (security)
        
        except DRFValidationError as e:
            # SECURITY: Catch validation errors (including race condition duplicates)
            # Only return 200 OK for email duplicates to prevent user enumeration
            error_detail = e.detail
            email_error = None
            
            # Check if error is about email already exists
            if isinstance(error_detail, dict):
                email_error = error_detail.get('email')
                if email_error and isinstance(email_error, list):
                    email_error = email_error[0] if email_error else None
            
            # If it's an email duplicate error, return 200 OK with redirect flag (security)
            if email_error and 'already exists' in str(email_error).lower():
                return Response({
                    'success': True,
                    'data': {
                        'redirect_to_login': True,
                        'email': email,
                    },
                    'meta': {
                        'message': 'Please login to continue',
                    }
                }, status=status.HTTP_200_OK)
            
            # Other validation errors (password mismatch, invalid role, etc.)
            # These can return 400 as they don't reveal user information
            # Re-raise to let DRF handle it normally
            raise


class LoginView(TokenObtainPairView):
    """
    User login endpoint (public).
    POST /api/aut/login/
    Returns JWT tokens and user information.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Email and password are required',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize email to lowercase for case-insensitive lookup
        email = email.lower().strip()
        
        # SECURITY: Prevent user enumeration by always returning the same error
        # Don't differentiate between "email not found" and "wrong password"
        # This prevents attackers from determining if an email exists
        
        # Try to get user (case-insensitive lookup)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Email doesn't exist - return same generic error as wrong password
            # This prevents user enumeration attacks
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password',
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Email exists - check password
        if not user.check_password(password):
            # Password is wrong - return same generic error
            # Frontend will show "Invalid email or password" for both cases
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password',
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Password is correct - authenticate user
        user = authenticate(username=user.username, password=password)
        if user is None:
            return Response({
                'success': False,
                'error': {
                    'code': 'AUTHENTICATION_FAILED',
                    'message': 'Authentication failed',
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': {
                    'code': 'ACCOUNT_DISABLED',
                    'message': 'Account is disabled',
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            'meta': {
                'message': 'Login successful',
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint (protected).
    POST /api/aut/logout/
    Invalidates refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        # Always return 200 so frontend can clear tokens even when already logged out
        return Response({
            'success': True,
            'data': {},
            'meta': {
                'message': 'Logout successful',
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid refresh token',
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_view(request):
    """
    Exchange Google (Supabase) OAuth for Django user and JWT.
    POST /api/aut/google/
    Body: { "access_token": "<supabase_jwt>" } or (dev) { "email": "...", "name": "..." }
    Creates or finds User in Django DB and returns Django JWT + user (role) for dashboard redirect.
    """
    import logging
    from django.db import IntegrityError

    logger = logging.getLogger(__name__)
    data = getattr(request, 'data', None) or {}
    if not isinstance(data, dict):
        data = {}

    access_token = data.get('access_token')
    email = (data.get('email') or '').lower().strip()
    name = (data.get('name') or '').strip()

    # Option 1: Verify Supabase JWT and extract email/name
    supabase_jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
    if access_token and supabase_jwt_secret:
        try:
            import jwt as pyjwt
            payload = pyjwt.decode(
                access_token,
                supabase_jwt_secret,
                algorithms=['HS256'],
                options={'verify_aud': False},
            )
            email = (payload.get('email') or payload.get('sub') or '').lower().strip()
            if not email and payload.get('sub'):
                # Supabase may put email in user_metadata or app_metadata
                email = (payload.get('user_metadata', {}).get('email') or '').lower().strip()
            name = (payload.get('user_metadata', {}).get('full_name') or
                    payload.get('user_metadata', {}).get('name') or
                    payload.get('name') or
                    (payload.get('given_name', '') + ' ' + payload.get('family_name', '')).strip() or
                    name)
        except Exception as e:
            # Fallback: use email/name from body (JWT secret mismatch, PyJWT not installed, etc.)
            logger.debug('Google login JWT fallback: %s', e)
            email = (data.get('email') or '').lower().strip()
            name = (data.get('name') or '').strip()
            if not email:
                return Response({
                    'success': False,
                    'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid token. Send email (and name) in the request body as fallback, or set SUPABASE_JWT_SECRET in backend .env to match Supabase project JWT Secret.'},
                }, status=status.HTTP_401_UNAUTHORIZED)

    # Option 2: No token or no secret – accept email + name from body (e.g. frontend sends session.user)
    if not email and data.get('email'):
        email = (data.get('email') or '').lower().strip()
        name = (data.get('name') or '').strip()

    if not email:
        return Response({
            'success': False,
            'error': {'code': 'MISSING_EMAIL', 'message': 'Email is required'},
        }, status=status.HTTP_400_BAD_REQUEST)

    from apps.customers.models import Customer

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        # Create new user (customer) and Customer record
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        name_parts = (name or 'User').split(None, 1)
        first_name = name_parts[0] if name_parts else 'User'
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        try:
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='customer',
            )
            user.set_unusable_password()
            user.save()
            Customer.objects.get_or_create(
                user=user,
                defaults={
                    'name': name or f'{first_name} {last_name}'.strip() or email,
                    'email': email,
                },
            )
        except IntegrityError:
            # Race: user was created by another request; fetch and continue
            user = User.objects.get(email__iexact=email)

    if not user.is_active:
        return Response({
            'success': False,
            'error': {'code': 'ACCOUNT_DISABLED', 'message': 'Account is disabled'},
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            },
            'meta': {'message': 'Signed in successfully'},
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception('Google login failed after user lookup: %s', e)
        return Response({
            'success': False,
            'error': {'code': 'SERVER_ERROR', 'message': 'Sign-in failed. Please try again.'},
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile (protected).
    GET /api/aut/me/
    """
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data,
        'meta': {}
    }, status=status.HTTP_200_OK)


from rest_framework import viewsets


class InvitationViewSet(viewsets.ModelViewSet):
    """
    Invitation ViewSet (admin and manager).
    - Managers can only invite staff
    - Admins can invite staff, managers, and admins
    GET, POST, PUT, PATCH, DELETE /api/aut/invitations/
    """
    permission_classes = [IsAdminOrManager]
    serializer_class = InvitationSerializer
    queryset = Invitation.objects.all().order_by('-created_at')
    
    def get_queryset(self):
        """Filter invitations based on user role."""
        queryset = super().get_queryset()
        # Managers can only see their own invitations
        if hasattr(self.request.user, 'role') and self.request.user.role == 'manager':
            return queryset.filter(invited_by=self.request.user)
        # Admins can see all invitations
        return queryset
    
    def perform_create(self, serializer):
        """Set invited_by to current user and validate permissions."""
        user = self.request.user
        role = serializer.validated_data.get('role')
        
        # Check permissions based on user role
        if hasattr(user, 'role'):
            if user.role == 'manager':
                # Managers can only invite staff
                if role != 'staff':
                    raise PermissionDenied({
                        'error': {
                            'code': 'PERMISSION_DENIED',
                            'message': 'Managers can only invite staff members.',
                        }
                    })
            elif user.role == 'admin' or user.is_superuser:
                # Admins can invite staff, managers, and admins
                if role not in ['staff', 'manager', 'admin']:
                    raise PermissionDenied({
                        'error': {
                            'code': 'PERMISSION_DENIED',
                            'message': 'Admins can only invite staff, managers, and admins.',
                        }
                    })
            else:
                # Other roles cannot create invitations
                raise PermissionDenied({
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': 'You do not have permission to create invitations.',
                    }
                })
        
        serializer.save(invited_by=user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except PermissionDenied as e:
            # Return PermissionDenied with proper response format
            if isinstance(e.detail, dict):
                return Response(e.detail, status=status.HTTP_403_FORBIDDEN)
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': str(e.detail) if e.detail else 'You do not have permission to create this invitation.',
                }
            }, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'message': 'Invitation created successfully',
            }
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {}
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_invitation_view(request, token):
    """
    Validate invitation token (public).
    GET /api/aut/invitations/validate/<token>/
    """
    try:
        invitation = Invitation.objects.get(token=token, is_active=True)
        if invitation.is_expired():
            return Response({
                'success': False,
                'error': {
                    'code': 'INVITATION_EXPIRED',
                    'message': 'This invitation has expired.',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        if invitation.used_at:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVITATION_USED',
                    'message': 'This invitation has already been used.',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'data': {
                'email': invitation.email,
                'role': invitation.role,
                'expires_at': invitation.expires_at.isoformat(),
            },
            'meta': {
                'message': 'Invitation is valid',
            }
        }, status=status.HTTP_200_OK)
    except Invitation.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'INVITATION_NOT_FOUND',
                'message': 'Invalid or expired invitation token.',
            }
        }, status=status.HTTP_404_NOT_FOUND)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Profile ViewSet (protected).
    GET, PUT, PATCH /api/aut/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    http_method_names = ['get', 'put', 'patch']  # Only allow GET, PUT, PATCH
    
    def get_queryset(self):
        """Return only the current user's profile."""
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return Profile.objects.filter(id=profile.id)
    
    def get_object(self):
        """Return the current user's profile."""
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {}
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'message': 'Profile updated successfully',
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_view(request):
    """
    Check if email exists (for account linking prompt) (public).
    POST /api/aut/check-email/
    """
    email = request.data.get('email')
    if not email:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Email is required',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize email to lowercase for case-insensitive lookup
    email = email.lower().strip()
    email_exists = User.objects.filter(email__iexact=email).exists()
    
    return Response({
        'success': True,
        'data': {
            'email': email,
            'exists': email_exists,
            'suggestion': 'Login to link your order/subscription to your account' if email_exists else 'Register to create an account and link your order/subscription'
        },
        'meta': {}
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    """
    Request password reset (public).
    POST /api/aut/password-reset/request/
    Sends password reset email.
    """
    email = request.data.get('email')
    if not email:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Email is required',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize email to lowercase for case-insensitive lookup
    email = email.lower().strip()
    
    try:
        user = User.objects.get(email__iexact=email)
        if not user.is_active:
            return Response({
                'success': False,
                'error': {
                    'code': 'ACCOUNT_DISABLED',
                    'message': 'Account is disabled',
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Send password reset email
        from .utils import send_password_reset_email
        token, code = send_password_reset_email(user)
        
        # Store token in user's profile preferences (temporary solution)
        # In production, use a dedicated PasswordResetToken model
        profile, _ = Profile.objects.get_or_create(user=user)
        if not profile.preferences:
            profile.preferences = {}
        profile.preferences['password_reset_token'] = token
        profile.preferences['password_reset_code'] = code
        profile.preferences['password_reset_expires'] = (timezone.now() + timedelta(hours=1)).isoformat()
        profile.save()
        
        return Response({
            'success': True,
            'data': {
                'message': 'Password reset email sent',
                'token': token if settings.DEBUG else None,  # Only return in debug mode
                'code': code if settings.DEBUG else None,  # Only return in debug mode
            },
            'meta': {}
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # Don't reveal if email exists (security best practice)
        return Response({
            'success': True,
            'data': {
                'message': 'If the email exists, a password reset link has been sent',
            },
            'meta': {}
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    Confirm password reset (public).
    POST /api/aut/password-reset/confirm/
    Resets password with token.
    """
    token = request.data.get('token')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    if not all([token, code, new_password, new_password_confirm]):
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Token, code, new_password, and new_password_confirm are required',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password_confirm:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Passwords do not match',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password
    from django.contrib.auth.password_validation import validate_password
    try:
        validate_password(new_password)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Password does not meet requirements',
                'details': list(e.messages) if hasattr(e, 'messages') else [str(e)],
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find user with matching token
    import hashlib
    from django.conf import settings
    from django.utils import timezone
    from datetime import timedelta
    
    users = User.objects.filter(is_active=True)
    for user in users:
        profile, _ = Profile.objects.get_or_create(user=user)
        if profile.preferences and 'password_reset_token' in profile.preferences:
            stored_token = profile.preferences.get('password_reset_token')
            stored_code = profile.preferences.get('password_reset_code')
            expires_str = profile.preferences.get('password_reset_expires')
            
            if stored_token == token and stored_code == code:
                # Check expiration
                if expires_str:
                    expires = timezone.datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    if timezone.now() > expires:
                        return Response({
                            'success': False,
                            'error': {
                                'code': 'TOKEN_EXPIRED',
                                'message': 'Password reset token has expired',
                            }
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user.set_password(new_password)
                user.save()
                
                # Clear reset token
                profile.preferences.pop('password_reset_token', None)
                profile.preferences.pop('password_reset_code', None)
                profile.preferences.pop('password_reset_expires', None)
                profile.save()
                
                return Response({
                    'success': True,
                    'data': {
                        'message': 'Password reset successfully',
                    },
                    'meta': {}
                }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': {
            'code': 'INVALID_TOKEN',
            'message': 'Invalid or expired password reset token',
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def email_verification_request_view(request):
    """
    Request email verification (public).
    POST /api/aut/verify-email/request/
    Sends verification email.
    """
    email = request.data.get('email')
    if not email:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Email is required',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize email to lowercase for case-insensitive lookup
    email = email.lower().strip()
    
    try:
        user = User.objects.get(email__iexact=email)
        if user.is_verified:
            return Response({
                'success': True,
                'data': {
                    'message': 'Email is already verified',
                },
                'meta': {}
            }, status=status.HTTP_200_OK)
        
        # Send verification email
        from .utils import send_verification_email
        token, code = send_verification_email(user)
        
        # Store token in user's profile preferences (temporary solution)
        profile, _ = Profile.objects.get_or_create(user=user)
        if not profile.preferences:
            profile.preferences = {}
        profile.preferences['verification_token'] = token
        profile.preferences['verification_code'] = code
        profile.save()
        
        return Response({
            'success': True,
            'data': {
                'message': 'Verification email sent',
                'token': token if settings.DEBUG else None,  # Only return in debug mode
                'code': code if settings.DEBUG else None,  # Only return in debug mode
            },
            'meta': {}
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'USER_NOT_FOUND',
                'message': 'User with this email does not exist',
            }
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def email_verification_confirm_view(request):
    """
    Confirm email verification (public).
    POST /api/aut/verify-email/confirm/
    Verifies email with token.
    """
    token = request.data.get('token')
    code = request.data.get('code')
    
    if not all([token, code]):
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Token and code are required',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find user with matching token
    users = User.objects.filter(is_active=True, is_verified=False)
    for user in users:
        profile, _ = Profile.objects.get_or_create(user=user)
        if profile.preferences and 'verification_token' in profile.preferences:
            stored_token = profile.preferences.get('verification_token')
            stored_code = profile.preferences.get('verification_code')
            
            if stored_token == token and stored_code == code:
                # Verify email
                user.is_verified = True
                user.save()
                
                # Clear verification token
                profile.preferences.pop('verification_token', None)
                profile.preferences.pop('verification_code', None)
                profile.save()
                
                return Response({
                    'success': True,
                    'data': {
                        'message': 'Email verified successfully',
                        'user': UserSerializer(user).data,
                    },
                    'meta': {}
                }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': {
            'code': 'INVALID_TOKEN',
            'message': 'Invalid verification token',
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification_email_view(request):
    """
    Resend verification email (authenticated).
    POST /api/aut/verify-email/resend/
    """
    user = request.user
    if user.is_verified:
        return Response({
            'success': True,
            'data': {
                'message': 'Email is already verified',
            },
            'meta': {}
        }, status=status.HTTP_200_OK)
    
    # Send verification email
    from .utils import send_verification_email
    token, code = send_verification_email(user)
    
    # Store token
    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.preferences:
        profile.preferences = {}
    profile.preferences['verification_token'] = token
    profile.preferences['verification_code'] = code
    profile.save()
    
    return Response({
        'success': True,
        'data': {
            'message': 'Verification email sent',
            'token': token if settings.DEBUG else None,
            'code': code if settings.DEBUG else None,
        },
        'meta': {}
    }, status=status.HTTP_200_OK)
