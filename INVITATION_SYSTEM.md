# Invitation System Documentation

## Overview

The invitation system ensures that only invited users can register for staff, manager, or admin roles. Customers can register publicly without an invitation.

## How It Works

### For Customers
- **Public Registration**: Customers can register at `/register` without any invitation token
- **No Token Required**: The registration endpoint accepts `role: 'customer'` without validation

### For Staff/Managers/Admins
- **Invitation Required**: Staff, managers, and admins must have a valid invitation token to register
- **Invitation Links**: Admins generate invitation links with unique tokens
- **Token Validation**: The registration endpoint validates the invitation token before creating the account

## Backend Implementation

### Models

#### Invitation Model
```python
class Invitation(TimeStampedModel):
    email = models.EmailField()
    role = models.CharField(choices=['staff', 'manager', 'admin'])
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(User)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

### API Endpoints

#### Public Endpoints

**Validate Invitation Token**
```
GET /api/aut/invitations/validate/<token>/
```
Returns invitation details if valid:
```json
{
  "success": true,
  "data": {
    "email": "staff@example.com",
    "role": "staff",
    "expires_at": "2026-01-18T12:00:00Z"
  }
}
```

**Register User** (with invitation token for non-customers)
```
POST /api/aut/register/
{
  "email": "staff@example.com",
  "password": "securepassword",
  "name": "Staff Member",
  "phone": "+441234567890",
  "role": "staff",
  "invitation_token": "abc123..."  // Required for staff/manager/admin
}
```

#### Admin Endpoints (Protected)

**List Invitations**
```
GET /api/aut/invitations/
```
Requires admin authentication.

**Create Invitation**
```
POST /api/aut/invitations/
{
  "email": "newstaff@example.com",
  "role": "staff",
  "expires_at": "2026-01-18T12:00:00Z"  // Optional, defaults to 7 days
}
```
Requires admin authentication. Returns invitation with token and invitation link.

**Get Invitation Details**
```
GET /api/aut/invitations/<id>/
```
Requires admin authentication.

**Update Invitation**
```
PUT/PATCH /api/aut/invitations/<id>/
{
  "is_active": false  // Deactivate invitation
}
```
Requires admin authentication.

**Delete Invitation**
```
DELETE /api/aut/invitations/<id>/
```
Requires admin authentication.

### Registration Flow

1. **Customer Registration**:
   - User fills out form at `/register`
   - Submits with `role: 'customer'`
   - No invitation token required
   - Account created immediately

2. **Staff/Manager/Admin Registration**:
   - Admin creates invitation via `/api/aut/invitations/`
   - Invitation link generated: `/{role_prefix}/register?token={token}&email={email}`
   - User clicks link and sees registration form
   - Form validates token via `/api/aut/invitations/validate/<token>/`
   - If valid, user fills out form with email pre-filled
   - Submits registration with `invitation_token`
   - Backend validates token:
     - Token exists and is active
     - Token is not expired
     - Token has not been used
     - Token matches the role
     - Token matches the email
   - If valid, account created and token marked as used
   - User redirected to role-specific dashboard

## Frontend Implementation

### Staff Registration (`/st/register`)

1. **Check for Invitation Token**:
   ```typescript
   const token = searchParams.get('token')
   if (!token) {
     // Show error: "Invitation token is required"
   }
   ```

2. **Validate Token**:
   ```typescript
   const invitationData = await apiClient.validateInvitation(token)
   // Pre-fill email from invitation
   // Show registration form
   ```

3. **Submit Registration**:
   ```typescript
   await register({
     email: invitationData.email,
     password: formData.password,
     name: formData.name,
     role: 'staff',
     invitation_token: token,  // Required!
   })
   ```

### Manager Registration (`/man/register`)
Same flow as staff, but with `role: 'manager'`.

### Admin Registration (`/ad/register`)
Same flow as staff, but with `role: 'admin'`.

## Admin Panel

Admins can manage invitations via Django admin:

1. **Create Invitation**:
   - Navigate to `/admin/accounts/invitation/`
   - Click "Add Invitation"
   - Enter email and role
   - Token is auto-generated
   - Expiration defaults to 7 days
   - Save to create invitation

2. **View Invitations**:
   - List view shows all invitations
   - Filter by role, status, expiration
   - Search by email or token

3. **Copy Invitation Link**:
   - Click on invitation to view details
   - Token is displayed
   - Use token to construct invitation link:
     - Staff: `http://localhost:3000/st/register?token={token}&email={email}`
     - Manager: `http://localhost:3000/man/register?token={token}&email={email}`
     - Admin: `http://localhost:3000/ad/register?token={token}&email={email}`

## Security Considerations

1. **Token Uniqueness**: Each invitation has a unique, cryptographically secure token
2. **Expiration**: Invitations expire after 7 days (configurable)
3. **One-Time Use**: Invitations can only be used once
4. **Email Matching**: Token email must match registration email
5. **Role Matching**: Token role must match registration role
6. **Admin-Only Creation**: Only admins can create invitations

## Example Workflow

1. **Admin invites new staff member**:
   - Admin goes to `/admin/accounts/invitation/add/`
   - Enters email: `newstaff@valclean.uk`
   - Selects role: `Staff`
   - Saves invitation
   - Copies invitation link: `http://localhost:3000/st/register?token=abc123...&email=newstaff@valclean.uk`

2. **Staff member receives invitation**:
   - Staff member clicks link
   - Sees registration form with email pre-filled
   - Fills out name, password, etc.
   - Submits form

3. **Registration succeeds**:
   - Backend validates token
   - Creates staff account
   - Marks invitation as used
   - Returns JWT tokens
   - Frontend redirects to `/st/dashboard`

## API Client Methods

```typescript
// Validate invitation token
const invitationData = await apiClient.validateInvitation(token)

// Register with invitation token
const response = await apiClient.register({
  email: invitationData.email,
  password: 'securepassword',
  name: 'Staff Member',
  role: 'staff',
  invitation_token: token,  // Required for non-customers
})
```
