# IMPLEMENTATION_ROADMAP Verification (Line 1 – Week 12 Complete)

This document verifies what has been **created and implemented** from the start of [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) through **Week 12**, and how to **test** all connections and flows. Use it to confirm everything works correctly end-to-end.

---

## 1. Scope

- **Roadmap:** Line 1 through end of **Week 12** (Phase 5: Polish & Optimization).
- **Code:** Backend (Django + Supabase PostgreSQL), Frontend (Next.js App Router), API (security prefixes: `/api/svc/`, `/api/aut/`, `/api/bkg/`, `/api/cus/`, `/api/ad/`, etc.).
- **Access:** App at `http://127.0.0.1:3000`, API at `http://127.0.0.1:8000/api` (or set `NEXT_PUBLIC_API_URL` for 127.0.0.1).

---

## 2. Fixes Applied (Booking & Order Full Info)

### 2.1 Order missing guest_* when logged-in customer

**Issue:** Orders created with `customer_id` had `guest_email`, `guest_name`, `guest_phone` as `null`, so the order record lacked display/invoice info.

**Backend (`backend/apps/orders/views.py`):**

- When creating an order we now **always** set guest/display fields from the payload or from the linked customer:
  - `guest_email` = payload or `customer.email`
  - `guest_name` = payload or `customer.name`
  - `guest_phone` = payload or `customer.phone`
- So every order has full contact/display info whether guest or logged-in.

### 2.2 /booking/details not using logged-in user info

**Issue:** When a user was logged in, `/booking/details` did not pre-fill name, email, phone, address from their profile.

**Frontend:**

- **`frontend/app/booking/details/page.tsx`:**  
  When user is authenticated and role is `customer`, we fetch `GET /api/cus/profile/` and pre-fill the form and booking store (name, email, phone, address). We also set `customerId` in the store.
- **`frontend/store/booking-store.ts`:**  
  Added `customerId` and `setCustomerId` so the payment step can send `customer_id` when the user is logged in.

### 2.3 Payment step not sending customer_id

**Issue:** Payment page did not send `customer_id` when the user was logged in, so the backend could not link the order to the account and had no customer to fall back to for guest_*.

**Frontend (`frontend/app/booking/payment/page.tsx`):**

- Reads `customerId` from the booking store.
- When creating the order, if `customerId` is set, the payload includes `customer_id`, so the order is linked to the customer and the backend can set guest_* from payload or customer.

---

## 3. Connections to Test

### 3.1 Booking flow (guest and logged-in)

| Step | URL | What to test |
|------|-----|----------------|
| 1 | `http://127.0.0.1:3000/booking/postcode` | Enter UK postcode → next |
| 2 | `http://127.0.0.1:3000/booking/services` | Services for area → select service → next |
| 3 | `http://127.0.0.1:3000/booking/date-time` | Pick date/time (and staff if shown) → next |
| 4 | `http://127.0.0.1:3000/booking/details` | **Guest:** Fill name, email, phone, address. **Logged-in customer:** Form should be **pre-filled** from profile (and store has `customerId`) |
| 5 | `http://127.0.0.1:3000/booking/payment` | Review → Complete booking. Order created with `guest_email`, `guest_name`, `guest_phone` and, if logged in, `customer_id` |
| 6 | `http://127.0.0.1:3000/booking/confirmation?order=ORD-...` | Confirmation and optional account linking |

**APIs used:**

- Postcode/services: `GET /api/svc/by-postcode/`, `GET /api/stf/by-postcode/`
- Slots: `GET /api/slots/available/`
- Address: `GET /api/addr/autocomplete/`, `POST /api/addr/validate/`
- Order: `POST /api/bkg/orders/` (payload: items, scheduled_date/time, guest_*, address_*, optional `customer_id`)

### 3.2 Dashboards by role

- **Customer:** `http://127.0.0.1:3000/cus/dashboard` – appointments, orders, profile, settings/calendar. From dashboard, “Book” (or similar) should go to `/booking`; details step pre-fills if profile is complete.
- **Staff:** `http://127.0.0.1:3000/st/dashboard` – jobs, schedule, calendar.
- **Manager:** `http://127.0.0.1:3000/man/dashboard` – team, customers (if applicable).
- **Admin:** `http://127.0.0.1:3000/ad/dashboard` – metrics, orders, customers, staff, services, reports, routes, calendar settings.

All role dashboards should be reachable after login (email/password or Google) and should only show features allowed for that role.

### 3.3 Order has full info

After creating an order (guest or logged-in):

- **Backend:** Order row should have `guest_email`, `guest_name`, `guest_phone` and address fields populated (and `customer_id` if logged-in customer).
- **Frontend:** Confirmation page and any order detail view should show name, email, phone, address (from order or linked customer).

---

## 4. Roadmap Status (Line 1 – Week 12)

| Phase / Week | Status | Notes |
|--------------|--------|--------|
| **Phase 1: Foundation (Weeks 1–3)** | | |
| Week 1: Project setup, DB, API structure | Done | Django + Next.js, Supabase/PostgreSQL, CORS |
| Week 2: Auth, core API, frontend auth | Done | JWT, roles, protected routes, login/register |
| Week 3: Booking flow (postcode → services → date/time → details → payment) | Done | Guest checkout; details pre-fill for logged-in customer |
| **Phase 2: Enhanced (Weeks 4–5)** | | |
| Week 4: Payment (Stripe/PayPal) | Paused | Waiting for customer access |
| Week 4–5: Calendar (Google/Outlook/Apple), address, notifications | Done | Calendar sync, Google Places, email templates |
| **Phase 3: Management (Weeks 6–8)** | | |
| Week 6: Admin dashboard | Done | Metrics, recent orders, quick actions |
| Week 7: Staff & customer & service management | Done | Staff areas, performance, customer list/detail, services/categories |
| Week 8: Staff portal, customer portal, mobile | Done | Dashboards, jobs, profile, responsive/PWA |
| **Phase 4: Advanced (Weeks 9–11)** | | |
| Week 9: Subscriptions, orders, coupons, guest support | Done | Multi-service orders, guest links, change requests, coupons |
| Week 10: Reports | Done | Revenue, appointments, staff performance |
| Week 11: Routes, calendar sync UI | Done | Route optimization, calendar settings, sync, custom events |
| **Phase 5: Polish (Week 12)** | | |
| Week 12: Backend optimization | Done | Cache (LocMem/Redis), query patterns, indexes (see PHASE5_OPTIMIZATION.md) |
| Week 12: Frontend optimization | Partial | Code splitting; image/lazy/bundle/Lighthouse manual |
| Week 12: SEO | Done | Meta, Open Graph, JSON-LD, sitemap, robots |

---

## 5. Testing Checklist

Use this to verify behaviour end-to-end:

1. **Auth**
   - [ ] Login with email/password → redirect to role dashboard.
   - [ ] Login with Google (if configured) → redirect to role dashboard.
   - [ ] Logout → redirect to login; protected routes redirect to login when not authenticated.

2. **Booking (guest)**
   - [ ] Open `http://127.0.0.1:3000/booking` → postcode → services → date/time → details (fill all) → payment → confirm. Order created with guest_* and address filled.

3. **Booking (logged-in customer)**
   - [ ] Log in as customer → go to `/booking/details` (or full flow from postcode). Details form should be **pre-filled** from profile.
   - [ ] Complete booking. Order should have `customer_id` and `guest_email`, `guest_name`, `guest_phone` and address populated.

4. **Order record**
   - [ ] In DB or admin, open the created order. Check `guest_email`, `guest_name`, `guest_phone`, address fields and, for logged-in, `customer_id`.

5. **Dashboards**
   - [ ] Customer: dashboard, profile, appointments, orders, settings/calendar.
   - [ ] Staff: dashboard, jobs, schedule.
   - [ ] Admin: dashboard, orders, customers, staff, services, reports, routes, calendar settings.

6. **APIs**
   - [ ] Public: `GET /api/svc/`, `GET /api/slots/available/`, `POST /api/bkg/orders/`.
   - [ ] Auth: `POST /api/aut/login/`, `GET /api/aut/me/`.
   - [ ] Customer: `GET /api/cus/profile/`, `GET /api/cus/orders/`, `GET /api/cus/appointments/`.

---

## 6. Documentation References

- **[IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)** – Full task list and acceptance criteria (line 1 – end).
- **[PHASE5_OPTIMIZATION.md](./PHASE5_OPTIMIZATION.md)** – Backend cache, DB indexes, API optimization, SEO.
- **[AUTH_AUDIT_127.md](./AUTH_AUDIT_127.md)** – Auth and 127.0.0.1 setup.
- **[TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md)** – System design and APIs.

---

**Summary:** From line 1 through Week 12, the roadmap is implemented and Week 12 is complete except optional load testing and manual Lighthouse/bundle work. Booking flow now pre-fills details for logged-in customers and orders are always stored with full guest/display info (`guest_email`, `guest_name`, `guest_phone`, address) and optional `customer_id`. Use the testing checklist above to confirm all connections and dashboards by role.
