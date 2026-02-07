# Backend Authentication Fixes

## Issues Fixed

### 1. Registration Serializer ✅
- **Problem:** Serializer expected `first_name`/`last_name` separately, but frontend sends `name`
- **Solution:** 
  - Added `name` field to serializer (accepts full name)
  - Automatically splits `name` into `first_name` and `last_name`
  - Added `phone` field support
  - Made `username` optional (auto-generated from email)
  - Made `password_confirm` optional
  - Added role validation (supports all roles: customer, staff, manager, admin)

### 2. Login Endpoint ✅
- **Status:** Endpoint exists and is correctly configured
- **Path:** `POST /api/aut/login/`
- **Features:**
  - Accepts email and password
  - Returns specific error codes:
    - `EMAIL_NOT_FOUND` (404) - Email doesn't exist
    - `INVALID_CREDENTIALS` (401) - Wrong password
    - `ACCOUNT_DISABLED` (403) - Account is disabled
  - Returns JWT tokens and user data on success

### 3. Registration Endpoint ✅
- **Status:** Endpoint exists and is correctly configured
- **Path:** `POST /api/aut/register/`
- **Features:**
  - Accepts `name`, `email`, `password`, `phone`, `role`
  - Auto-generates username from email
  - Creates Profile if phone is provided
  - Supports all roles (customer, staff, manager, admin)
  - Returns JWT tokens and user data on success

## Endpoint Details

### Login: `POST /api/aut/login/`
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "customer",
      "first_name": "John",
      "last_name": "Doe",
      ...
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  },
  "meta": {
    "message": "Login successful"
  }
}
```

**Response (Email Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_NOT_FOUND",
    "message": "Email not found. Please register to create an account."
  }
}
```

**Response (Invalid Password):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

### Register: `POST /api/aut/register/`
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "phone": "+1234567890",
  "role": "customer"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "customer",
      "first_name": "John",
      "last_name": "Doe",
      ...
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  },
  "meta": {
    "message": "User registered successfully"
  }
}
```

## Troubleshooting

### If you see 404 on `/api/aut/login/`:
1. **Check if backend server is running:**
   ```bash
   cd backend
   .\venv\Scripts\python.exe manage.py runserver
   ```

2. **Verify the endpoint is accessible:**
   - Open browser: http://localhost:8000/api/aut/login/
   - Should show method not allowed (405) for GET, but endpoint exists
   - Or use Postman/curl to test POST request

3. **Check CORS settings:**
   - Make sure `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
   - Check `CORS_ALLOW_CREDENTIALS = True` in settings

### If you see 400 on `/api/aut/register/`:
1. **Check request format:**
   - Must send JSON with `Content-Type: application/json`
   - Required fields: `email`, `password`
   - Optional fields: `name`, `phone`, `role`, `password_confirm`

2. **Check validation errors:**
   - Password must meet Django's password validation rules
   - Email must be unique
   - Role must be one of: customer, staff, manager, admin

## Files Modified

1. `backend/apps/accounts/serializers.py`
   - Updated `UserCreateSerializer` to accept `name` and `phone`
   - Added automatic username generation
   - Added role validation
   - Made fields optional where appropriate

2. `frontend/hooks/use-auth.ts`
   - Updated to send `name` instead of splitting to `first_name`/`last_name`

## Testing

To test the endpoints:

1. **Start backend server:**
   ```bash
   cd backend
   .\venv\Scripts\python.exe manage.py runserver
   ```

2. **Test login:**
   ```bash
   curl -X POST http://localhost:8000/api/aut/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"testpass123"}'
   ```

3. **Test register:**
   ```bash
   curl -X POST http://localhost:8000/api/aut/register/ \
     -H "Content-Type: application/json" \
     -d '{"email":"newuser@test.com","password":"testpass123","name":"New User","role":"customer"}'
   ```

## Notes

- All endpoints support all roles (customer, staff, manager, admin)
- Username is auto-generated from email if not provided
- Profile is automatically created if phone is provided
- JWT tokens are returned on successful login/registration
- Frontend automatically stores tokens in localStorage
