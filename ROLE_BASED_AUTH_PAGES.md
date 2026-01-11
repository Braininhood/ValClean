# Role-Based Authentication Pages

## Overview

The application now has separate login and registration pages for each user role, ensuring users are directed to the correct dashboard based on their role.

---

## Login Pages

### Customer Login (`/login`)
- **Route:** `/login`
- **Allowed Role:** `customer` only
- **Redirect:** `/cus/dashboard`
- **Features:**
  - Validates that logged-in user is a customer
  - Shows error if wrong role attempts to login
  - Redirects to `/register?email=...` if email not found

### Staff Login (`/st/login`)
- **Route:** `/st/login`
- **Allowed Role:** `staff` only
- **Redirect:** `/st/dashboard`
- **Features:**
  - Validates that logged-in user is staff
  - Shows error if wrong role attempts to login
  - Redirects to `/st/register?email=...` if email not found

### Manager Login (`/man/login`)
- **Route:** `/man/login`
- **Allowed Roles:** `manager` or `admin`
- **Redirect:** `/man/dashboard` (manager) or `/ad/dashboard` (admin)
- **Features:**
  - Validates that logged-in user is manager or admin
  - Shows error if wrong role attempts to login
  - Redirects to `/man/register?email=...` if email not found

### Admin Login (`/ad/login`)
- **Route:** `/ad/login`
- **Allowed Role:** `admin` only
- **Redirect:** `/ad/dashboard`
- **Features:**
  - Validates that logged-in user is admin
  - Shows error if wrong role attempts to login
  - Redirects to `/ad/register?email=...` if email not found

---

## Registration Pages

### Customer Registration (`/register`)
- **Route:** `/register`
- **Allowed Role:** `customer` only
- **Redirect:** `/cus/dashboard`
- **Features:**
  - Creates customer account
  - Validates role after registration
  - Pre-fills email if redirected from login

### Staff Registration (`/st/register`)
- **Route:** `/st/register`
- **Allowed Role:** `staff` only
- **Redirect:** `/st/dashboard`
- **Features:**
  - Creates staff account
  - Validates role after registration
  - Pre-fills email if redirected from login

### Manager Registration (`/man/register`)
- **Route:** `/man/register`
- **Allowed Role:** `manager` only
- **Redirect:** `/man/dashboard`
- **Features:**
  - Creates manager account
  - Validates role after registration
  - Pre-fills email if redirected from login

### Admin Registration (`/ad/register`)
- **Route:** `/ad/register`
- **Allowed Role:** `admin` only
- **Redirect:** `/ad/dashboard`
- **Features:**
  - Creates admin account
  - Validates role after registration
  - Pre-fills email if redirected from login

---

## Features

### Role Validation
- All login pages validate the user's role after successful authentication
- If the wrong role attempts to login, an error message is shown
- Registration pages validate the role after account creation

### Email Pre-fill
- When a user tries to login with an email that doesn't exist, they are redirected to the appropriate registration page
- The email is pre-filled in the registration form via URL query parameter

### Automatic Redirects
- After successful login/registration, users are automatically redirected to their role-specific dashboard:
  - Customer → `/cus/dashboard`
  - Staff → `/st/dashboard`
  - Manager → `/man/dashboard`
  - Admin → `/ad/dashboard`

### Cross-Page Navigation
- Each login/register page has links to other role pages
- Easy navigation between different role authentication pages

---

## API Endpoint

All authentication pages use the same backend endpoints:
- **Login:** `POST /api/aut/login/`
- **Register:** `POST /api/aut/register/`

The backend returns role information in the response, which is used to validate and redirect users.

---

## File Structure

```
frontend/app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx          # Customer login
│   └── register/
│       └── page.tsx           # Customer registration
├── st/
│   ├── login/
│   │   └── page.tsx          # Staff login
│   └── register/
│       └── page.tsx           # Staff registration
├── man/
│   ├── login/
│   │   └── page.tsx          # Manager login
│   └── register/
│       └── page.tsx           # Manager registration
└── ad/
    ├── login/
    │   └── page.tsx          # Admin login
    └── register/
        └── page.tsx           # Admin registration
```

---

## Usage

### For Customers
1. Navigate to `/login` or `/register`
2. Login/register with customer credentials
3. Automatically redirected to `/cus/dashboard`

### For Staff
1. Navigate to `/st/login` or `/st/register`
2. Login/register with staff credentials
3. Automatically redirected to `/st/dashboard`

### For Managers
1. Navigate to `/man/login` or `/man/register`
2. Login/register with manager credentials
3. Automatically redirected to `/man/dashboard`

### For Admins
1. Navigate to `/ad/login` or `/ad/register`
2. Login/register with admin credentials
3. Automatically redirected to `/ad/dashboard`

---

## Notes

- The backend must be running on `http://localhost:8000` for authentication to work
- All pages validate roles to ensure users can only access their designated areas
- Email pre-fill works when redirected from login pages
- Cross-origin warnings have been fixed in `next.config.js`
