"""
Accounts app views.
Authentication views (register, login, logout, token refresh).
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore[import-untyped]
from rest_framework_simplejwt.views import TokenObtainPairView  # type: ignore[import-untyped]
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, ProfileSerializer, ManagerSerializer
from .models import Profile
from apps.core.permissions import IsAdmin, IsAdminOrManager

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint (public).
    POST /api/aut/register/
    """
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
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
                'message': 'User registered successfully',
            }
        }, status=status.HTTP_201_CREATED)


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
        
        # Authenticate user (Django User model uses username by default, but we're using email)
        user = None
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                user = authenticate(username=user.username, password=password)
        except User.DoesNotExist:
            pass
        
        if user is None:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password',
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
            return Response({
                'success': True,
                'data': {},
                'meta': {
                    'message': 'Logout successful',
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Refresh token is required',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid refresh token',
            }
        }, status=status.HTTP_400_BAD_REQUEST)


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
    
    email_exists = User.objects.filter(email=email).exists()
    
    return Response({
        'success': True,
        'data': {
            'email': email,
            'exists': email_exists,
            'suggestion': 'Login to link your order/subscription to your account' if email_exists else 'Register to create an account and link your order/subscription'
        },
        'meta': {}
    }, status=status.HTTP_200_OK)
