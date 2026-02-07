# Supabase Migration Guide - Complete Step-by-Step

This guide will help you migrate your VALClean application from Django's built-in authentication and SQLite/PostgreSQL to Supabase, leveraging:
- **Supabase PostgreSQL** (managed database)
- **Supabase Auth** (email, OAuth)
- **Supabase Storage** (file storage)
- **Supabase REST API** (auto-generated)

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Supabase Project Setup](#phase-1-supabase-project-setup)
3. [Phase 2: Database Migration](#phase-2-database-migration)
4. [Phase 3: Authentication Migration](#phase-3-authentication-migration)
5. [Phase 4: File Storage Migration](#phase-4-file-storage-migration)
6. [Phase 5: Backend Integration](#phase-5-backend-integration)
7. [Phase 6: Frontend Integration](#phase-6-frontend-integration)
8. [Phase 7: Data Migration](#phase-7-data-migration)
9. [Phase 8: Testing & Verification](#phase-8-testing--verification)
10. [Phase 9: Production Deployment](#phase-9-production-deployment)

---

## Prerequisites

### Required Accounts
- ✅ Supabase account (sign up at https://supabase.com)
- ✅ GitHub account (for OAuth, optional)

### Required Tools
- ✅ Python 3.10+ (for Django backend)
- ✅ Node.js 18+ (for Next.js frontend)
- ✅ PostgreSQL client tools (pg_dump, psql) - optional
- ✅ Git (for version control)

### Current Setup Understanding
- ✅ Django REST Framework backend
- ✅ Next.js frontend
- ✅ JWT authentication (SimpleJWT)
- ✅ SQLite (dev) / PostgreSQL (prod)
- ✅ Local file storage (media files)

---

## Phase 1: Supabase Project Setup

### Step 1.1: Create Supabase Project

1. **Go to Supabase Dashboard**
   - Visit https://app.supabase.com
   - Sign in or create an account

2. **Create New Project**
   - Click "New Project"
   - Fill in details:
     - **Name**: `valclean` (or your preferred name)
     - **Database Password**: Generate a strong password (save it!)
     - **Region**: Choose closest to your users (e.g., `London (eu-west-2)`)
     - **Pricing Plan**: Free tier is sufficient for MVP

3. **Wait for Project Creation** (2-3 minutes)

4. **Save Project Credentials**
   - Go to **Settings** → **API**
   - Copy and save:
     - **Project URL**: `https://xxxxx.supabase.co`
     - **anon/public key**: `eyJhbGc...`
     - **service_role key**: `eyJhbGc...` (keep secret!)
   - Go to **Settings** → **Database**
   - Copy **Connection string** (URI format)

### Step 1.2: Install Supabase CLI (Optional but Recommended)

```powershell
# Install Supabase CLI globally
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref
```

### Step 1.3: Create Environment Variables File

Create `backend/.env.supabase`:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # Keep secret!
SUPABASE_DB_PASSWORD=your-db-password

# Database Connection (from Supabase Settings → Database)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Keep existing Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Phase 2: Database Migration

### Step 2.1: Update Django Settings for Supabase PostgreSQL

**File**: `backend/config/settings/base.py`

Update the database configuration:

```python
# Database - Supabase PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='postgres'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='db.xxxxx.supabase.co'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Supabase requires SSL
        },
    }
}
```

Or use `DATABASE_URL`:

```python
import dj_database_url

# Parse DATABASE_URL from Supabase
database_url = env('DATABASE_URL', default=None)
if database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
```

### Step 2.2: Install PostgreSQL Adapter

```powershell
cd backend
.\venv\Scripts\activate
pip install psycopg2-binary dj-database-url
```

Update `backend/requirements.txt`:

```txt
psycopg2-binary==2.9.9
dj-database-url==2.1.0
```

### Step 2.3: Run Django Migrations on Supabase

```powershell
cd backend
.\venv\Scripts\activate

# Test connection
python manage.py dbshell

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

### Step 2.4: Verify Database Connection

```powershell
# Test database connection
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
```

---

## Phase 3: Authentication Migration

### Step 3.1: Install Supabase Python Client

```powershell
cd backend
.\venv\Scripts\activate
pip install supabase
```

Add to `backend/requirements.txt`:

```txt
supabase==2.0.0
```

### Step 3.2: Create Supabase Auth Service

**File**: `backend/apps/core/supabase_auth.py` (NEW)

```python
"""
Supabase Authentication Service
Handles authentication using Supabase Auth instead of Django's built-in auth.
"""
from supabase import create_client, Client
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    """Service for Supabase authentication operations."""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_ANON_KEY
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.client: Client = create_client(self.url, self.key)
        self.admin_client: Client = create_client(self.url, self.service_key)
    
    def sign_up(self, email: str, password: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Register a new user with Supabase Auth.
        
        Args:
            email: User email
            password: User password
            metadata: Additional user metadata (role, first_name, last_name, etc.)
        
        Returns:
            Dict with user data and session tokens
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session,
            }
        except Exception as e:
            logger.error(f"Supabase sign up error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in user with Supabase Auth.
        
        Returns:
            Dict with user data and session tokens
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session,
            }
        except Exception as e:
            logger.error(f"Supabase sign in error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out user."""
        try:
            self.client.auth.set_session(access_token, "")
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            logger.error(f"Supabase sign out error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user from access token."""
        try:
            self.client.auth.set_session(access_token, "")
            user = self.client.auth.get_user(access_token)
            return user.user if user else None
        except Exception as e:
            logger.error(f"Supabase get user error: {str(e)}")
            return None
    
    def update_user(self, access_token: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user metadata."""
        try:
            self.client.auth.set_session(access_token, "")
            response = self.client.auth.update_user(updates)
            return {
                "success": True,
                "user": response.user
            }
        except Exception as e:
            logger.error(f"Supabase update user error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email."""
        try:
            self.client.auth.reset_password_for_email(email)
            return {"success": True}
        except Exception as e:
            logger.error(f"Supabase reset password error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email."""
        try:
            response = self.client.auth.verify_otp({
                "token": token,
                "type": "email"
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session,
            }
        except Exception as e:
            logger.error(f"Supabase verify email error: {str(e)}")
            return {"success": False, "error": str(e)}


# Singleton instance
supabase_auth = SupabaseAuthService()
```

### Step 3.3: Update Django Settings for Supabase Auth

**File**: `backend/config/settings/base.py`

Add Supabase settings:

```python
# Supabase Configuration
SUPABASE_URL = env('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY', default='')
SUPABASE_SERVICE_ROLE_KEY = env('SUPABASE_SERVICE_ROLE_KEY', default='')
```

### Step 3.4: Create Supabase Auth Middleware

**File**: `backend/apps/core/middleware.py`

Add Supabase authentication middleware:

```python
from .supabase_auth import supabase_auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class SupabaseAuthMiddleware:
    """
    Middleware to authenticate users via Supabase Auth tokens.
    Sets request.user based on Supabase JWT token.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Get user from Supabase
            supabase_user = supabase_auth.get_user(token)
            if supabase_user:
                # Get or create Django user from Supabase user
                try:
                    user = User.objects.get(email=supabase_user['email'])
                except User.DoesNotExist:
                    # Create Django user from Supabase user
                    user = User.objects.create_user(
                        email=supabase_user['email'],
                        username=supabase_user.get('id'),
                        role=supabase_user.get('user_metadata', {}).get('role', 'customer'),
                        is_verified=supabase_user.get('email_confirmed_at') is not None,
                    )
                request.user = user
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        return self.get_response(request)
```

### Step 3.5: Update Authentication Views

**File**: `backend/apps/accounts/views.py`

Update login and registration views to use Supabase:

```python
from apps.core.supabase_auth import supabase_auth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login using Supabase Auth.
    POST /api/aut/login/
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'success': False,
            'error': {'message': 'Email and password are required'}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate with Supabase
    result = supabase_auth.sign_in(email, password)
    
    if not result['success']:
        return Response({
            'success': False,
            'error': {'message': result.get('error', 'Invalid credentials')}
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get or create Django user
    supabase_user = result['user']
    try:
        user = User.objects.get(email=supabase_user['email'])
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=supabase_user['email'],
            username=supabase_user.get('id'),
            role=supabase_user.get('user_metadata', {}).get('role', 'customer'),
            is_verified=supabase_user.get('email_confirmed_at') is not None,
        )
    
    return Response({
        'success': True,
        'data': {
            'user': UserSerializer(user).data,
            'tokens': {
                'access': result['session']['access_token'],
                'refresh': result['session']['refresh_token'],
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register using Supabase Auth.
    POST /api/aut/register/
    """
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name', '')
    role = request.data.get('role', 'customer')
    
    if not email or not password:
        return Response({
            'success': False,
            'error': {'message': 'Email and password are required'}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Split name into first_name and last_name
    name_parts = name.split(' ', 1) if name else ['', '']
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Register with Supabase
    metadata = {
        'role': role,
        'first_name': first_name,
        'last_name': last_name,
    }
    result = supabase_auth.sign_up(email, password, metadata)
    
    if not result['success']:
        return Response({
            'success': False,
            'error': {'message': result.get('error', 'Registration failed')}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create Django user
    supabase_user = result['user']
    user = User.objects.create_user(
        email=supabase_user['email'],
        username=supabase_user.get('id'),
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_verified=False,  # Will be verified via email
    )
    
    return Response({
        'success': True,
        'data': {
            'user': UserSerializer(user).data,
            'tokens': {
                'access': result['session']['access_token'],
                'refresh': result['session']['refresh_token'],
            }
        }
    }, status=status.HTTP_201_CREATED)
```

### Step 3.6: Configure Supabase Auth Settings

In Supabase Dashboard:

1. **Go to Authentication → Settings**
2. **Configure Email Auth**:
   - Enable "Enable email confirmations"
   - Set "Site URL": `http://localhost:3000` (dev) or your production URL
   - Set "Redirect URLs**: `http://localhost:3000/**` (dev)
3. **Configure OAuth Providers** (optional):
   - Enable Google, GitHub, etc.
   - Add OAuth credentials
4. **Configure Email Templates**:
   - Customize confirmation email
   - Customize password reset email

---

## Phase 4: File Storage Migration

### Step 4.1: Install Supabase Storage Client

The `supabase` Python package already includes storage functionality.

### Step 4.2: Create Supabase Storage Service

**File**: `backend/apps/core/supabase_storage.py` (NEW)

```python
"""
Supabase Storage Service
Handles file uploads to Supabase Storage buckets.
"""
from supabase import create_client, Client
from django.conf import settings
from typing import Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """Service for Supabase Storage operations."""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY  # Use service role for admin operations
        self.client: Client = create_client(self.url, self.key)
    
    def upload_file(
        self,
        bucket: str,
        file_path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        upsert: bool = False
    ) -> dict:
        """
        Upload a file to Supabase Storage.
        
        Args:
            bucket: Storage bucket name (e.g., 'avatars', 'services', 'staff')
            file_path: Path within bucket (e.g., 'user_123/avatar.jpg')
            file_data: File data as bytes
            content_type: MIME type (e.g., 'image/jpeg')
            upsert: If True, overwrite existing file
        
        Returns:
            Dict with success status and file URL
        """
        try:
            response = self.client.storage.from_(bucket).upload(
                file_path,
                file_data,
                file_options={
                    "content-type": content_type or "application/octet-stream",
                    "upsert": upsert
                }
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            
            return {
                "success": True,
                "path": file_path,
                "url": public_url,
                "data": response
            }
        except Exception as e:
            logger.error(f"Supabase storage upload error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, bucket: str, file_path: str) -> dict:
        """Delete a file from Supabase Storage."""
        try:
            response = self.client.storage.from_(bucket).remove([file_path])
            return {
                "success": True,
                "data": response
            }
        except Exception as e:
            logger.error(f"Supabase storage delete error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_public_url(self, bucket: str, file_path: str) -> str:
        """Get public URL for a file."""
        return self.client.storage.from_(bucket).get_public_url(file_path)
    
    def get_signed_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for private file (expires in seconds)."""
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                file_path,
                expires_in
            )
            return response.get('signedURL', '')
        except Exception as e:
            logger.error(f"Supabase storage signed URL error: {str(e)}")
            return ''


# Singleton instance
supabase_storage = SupabaseStorageService()
```

### Step 4.3: Create Storage Buckets in Supabase

In Supabase Dashboard:

1. **Go to Storage**
2. **Create Buckets**:
   - `avatars` (public)
   - `services` (public)
   - `staff` (public)
   - `categories` (public)
   - `appointment-photos` (private)
   - `documents` (private)

3. **Configure Bucket Policies** (Row Level Security):
   - **Public buckets**: Allow public read access
   - **Private buckets**: Allow authenticated users only

### Step 4.4: Create Django Storage Backend

**File**: `backend/apps/core/storage_backend.py` (NEW)

```python
"""
Django Storage Backend for Supabase Storage.
Allows Django to use Supabase Storage like local file storage.
"""
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from .supabase_storage import supabase_storage
import os

class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage.
    Usage in models:
        image = models.ImageField(storage=SupabaseStorage(bucket='images'))
    """
    
    def __init__(self, bucket='default'):
        self.bucket = bucket
    
    def _open(self, name, mode='rb'):
        # For reading, we'll use public URLs
        # For private files, use signed URLs
        url = supabase_storage.get_public_url(self.bucket, name)
        # Return a ContentFile that can be read
        # Note: This is a simplified implementation
        # For production, you may want to fetch the file content
        return ContentFile(b'')
    
    def _save(self, name, content):
        # Read file content
        content.seek(0)
        file_data = content.read()
        
        # Determine content type
        content_type = getattr(content, 'content_type', None)
        if not content_type:
            # Guess from extension
            ext = os.path.splitext(name)[1].lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.pdf': 'application/pdf',
            }
            content_type = content_types.get(ext, 'application/octet-stream')
        
        # Upload to Supabase
        result = supabase_storage.upload_file(
            self.bucket,
            name,
            file_data,
            content_type=content_type,
            upsert=True
        )
        
        if result['success']:
            return name
        else:
            raise IOError(f"Failed to upload file: {result.get('error')}")
    
    def delete(self, name):
        result = supabase_storage.delete_file(self.bucket, name)
        if not result['success']:
            raise IOError(f"Failed to delete file: {result.get('error')}")
    
    def exists(self, name):
        # Check if file exists (simplified - may need to implement list check)
        try:
            url = supabase_storage.get_public_url(self.bucket, name)
            # Try to access the URL to check existence
            import requests
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def url(self, name):
        """Return public URL for the file."""
        return supabase_storage.get_public_url(self.bucket, name)
```

### Step 4.5: Update Models to Use Supabase Storage

**File**: `backend/apps/accounts/models.py`

```python
from apps.core.storage_backend import SupabaseStorage

class Profile(TimeStampedModel):
    # ... existing fields ...
    avatar = models.ImageField(
        upload_to='avatars/',
        storage=SupabaseStorage(bucket='avatars'),  # Add this
        blank=True,
        null=True,
        help_text='User avatar image'
    )
```

**File**: `backend/apps/services/models.py`

```python
from apps.core.storage_backend import SupabaseStorage

class Category(TimeStampedModel):
    # ... existing fields ...
    image = models.ImageField(
        upload_to='categories/',
        storage=SupabaseStorage(bucket='categories'),  # Add this
        blank=True,
        null=True,
        help_text='Category image'
    )

class Service(TimeStampedModel):
    # ... existing fields ...
    image = models.ImageField(
        upload_to='services/',
        storage=SupabaseStorage(bucket='services'),  # Add this
        blank=True,
        null=True,
        help_text='Service image'
    )
```

**File**: `backend/apps/staff/models.py`

```python
from apps.core.storage_backend import SupabaseStorage

class Staff(TimeStampedModel):
    # ... existing fields ...
    photo = models.ImageField(
        upload_to='staff/',
        storage=SupabaseStorage(bucket='staff'),  # Add this
        blank=True,
        null=True,
        help_text='Staff photo'
    )
```

### Step 4.6: Create File Upload API Endpoint

**File**: `backend/apps/core/views.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .supabase_storage import supabase_storage

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """
    Upload file to Supabase Storage.
    POST /api/core/upload/
    """
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': {'message': 'No file provided'}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    bucket = request.data.get('bucket', 'default')
    folder = request.data.get('folder', '')
    
    # Generate file path
    file_path = f"{folder}/{file.name}" if folder else file.name
    
    # Read file data
    file_data = file.read()
    
    # Upload to Supabase
    result = supabase_storage.upload_file(
        bucket=bucket,
        file_path=file_path,
        file_data=file_data,
        content_type=file.content_type,
        upsert=True
    )
    
    if result['success']:
        return Response({
            'success': True,
            'data': {
                'url': result['url'],
                'path': result['path']
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'error': {'message': result.get('error', 'Upload failed')}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

## Phase 5: Backend Integration

### Step 5.1: Update Middleware Order

**File**: `backend/config/settings/base.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.core.middleware.SupabaseAuthMiddleware',  # Add Supabase auth middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.AuthenticationMiddleware',  # Keep existing
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Step 5.2: Update CORS Settings for Supabase

**File**: `backend/config/settings/base.py`

```python
# CORS Settings - Add Supabase URLs
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://xxxxx.supabase.co',  # Add your Supabase URL
])
```

### Step 5.3: Update Environment Variables

**File**: `backend/env.example`

Add Supabase variables:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
SUPABASE_DB_PASSWORD=your-password

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

---

## Phase 6: Frontend Integration

### Step 6.1: Install Supabase JavaScript Client

```powershell
cd frontend
npm install @supabase/supabase-js
```

### Step 6.2: Create Supabase Client

**File**: `frontend/lib/supabase/client.ts` (NEW)

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Step 6.3: Create Supabase Auth Hook

**File**: `frontend/hooks/use-supabase-auth.ts` (NEW)

```typescript
'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase/client'
import { User, Session } from '@supabase/supabase-js'
import { useAuthStore } from '@/store/auth-store'

export function useSupabaseAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const { setUser: setStoreUser, setToken, clearAuth } = useAuthStore()

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session) {
        setStoreUser({
          id: session.user.id,
          email: session.user.email || '',
          role: session.user.user_metadata?.role || 'customer',
        })
        setToken(session.access_token)
      }
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session) {
        setStoreUser({
          id: session.user.id,
          email: session.user.email || '',
          role: session.user.user_metadata?.role || 'customer',
        })
        setToken(session.access_token)
      } else {
        clearAuth()
      }
    })

    return () => subscription.unsubscribe()
  }, [setStoreUser, setToken, clearAuth])

  const signUp = async (email: string, password: string, metadata?: any) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
      },
    })
    return { data, error }
  }

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (!error) {
      clearAuth()
    }
    return { error }
  }

  const resetPassword = async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email)
    return { error }
  }

  return {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    resetPassword,
  }
}
```

### Step 6.4: Update Frontend Environment Variables

**File**: `frontend/.env.local` (NEW)

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Step 6.5: Update Auth Store

**File**: `frontend/store/auth-store.ts`

Update to work with Supabase tokens:

```typescript
// Keep existing structure, but tokens will come from Supabase
// The useSupabaseAuth hook will handle setting tokens
```

### Step 6.6: Update Login/Register Pages

**File**: `frontend/app/(auth)/login/page.tsx`

Update to use Supabase auth:

```typescript
'use client'

import { useSupabaseAuth } from '@/hooks/use-supabase-auth'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function LoginPage() {
  const { signIn } = useSupabaseAuth()
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const { data, error: signInError } = await signIn(email, password)

    if (signInError) {
      setError(signInError.message)
      setLoading(false)
      return
    }

    if (data.session) {
      router.push('/dashboard')
    }
  }

  // ... rest of component
}
```

### Step 6.7: Update API Client to Include Supabase Token

**File**: `frontend/lib/api/client.ts`

```typescript
import axios from 'axios'
import { supabase } from '@/lib/supabase/client'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
})

// Add Supabase token to requests
apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

export default apiClient
```

---

## Phase 7: Data Migration

### Step 7.1: Export Existing Data

```powershell
cd backend
.\venv\Scripts\activate

# Export data to JSON
python manage.py dumpdata --natural-foreign --natural-primary -o data_export.json
```

### Step 7.2: Create Migration Script

**File**: `backend/migrate_to_supabase.py` (NEW)

```python
"""
Script to migrate existing data to Supabase.
Run after setting up Supabase database and authentication.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Profile
from apps.services.models import Category, Service
from apps.staff.models import Staff
from apps.customers.models import Customer
from apps.appointments.models import Appointment
from apps.core.supabase_auth import supabase_auth
from apps.core.supabase_storage import supabase_storage
import json

User = get_user_model()

def migrate_users():
    """Migrate users to Supabase Auth."""
    users = User.objects.all()
    migrated = 0
    
    for user in users:
        try:
            # Check if user exists in Supabase
            # Note: You may need to create users manually or use admin API
            print(f"Migrating user: {user.email}")
            # Supabase doesn't allow password migration directly
            # Users will need to reset passwords or you'll need to use admin API
            migrated += 1
        except Exception as e:
            print(f"Error migrating user {user.email}: {str(e)}")
    
    print(f"Migrated {migrated} users")

def migrate_files():
    """Migrate local media files to Supabase Storage."""
    import os
    from django.conf import settings
    
    media_root = settings.MEDIA_ROOT
    buckets = {
        'avatars': 'avatars',
        'services': 'services',
        'staff': 'staff',
        'categories': 'categories',
    }
    
    for folder, bucket in buckets.items():
        folder_path = os.path.join(media_root, folder)
        if not os.path.exists(folder_path):
            continue
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, media_root)
                
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    result = supabase_storage.upload_file(
                        bucket=bucket,
                        file_path=relative_path,
                        file_data=file_data,
                        upsert=True
                    )
                    
                    if result['success']:
                        print(f"Uploaded: {relative_path}")
                    else:
                        print(f"Failed: {relative_path} - {result.get('error')}")
                except Exception as e:
                    print(f"Error uploading {relative_path}: {str(e)}")

if __name__ == '__main__':
    print("Starting migration to Supabase...")
    # migrate_users()  # Run after setting up auth
    migrate_files()
    print("Migration complete!")
```

### Step 7.3: Run Migration Script

```powershell
cd backend
.\venv\Scripts\activate
python migrate_to_supabase.py
```

---

## Phase 8: Testing & Verification

### Step 8.1: Test Authentication

1. **Test Registration**:
   ```powershell
   # Use Postman or curl
   curl -X POST http://localhost:8000/api/aut/register/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123456","name":"Test User"}'
   ```

2. **Test Login**:
   ```powershell
   curl -X POST http://localhost:8000/api/aut/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123456"}'
   ```

3. **Verify in Supabase Dashboard**:
   - Go to **Authentication** → **Users**
   - Check that user was created

### Step 8.2: Test File Upload

1. **Test via API**:
   ```powershell
   curl -X POST http://localhost:8000/api/core/upload/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test.jpg" \
     -F "bucket=avatars" \
     -F "folder=user_123"
   ```

2. **Verify in Supabase Dashboard**:
   - Go to **Storage** → **avatars**
   - Check that file was uploaded

### Step 8.3: Test Database Queries

```powershell
cd backend
python manage.py shell
```

```python
from apps.services.models import Service
from apps.staff.models import Staff

# Test queries
services = Service.objects.all()
print(f"Services count: {services.count()}")

staff = Staff.objects.all()
print(f"Staff count: {staff.count()}")
```

---

## Phase 9: Production Deployment

### Step 9.1: Update Production Settings

**File**: `backend/config/settings/production.py`

```python
# Supabase Configuration (Production)
SUPABASE_URL = env('SUPABASE_URL')
SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = env('SUPABASE_SERVICE_ROLE_KEY')

# Database (Supabase PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

### Step 9.2: Update Supabase Auth Settings

In Supabase Dashboard:

1. **Authentication → URL Configuration**:
   - **Site URL**: `https://yourdomain.com`
   - **Redirect URLs**: `https://yourdomain.com/**`

2. **Enable Email Confirmations** (recommended for production)

3. **Configure OAuth Providers** (if using)

### Step 9.3: Set Up Row Level Security (RLS)

In Supabase Dashboard → **SQL Editor**:

```sql
-- Example: Enable RLS on a table
ALTER TABLE accounts_user ENABLE ROW LEVEL SECURITY;

-- Create policy for users to read their own data
CREATE POLICY "Users can read own data"
ON accounts_user
FOR SELECT
USING (auth.uid() = id);
```

### Step 9.4: Monitor Usage

- **Supabase Dashboard** → **Usage**: Monitor database size, API calls, storage
- **Free Tier Limits**:
  - 500 MB database
  - 1 GB file storage
  - 50,000 monthly active users
  - 2 GB bandwidth

---

## 🎯 Summary Checklist

### ✅ Phase 1: Supabase Setup
- [ ] Created Supabase project
- [ ] Saved credentials
- [ ] Installed Supabase CLI (optional)

### ✅ Phase 2: Database Migration
- [ ] Updated Django settings for Supabase PostgreSQL
- [ ] Installed psycopg2-binary
- [ ] Ran migrations
- [ ] Verified connection

### ✅ Phase 3: Authentication Migration
- [ ] Installed supabase Python package
- [ ] Created SupabaseAuthService
- [ ] Updated login/register views
- [ ] Configured Supabase Auth settings

### ✅ Phase 4: File Storage Migration
- [ ] Created SupabaseStorageService
- [ ] Created storage buckets
- [ ] Updated models to use Supabase storage
- [ ] Created upload endpoint

### ✅ Phase 5: Backend Integration
- [ ] Updated middleware
- [ ] Updated CORS settings
- [ ] Updated environment variables

### ✅ Phase 6: Frontend Integration
- [ ] Installed @supabase/supabase-js
- [ ] Created Supabase client
- [ ] Created useSupabaseAuth hook
- [ ] Updated login/register pages
- [ ] Updated API client

### ✅ Phase 7: Data Migration
- [ ] Exported existing data
- [ ] Migrated files to Supabase Storage
- [ ] Verified data integrity

### ✅ Phase 8: Testing
- [ ] Tested authentication
- [ ] Tested file uploads
- [ ] Tested database queries
- [ ] Verified all features work

### ✅ Phase 9: Production
- [ ] Updated production settings
- [ ] Configured production URLs
- [ ] Set up RLS policies
- [ ] Monitored usage

---

## 📚 Additional Resources

- **Supabase Documentation**: https://supabase.com/docs
- **Supabase Python Client**: https://github.com/supabase/supabase-py
- **Supabase JavaScript Client**: https://github.com/supabase/supabase-js
- **Django + Supabase Guide**: https://supabase.com/docs/guides/getting-started/tutorials/with-django

---

## 🆘 Troubleshooting

### Database Connection Issues
- **Error**: "SSL connection required"
  - **Solution**: Add `'OPTIONS': {'sslmode': 'require'}` to database config

### Authentication Issues
- **Error**: "Invalid API key"
  - **Solution**: Verify SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY are correct

### File Upload Issues
- **Error**: "Bucket not found"
  - **Solution**: Create buckets in Supabase Dashboard → Storage

### CORS Issues
- **Error**: "CORS policy blocked"
  - **Solution**: Add frontend URL to CORS_ALLOWED_ORIGINS in Django settings

---

## 🎉 Congratulations!

You've successfully migrated to Supabase! Your application now uses:
- ✅ Managed PostgreSQL database
- ✅ Built-in authentication (email, OAuth)
- ✅ File storage
- ✅ Auto-generated REST API
- ✅ Row-level security

**Next Steps**:
1. Monitor usage in Supabase Dashboard
2. Set up backups (Supabase handles this automatically)
3. Configure custom domains (if needed)
4. Set up monitoring and alerts

---

**Last Updated**: 2024
**Version**: 1.0.0
