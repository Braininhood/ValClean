# High-Quality Booking System - Django Implementation Plan

## Executive Summary

This document outlines a comprehensive plan for building a professional-grade appointment booking system using Python Django, inspired by the Bookly WordPress plugin architecture. The system will support service providers, staff members, customers, and a complete booking workflow with payment processing, notifications, and administrative features.

---

## 1. PROJECT ARCHITECTURE OVERVIEW

### 1.1 Technology Stack
- **Backend Framework**: Django 4.2+ (Python 3.10+)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Django Templates + Bootstrap 5 / React (optional for SPA)
- **Task Queue**: Celery + Redis (for async tasks)
- **Caching**: Redis
- **Payment Processing**: Stripe, PayPal SDK
- **Email**: Django Email Backend + SendGrid/Mailgun
- **SMS**: Twilio API
- **Calendar Integration**: Google Calendar API, Microsoft Outlook Calendar API, Apple Calendar (iCal/CalDAV)
- **Address Lookup**: Royal Mail AddressNow API (UK addresses)
- **API**: Django REST Framework (for mobile/future integrations)

### 1.2 Project Structure
```
booking_system/
├── config/              # Django settings
├── apps/
│   ├── core/           # Core models, utilities, HTTPS middleware
│   ├── accounts/       # User authentication
│   ├── services/       # Service & category management
│   ├── staff/          # Staff member management
│   ├── customers/      # Customer management
│   ├── appointments/   # Appointment booking & scheduling
│   ├── payments/       # Payment processing
│   ├── coupons/        # Discount coupons
│   ├── notifications/  # Email/SMS notifications
│   ├── calendar/       # Calendar views & multi-calendar sync (Google, Outlook, Apple)
│   ├── integrations/   # Third-party integrations (AddressNow, etc.)
│   ├── admin_panel/    # Admin dashboard
│   └── api/            # REST API endpoints
├── static/             # CSS, JS, images
├── templates/          # HTML templates
├── media/              # User uploads
└── requirements.txt
```

---

## 2. CORE DATA MODELS

### 2.1 User Management
- **User** (extends Django User)
  - Role-based permissions (Admin, Staff, Customer)
  - Profile information

### 2.2 Service Management
- **Category**
  - name, description, position, visibility

- **Service**
  - category (FK), title, description, duration (minutes)
  - price, color (for calendar), capacity (max persons)
  - padding_left, padding_right (buffer time)
  - service_type (simple/compound), sub_services (JSON)
  - start_time, end_time (for all-day services)
  - visibility, position, is_active

### 2.3 Staff Management
- **Staff**
  - user (FK), full_name, email, phone
  - photo, info/bio, visibility
  - calendar_provider (google/outlook/apple/none)
  - calendar_id, calendar_data (JSON) - stores provider-specific data
  - position, is_active

- **StaffScheduleItem**
  - staff (FK), day_index (0-6), start_time, end_time
  - breaks (JSON array)

- **StaffService**
  - staff (FK), service (FK), price, capacity
  - deposit (percentage/amount)

- **Holiday**
  - staff (FK, nullable for company-wide)
  - date, repeat_event (yearly), name

### 2.4 Customer Management
- **Customer**
  - user (FK, nullable), name, email, phone
  - address_line1, address_line2, city, county, postcode, country
  - address_validated (boolean, if AddressNow was used)
  - notes, date_created, date_modified

### 2.5 Appointment System
- **Appointment**
  - staff (FK), service (FK), start_date, end_date
  - calendar_event_id (stores event ID from any calendar provider)
  - calendar_provider (google/outlook/apple/none)
  - internal_note
  - extras_duration, series (FK, for recurring)

- **CustomerAppointment**
  - customer (FK), appointment (FK)
  - status (pending/approved/cancelled/rejected)
  - number_of_persons, extras (JSON)
  - custom_fields (JSON), token (for cancellation)
  - time_zone_offset, payment (FK)
  - location (FK, if multi-location)
  - compound_token (for multi-appointment bookings)

- **Series** (for recurring appointments)
  - repeat_type, repeat_interval, until_date

### 2.6 Payment System
- **Payment**
  - type (local/paypal/stripe/etc.)
  - total, paid, status (completed/pending)
  - created, details (JSON)
  - customer_appointments (M2M)

### 2.7 Coupon System
- **Coupon**
  - code, discount (%), deduction (fixed amount)
  - usage_limit, used, start_date, end_date
  - services (M2M, if coupon applies to specific services)

### 2.8 Custom Fields
- **CustomField**
  - type (text/textarea/select/checkbox/date/captcha)
  - label, required, position
  - items (JSON, for select/checkbox)
  - services (M2M, if per-service)

### 2.9 Notifications
- **Notification**
  - type (email/sms), event_type (new/approved/cancelled/reminder)
  - active, subject, message
  - send_to (customer/staff/admin)

- **SentNotification**
  - notification (FK), customer_appointment (FK)
  - sent_at, status, error_message

---

## 3. BOOKING WORKFLOW (Multi-Step Process)

### 3.1 Step 1: Service Selection
**Features:**
- Display service categories
- Filter by category
- Select service(s)
- Select staff member (optional, can be "Any")
- Show service details (duration, price, description)
- Number of persons selector
- Week days selector (if enabled)
- Time range selector (if enabled)
- Skip if service_id provided in URL

**API Endpoints:**
- `GET /api/booking/services/` - List available services
- `GET /api/booking/staff/` - List staff for service
- `GET /api/booking/available-days/` - Get available booking days

### 3.2 Step 2: Extras (Optional)
**Features:**
- Display service extras/add-ons
- Quantity selection
- Price calculation
- Skip if no extras available

### 3.3 Step 3: Time Selection
**Features:**
- Calendar view or time slot list
- Show available time slots based on:
  - Staff schedule
  - Existing appointments
  - Service duration + padding
  - Holidays
  - Minimum time prior to booking
  - Maximum days in advance
- Time zone support (client's timezone)
- "Load more" for pagination
- Block unavailable slots

**API Endpoints:**
- `GET /api/booking/available-slots/` - Get available time slots
- `POST /api/booking/save-session/` - Save booking data in session

### 3.4 Step 4: Repeat (Optional - Recurring Appointments)
**Features:**
- Repeat type (daily/weekly/monthly)
- Repeat interval
- End date or number of occurrences
- Preview recurring appointments
- Skip if recurring disabled

### 3.5 Step 5: Cart
**Features:**
- Display all selected appointments
- Edit/remove items
- Show total price
- Apply coupon code
- Show deposit amount (if enabled)
- Skip if single appointment or cart disabled

**API Endpoints:**
- `POST /api/booking/add-to-cart/`
- `POST /api/booking/remove-from-cart/`
- `POST /api/booking/apply-coupon/`

### 3.6 Step 6: Customer Details
**Features:**
- Customer information form:
  - Name, Email, Phone (with country selector)
  - Address fields (with Royal Mail AddressNow integration for UK addresses):
    - Address lookup/autocomplete using [Royal Mail AddressNow API](https://addressnow.royalmail.com/support/guides/advanced-guide)
    - Real-time address suggestions as user types
    - Automatic population of address fields
    - Support for manual address entry
  - Custom fields (per service or global)
  - Notes
  - Captcha (if enabled)
- Auto-fill for logged-in users
- Login form (if guest booking allowed)
- Validation

**AddressNow Integration Details:**
- JavaScript SDK integration for address autocomplete
- Custom event listeners for address population
- Support for max suggestions (default 7, max 50)
- Support for max results (default 100, max 300)
- Manual load/disable functionality
- Customizable address bar visibility

**API Endpoints:**
- `POST /api/booking/save-details/`
- `POST /api/booking/validate-captcha/`
- `GET /api/booking/address-lookup/` - AddressNow proxy endpoint (if needed)

### 3.7 Step 7: Payment
**Features:**
- Payment method selection:
  - Local payment (pay on-site)
  - PayPal
  - Stripe (credit card)
  - Other gateways (Authorize.Net, 2Checkout, etc.)
- Show total amount, deposit, due amount
- Coupon code input
- Payment processing
- Skip if free service

**API Endpoints:**
- `POST /api/payments/create-intent/` (Stripe)
- `POST /api/payments/paypal/create/`
- `POST /api/payments/process/`

### 3.8 Step 8: Confirmation
**Features:**
- Booking confirmation message
- Booking number(s)
- Appointment details summary
- Email/SMS confirmation sent
- Download calendar file (.ics)
- Link to customer portal

---

## 4. ADMIN PANEL FEATURES

### 4.1 Dashboard
- Statistics overview:
  - Total appointments (today/week/month)
  - Revenue
  - Pending appointments
  - Upcoming appointments
- Recent activity
- Quick actions

### 4.2 Calendar View
- Monthly/Weekly/Daily views
- Drag-and-drop appointment editing
- Color-coded by service
- Filter by staff member
- Create/edit/delete appointments
- Show blocked time slots
- Multi-calendar sync indicators (Google/Outlook/Apple)
- Calendar provider status per staff member

### 4.3 Appointments Management
- List view with filters:
  - Date range
  - Staff member
  - Service
  - Status
  - Customer
- Bulk actions (approve, cancel, delete)
- Export to CSV
- Print view
- Appointment details modal
- Status management
- Internal notes

### 4.4 Services Management
- Category management
- Service CRUD
- Service-staff associations
- Pricing per staff
- Service visibility settings
- Drag-and-drop reordering

### 4.5 Staff Management
- Staff CRUD
- Schedule management (weekly view)
- Break management
- Holiday management
- Service assignments
- Calendar integration per staff (Google/Outlook/Apple)
- Staff availability calendar

### 4.6 Customers Management
- Customer list with search
- Customer details view
- Appointment history
- Payment history
- Customer notes
- Import/Export (CSV)
- Merge duplicate customers

### 4.7 Payments Management
- Payment list with filters
- Payment details
- Refund processing
- Payment reports
- Revenue analytics
- Export financial data

### 4.8 Coupons Management
- Coupon CRUD
- Usage tracking
- Service associations
- Expiry management

### 4.9 Custom Fields Management
- Field CRUD
- Field types configuration
- Service associations
- Ordering

### 4.10 Notifications Management
- Email templates
- SMS templates
- Notification codes/placeholders
- Test sending
- Notification logs
- Reminder scheduling

### 4.11 Settings
- **General Settings:**
  - Company information
  - Time zone
  - Date/time formats
  - Minimum time prior to booking
  - Maximum days in advance
  - Slot length
  - First day of week
  - Time slot display format

- **Appearance Settings:**
  - Theme colors
  - Form labels customization
  - Progress tracker visibility
  - Calendar display options

- **Customer Settings:**
  - Required fields
  - Phone field configuration
  - Auto-create user accounts
  - Default user role

- **Payment Settings:**
  - Payment methods configuration
  - Gateway credentials
  - Currency settings
  - Deposit settings

- **Notification Settings:**
  - Email settings (SMTP)
  - SMS provider settings
  - Notification preferences
  - Reminder timing

- **Calendar Integration Settings:**
  - **Google Calendar:**
    - OAuth 2.0 configuration
    - Sync settings (one-way/two-way)
    - Event formatting
  - **Microsoft Outlook:**
    - OAuth 2.0 configuration (Microsoft Graph API)
    - Sync settings (one-way/two-way)
    - Event formatting
  - **Apple Calendar:**
    - CalDAV server configuration
    - iCal file generation for downloads
    - Sync settings
  - Default calendar provider selection
  - Per-staff calendar configuration

- **Holidays Settings:**
  - Company-wide holidays
  - Holiday templates

---

## 5. CUSTOMER PORTAL

### 5.1 Customer Dashboard
- Upcoming appointments list
- Past appointments (paginated)
- Appointment details
- Cancel appointment (with restrictions)
- Reschedule appointment
- Payment history
- Profile management

### 5.2 Booking History
- All appointments with status
- Filter by date range, status
- Download receipts
- Re-book services

---

## 6. TECHNICAL IMPLEMENTATION DETAILS

### 6.1 Time Slot Calculation Algorithm
**Requirements:**
- Consider staff working hours
- Account for breaks
- Check existing appointments
- Apply service duration + padding
- Handle time zones
- Support night shifts (crossing midnight)
- Minimum time prior to booking
- Maximum advance booking days

**Implementation:**
- Use Django Q objects for complex queries
- Cache available slots (Redis)
- Background task to pre-calculate slots
- Real-time validation on booking

### 6.2 Session Management
- Use Django sessions for booking data
- Store booking state between steps
- Session expiry (30 minutes)
- Handle concurrent bookings
- Prevent double-booking

### 6.3 Payment Integration
- **Stripe:**
  - Payment Intents API
  - Webhook handling for payment status
  - Refund support

- **PayPal:**
  - REST API integration
  - IPN/Webhook handling
  - Express Checkout

- **Local Payment:**
  - Mark as pending
  - Manual completion by admin

### 6.4 Notification System
- **Email Notifications:**
  - Template system with placeholders
  - HTML and plain text versions
  - Attachment support (calendar files)
  - Queue for bulk sending (Celery)

- **SMS Notifications:**
  - Twilio integration
  - Template system
  - Delivery status tracking
  - Cost tracking

- **Reminders:**
  - Celery periodic tasks
  - Configurable timing (X hours before)
  - Time zone aware

### 6.5 Multi-Calendar Integration

#### 6.5.1 Google Calendar Integration
- OAuth 2.0 authentication
- Google Calendar API v3
- Create events on booking
- Update events on modification
- Delete events on cancellation
- Two-way sync (import busy slots)
- Handle time zones
- Event description formatting

#### 6.5.2 Microsoft Outlook Calendar Integration
- OAuth 2.0 authentication (Microsoft Graph API)
- Microsoft Graph Calendar API
- Create/update/delete events
- Two-way sync support
- Time zone handling
- Event formatting with appointment details

#### 6.5.3 Apple Calendar Integration
- CalDAV protocol support
- iCal file generation (.ics) for download
- Event creation via CalDAV server
- Support for standard calendar apps (Apple Calendar, Thunderbird, etc.)
- Time zone support
- Recurring event support

#### 6.5.4 Unified Calendar Interface
- Abstract calendar provider interface
- Provider-agnostic event management
- Automatic provider selection based on staff settings
- Fallback mechanisms if primary provider fails
- Calendar sync status monitoring
- Error handling and retry logic

### 6.6 Address Management & Royal Mail AddressNow Integration

#### 6.6.1 Royal Mail AddressNow Integration
**Implementation Details:**
- JavaScript SDK integration for UK address lookup
- Real-time address autocomplete as user types postcode/address
- Automatic form population on address selection
- Support for manual address entry (fallback)
- Configurable max suggestions (default: 7, max: 50)
- Configurable max results (default: 100, max: 300)
- Customizable address bar visibility (can be hidden)
- Event listeners for address population:
  - `addressNow.listen("load")` - When AddressNow loads
  - `addressNow.listen("populate")` - When address is populated
- Manual load/disable functionality:
  - `addressNow.load()` - Manually trigger load
  - `addressNow.disable()` - Disable AddressNow
- Custom options configuration via event listeners
- Reference: [Royal Mail AddressNow Advanced Guide](https://addressnow.royalmail.com/support/guides/advanced-guide)

**Frontend Implementation:**
```javascript
// Initialize AddressNow with custom options
addressNow.listen("options", function(options) {
    options.bar = options.bar || {};
    options.bar.visible = false; // Hide address bar
    options.search = {
        maxSuggestions: 7,
        maxResults: 100
    };
});

// Handle address population
addressNow.listen("load", function(control) {
    control.listen("populate", function(address) {
        // Populate form fields
        document.getElementById("address_line1").value = address.Line1;
        document.getElementById("address_line2").value = address.Line2 || "";
        document.getElementById("city").value = address.PostTown || "";
        document.getElementById("county").value = address.County || "";
        document.getElementById("postcode").value = address.Postcode || "";
    });
});
```

#### 6.6.2 Address Storage & Validation
- Normalized address fields (line1, line2, city, county, postcode, country)
- Address validation (UK postcode format validation)
- Support for international addresses (non-UK, manual entry)
- Address history for customers
- Address validation flag to track if AddressNow was used

### 6.7 Custom Fields System
- Dynamic form generation
- Field validation
- Per-service or global fields
- File upload support
- Captcha integration

### 6.8 Coupon System
- Code validation
- Service restrictions
- Usage limits
- Expiry dates
- Percentage and fixed discounts
- Combination rules

---

## 7. API DESIGN (Django REST Framework)

### 7.1 Public API Endpoints
- Booking workflow endpoints
- Available slots endpoint
- Service/staff listings
- Customer portal endpoints

### 7.2 Admin API Endpoints
- Full CRUD for all models
- Bulk operations
- Reports and analytics
- Export endpoints

### 7.3 Authentication
- Session-based (web)
- Token authentication (API)
- OAuth2 (future mobile apps)

---

## 8. SECURITY CONSIDERATIONS

### 8.1 HTTPS Enforcement (IMPLEMENTED ✅)
- **All pages require HTTPS in production**
- Custom `ForceHTTPSMiddleware` automatically redirects HTTP to HTTPS
- Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- HTTP Strict Transport Security (HSTS) enabled:
  - 1 year duration
  - Includes subdomains
  - Preload enabled
- Security headers configured:
  - X-Frame-Options: DENY (prevents clickjacking)
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: Enabled
  - Referrer-Policy: strict-origin-when-cross-origin
- Works behind reverse proxies (checks X-Forwarded-Proto header)
- Development mode: HTTPS enforcement disabled (Django dev server doesn't support SSL)
- Production mode: HTTPS always enforced - no exceptions

**Implementation Details:**
- Middleware: `core.middleware.ForceHTTPSMiddleware`
- Settings: Conditional based on `DEBUG` mode
- Documentation: See `HTTPS_ENFORCEMENT.md`

### 8.2 Data Protection
- Encrypt sensitive data (payment info)
- Secure session management
- CSRF protection
- XSS prevention
- SQL injection prevention (Django ORM)

### 8.3 Access Control
- Role-based permissions
- Staff can only see their appointments
- Customers can only access their data
- Admin-only sensitive operations

### 8.4 Payment Security
- PCI compliance considerations
- Never store credit card details
- Use payment gateway tokens
- Secure webhook endpoints
- All payment endpoints require HTTPS

---

## 9. PERFORMANCE OPTIMIZATION

### 9.1 Database Optimization
- Proper indexing (staff_id, service_id, start_date)
- Query optimization (select_related, prefetch_related)
- Database connection pooling
- Read replicas (for high traffic)

### 9.2 Caching Strategy
- Cache available time slots
- Cache service/staff listings
- Cache calendar views
- Redis for session storage

### 9.3 Background Tasks
- Email/SMS sending (Celery)
- Multi-calendar sync (Google, Outlook, Apple)
- Reminder notifications
- Report generation
- Data cleanup tasks

### 9.4 Frontend Optimization
- Lazy loading for calendar
- AJAX for step navigation
- Progressive enhancement
- Mobile-responsive design

---

## 10. TESTING STRATEGY

### 10.1 Unit Tests
- Model methods
- Business logic
- Utility functions
- Payment calculations

### 10.2 Integration Tests
- Booking workflow
- Payment processing
- Notification sending
- Multi-calendar sync (Google, Outlook, Apple)
- AddressNow integration

### 10.3 End-to-End Tests
- Complete booking flow
- Admin operations
- Customer portal

### 10.4 Performance Tests
- Load testing for booking
- Database query optimization
- API response times

---

## 11. DEPLOYMENT PLAN

### 11.1 Development Environment
- Docker Compose setup
- Local PostgreSQL
- Redis for caching
- Development settings

### 11.2 Production Environment
- **Web Server**: Gunicorn + Nginx
- **Database**: PostgreSQL (managed service)
- **Cache**: Redis (managed service)
- **Task Queue**: Celery workers
- **Static Files**: CDN (AWS S3/CloudFront)
- **Monitoring**: Sentry for error tracking
- **Logging**: Centralized logging system

### 11.3 CI/CD Pipeline
- Automated testing
- Code quality checks
- Database migrations
- Deployment automation

---

## 12. DEVELOPMENT PHASES

### Phase 1: Core Foundation (Weeks 1-3)
- Project setup
- Database models
- Basic admin panel
- User authentication
- Service/Staff/Customer CRUD

### Phase 2: Booking Engine (Weeks 4-6)
- Time slot calculation
- Multi-step booking form
- Session management
- Basic calendar view

### Phase 3: Payment Integration (Weeks 7-8)
- Payment models
- Stripe integration
- PayPal integration
- Payment processing workflow

### Phase 4: Notifications (Weeks 9-10)
- Email system
- SMS integration
- Notification templates
- Reminder system

### Phase 5: Advanced Features (Weeks 11-13)
- Multi-calendar integration (Google, Outlook, Apple)
- Royal Mail AddressNow integration
- Coupon system
- Custom fields
- Recurring appointments
- Customer portal

### Phase 6: Admin Enhancements (Weeks 14-15)
- Advanced calendar views
- Reporting
- Analytics dashboard
- Export functionality

### Phase 7: Polish & Testing (Weeks 16-17)
- UI/UX improvements
- Performance optimization
- Comprehensive testing
- Bug fixes

### Phase 8: Deployment & Documentation (Week 18)
- Production deployment
- Documentation
- User guides
- Admin training materials

---

## 13. FUTURE ENHANCEMENTS (Post-MVP)

### 13.1 Multi-Location Support
- Location model
- Location-based booking
- Staff assignment to locations

### 13.2 Service Extras/Add-ons
- Extras model
- Pricing per extra
- Quantity selection

### 13.3 Waitlist System
- Waitlist for fully booked slots
- Automatic notification on availability

### 13.4 Reviews & Ratings
- Customer reviews
- Staff ratings
- Service ratings

### 13.5 Mobile Apps
- Native iOS/Android apps
- Push notifications
- Mobile booking

### 13.6 Advanced Analytics
- Revenue reports
- Staff performance
- Service popularity
- Customer insights

### 13.7 Integrations
- Zoom/Google Meet integration
- Accounting software (QuickBooks, Xero)
- CRM integration
- Marketing automation

---

## 14. DOCUMENTATION REQUIREMENTS

### 14.1 Technical Documentation
- API documentation (Swagger/OpenAPI)
- Database schema documentation
- Architecture diagrams
- Deployment guides

### 14.2 User Documentation
- Admin user guide
- Staff user guide
- Customer guide
- Video tutorials

### 14.3 Developer Documentation
- Setup instructions
- Contribution guidelines
- Code style guide
- Testing guidelines

---

## 15. SUCCESS METRICS

### 15.1 Performance Metrics
- Page load times < 2 seconds
- API response times < 500ms
- 99.9% uptime
- Handle 1000+ concurrent bookings

### 15.2 Business Metrics
- Booking conversion rate
- Average booking value
- Customer retention
- Staff utilization rate

---

## 16. RISK MITIGATION

### 16.1 Technical Risks
- **Double-booking**: Implement database locks and real-time validation
- **Payment failures**: Retry logic and manual intervention
- **Calendar sync issues**: Error handling and retry mechanisms for all providers
- **AddressNow API availability**: Fallback to manual address entry
- **Performance under load**: Load testing and scaling strategy

### 16.2 Business Risks
- **Payment gateway downtime**: Multiple payment options
- **SMS/Email delivery failures**: Queue system with retries
- **Data loss**: Regular backups and disaster recovery plan

---

## CONCLUSION

This plan provides a comprehensive roadmap for building a production-ready booking system using Django. The system will be scalable, secure, and feature-rich, supporting the needs of service-based businesses while maintaining code quality and user experience standards.

**Estimated Timeline**: 18 weeks for MVP
**Team Size**: 2-3 developers (1 backend, 1 frontend, 1 full-stack)
**Budget Considerations**: Third-party service costs (Stripe, Twilio, SendGrid, Google Cloud, Microsoft Azure for Outlook API, Royal Mail AddressNow subscription)

---

*This plan is a living document and should be updated as requirements evolve and new insights are gained during development.*

