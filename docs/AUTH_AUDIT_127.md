# Auth & 127.0.0.1 Audit (Step-by-Step)

Audit of frontend, backend, and API for Google + email/password login so VALClean works on `127.0.0.1` like the working project ("FixedPrice Scotland").

---

## 1. Backend (Django)

### 1.1 Auth URLs (`/api/aut/`)

| Endpoint | View | Purpose |
|----------|------|---------|
| `POST /api/aut/register/` | RegisterView | Register, returns user + tokens |
| `POST /api/aut/login/` | LoginView | Email/password login, returns user + tokens |
| `POST /api/aut/google/` | google_login_view | Exchange Supabase OAuth → Django user + JWT |
| `POST /api/aut/logout/` | logout_view | Blacklist refresh token |
| `POST /api/aut/token/refresh/` | TokenRefreshView (SimpleJWT) | Returns `{ "access": "..." }` |
| `GET /api/aut/me/` | user_profile_view | Returns **`{ success, data: <user object> }`** (data = UserSerializer.data, not `data.user`) |

### 1.2 Response shapes

- **Login / Google / Register (with tokens):**  
  `{ success: true, data: { user: {...}, tokens: { access, refresh } } }`
- **GET /api/aut/me/:**  
  `{ success: true, data: <user object> }` — **`data` is the user**, not `data.user`.

### 1.3 CORS & hosts (development)

- `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']`
- `CORS_ALLOW_ALL_ORIGINS = True` (dev)
- `CORS_ALLOW_CREDENTIALS = True`

No changes needed for 127.0.0.1.

---

## 2. Frontend

### 2.1 Bug fixed: `/api/aut/me/` response parsing

- **Backend** returns `data: serializer.data` (the user object).
- **Frontend** `useAuth.checkAuth()` was using `profileData.user`, which is always undefined, so it cleared tokens and sent the user back to login (especially after Google redirect).

**Fix (in `frontend/hooks/use-auth.ts`):**

- Treat `profileData` as the user when it has `id` or `email`.
- Use `const userData = profileData?.user ?? profileData` so both shapes work.

### 2.2 Auth flow (current)

1. **Email/password:**  
   Login → backend returns user + tokens → store tokens → `useAuth` sets user → redirect to `/{rolePrefix}/dashboard`.

2. **Google:**  
   Supabase OAuth → redirect to `/auth/callback` → callback calls `apiClient.googleLogin(supabase access_token, email, name)` → backend returns Django user + tokens → store tokens → **full-page redirect** to `/{rolePrefix}/dashboard` (e.g. `http://127.0.0.1:3000/cus/dashboard`).  
   On load, dashboard has tokens in localStorage; `AuthProvider` runs `checkAuth()` → `GET /api/aut/me/` → with the fix, user is set correctly and dashboard renders.

3. **ProtectedRoute:**  
   If there is an `access_token` in localStorage but context is not hydrated yet, it calls `checkAuth()` once before redirecting to login.

### 2.3 API client

- Base URL: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'`.
- 401: Tries token refresh; only clears tokens and redirects to `/login` when refresh returns 401/403.
- Refresh request URL uses `API_URL` (same base); no double-refresh loop.

### 2.4 127.0.0.1

- **Next.js:** `allowedDevOrigins: ['127.0.0.1', 'localhost', 'http://127.0.0.1:3000', 'http://localhost:3000']` (in `next.config.js`).
- **Dev server:** `"dev": "next dev --hostname 0.0.0.0"` in `package.json` so HMR works when opening `http://127.0.0.1:3000`.
- **API URL:** When using the app at `http://127.0.0.1:3000`, set in `.env.local`:
  - `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api`
  - (Optional; `localhost:8000` often works from 127.0.0.1 too.)
- `.env.example` updated with a short note for 127.0.0.1.

---

## 3. Comparison with FixedPrice Scotland

- **FixedPrice Scotland:** Auth is **Supabase-only**. No Django JWT; API client sends Supabase `access_token`. Callback just `router.push('/account')`.
- **VALClean:** Supabase OAuth is exchanged for **Django JWT** via `POST /api/aut/google/`; all API calls use Django JWT. So the `/api/aut/me/` parsing fix is required for VALClean’s design.

---

## 4. Checklist (what was checked)

- [x] Backend: `/api/aut/google/`, `/api/aut/login/`, `/api/aut/me/`, `/api/aut/token/refresh/`, URLs and response shapes.
- [x] Frontend: `useAuth.checkAuth()` parses `/api/aut/me/` as `data` = user (fixed).
- [x] Frontend: Auth callback stores tokens and full-page redirects to role dashboard.
- [x] Frontend: Login page redirects already-authenticated users to role dashboard.
- [x] Frontend: ProtectedRoute re-checks auth when token exists but context not hydrated.
- [x] Frontend: API client 401 handling and refresh loop prevention.
- [x] CORS and ALLOWED_HOSTS for 127.0.0.1.
- [x] Next.js allowedDevOrigins and dev hostname for 127.0.0.1.
- [x] .env.example note for 127.0.0.1 API URL.

---

## 5. What to do locally

1. Restart frontend after pulling: `npm run dev` (or your script).
2. If you use `http://127.0.0.1:3000`, set in `.env.local`:
   - `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api`
3. Test:
   - Email/password login → should land on role dashboard.
   - Google sign-in → callback → should land on role dashboard (no redirect back to login).
   - Open app at `http://127.0.0.1:3000` and repeat; HMR and API should work.
