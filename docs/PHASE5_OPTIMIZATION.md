# Phase 5: Polish & Optimization – Implementation Notes

Reference: [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) Phase 5 (Weeks 12–13).

---

## Week 12: Performance Optimization

### Day 1–2: Backend Optimization

#### Database (Supabase PostgreSQL)
- **Indexes:** Models already use `db_index=True` and `Meta.indexes` where needed:
  - Orders: `order_number`, `tracking_token`, `customer`+`status`, `status`+`scheduled_date`, `postcode`
  - Appointments: `staff`+`start_time`, `status`+`start_time`, `order`, `subscription`
  - Subscriptions: `subscription_number`, `tracking_token`, `customer`+`status`
  - Coupons: `code`, `status`+`valid_from`+`valid_until`
  - Accounts: Invitation `token`+`is_active`, `email`+`role`
  - Staff: `postcode`+`is_active`, `is_active`+`email`
  - Services: `category`+`is_active`, `slug`
- **Action:** When adding new filters (e.g. list by date range), add composite indexes for those queries. Run `EXPLAIN ANALYZE` on slow queries in production.

#### Caching
- **Base:** `LocMemCache` when `REDIS_URL` is not set (dev/simple deploy).
- **Production:** Set `REDIS_URL` in env to use Redis (see `config/settings/production.py`).
- **Supabase-only (no Redis):** Use Django database cache:
  ```python
  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
          'LOCATION': 'cache_table',
      }
  }
  ```
  Then run: `python manage.py createcachetable`.
- **Usage:** Consider `@cache_page` or `cache.get/set` for heavy read endpoints (e.g. public service list, slot availability) with short TTL (e.g. 60–300s).

#### API response optimization
- **Already in place:** `select_related()` and `prefetch_related()` used in:
  - Orders, appointments, subscriptions, customers, staff, services, coupons, reports, route views.
- **Target:** Keep list/detail responses under ~200ms for typical payloads; add pagination where needed (PAGE_SIZE 20 is set).

#### Background tasks
- **Optional:** Celery is configured in production when `REDIS_URL` is set (see production.py).
- **Use for:** Email sending, calendar sync, report generation, reminder jobs. Not required for MVP.

#### Load testing
- **Tool:** Use `locust`, `k6`, or `wrk` against key endpoints (e.g. `/api/svc/`, `/api/slots/...`, `/api/aut/login/`).
- **Target:** API responses &lt; 200ms at p95 under expected load.

---

### Day 3–4: Frontend Optimization

- **Code splitting:** Next.js App Router does automatic code splitting per route.
- **Images:** Use `next/image` for all images; configure `images.domains` if using external CDN.
- **Lazy loading:** Use `next/dynamic` with `ssr: false` for heavy client-only components (e.g. map, rich editor).
- **Bundle size:** Run `npm run build` and check `.next/build-manifest.json` or use `@next/bundle-analyzer`.
- **Lighthouse:** Run in production build; aim for Performance &gt; 90.

---

### Day 5: SEO Optimization

Implemented in frontend:
- **Meta tags:** Root layout + per-page `metadata` / `generateMetadata` (title, description).
- **Open Graph:** `openGraph` in metadata for sharing.
- **Structured data:** JSON-LD (Organization, WebSite, local business) on home/booking where relevant.
- **Sitemap:** `app/sitemap.ts` generates sitemap.
- **robots.txt:** `app/robots.ts` allows crawlers and points to sitemap.

---

## Acceptance Criteria (Phase 5)

| Criterion              | Notes |
|------------------------|--------|
| Page load &lt; 2s       | Measure with Lighthouse / WebPageTest. |
| API responses &lt; 200ms | Measure with server logs or APM; optimize N+1 and add cache where needed. |
| Lighthouse &gt; 90     | Run against production build. |
| SEO best practices     | Meta, OG, JSON-LD, sitemap, robots in place. |
