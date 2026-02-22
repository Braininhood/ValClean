# VALClean Booking System - Best Professional Solution

A comprehensive, best-in-class appointment booking system combining the best features from HouseCallPro and Bookly, specifically designed for VALClean (https://valclean.uk/).

## 🎯 New Professional Solution Documents

**Start here for the complete professional solution:**

1. **📘 [SOLUTION_OVERVIEW.md](SOLUTION_OVERVIEW.md)** - Quick start guide and overview
2. **⭐ [VALCLEAN_BEST_SOLUTION.md](VALCLEAN_BEST_SOLUTION.md)** - Complete professional solution (READ THIS FIRST!)
3. **🗺️ [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Step-by-step implementation guide (15 weeks)
4. **📊 [FEATURE_COMPARISON.md](FEATURE_COMPARISON.md)** - Competitive analysis (HouseCallPro vs Bookly vs Our Solution)
5. **🏗️ [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)** - Detailed technical architecture

**These documents provide:**
- ✅ Complete solution combining best features from HouseCallPro and Bookly
- ✅ **Technology stack confirmed: Next.js + Django**
- ✅ **Development setup: localhost + SQLite**
- ✅ **User roles: Admin, Manager, Staff, Customer**
- ✅ Step-by-step 15-week implementation roadmap
- ✅ Feature-by-feature competitive analysis
- ✅ Detailed technical architecture
- ✅ User experience design
- ✅ Success metrics and KPIs

### Repository & deployment

- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** – Push project to GitHub and keep repo structure correct.
- **[docs/AWS_DEPLOYMENT_GUIDE.md](docs/AWS_DEPLOYMENT_GUIDE.md)** – Full step-by-step guide to deploy on AWS (VPC, RDS, EC2, ALB, HTTPS, DNS).

---

## Original Project

A comprehensive appointment booking system built with Django, inspired by professional booking platforms.

## Features

### ✅ Implemented (Phase 1 & 2)
- ✅ Multi-step booking workflow (8 steps)
- ✅ Staff and service management (full CRUD)
- ✅ Customer management with address fields
- ✅ Appointment scheduling with time slot calculation
- ✅ Role-based authentication (Admin, Manager, Staff, Customer)
- ✅ Role-based dashboards
- ✅ HTTPS enforcement (production)
- ✅ Session-based booking flow
- ✅ Time slot availability checking
- ✅ Staff schedule management
- ✅ Holiday management
- ✅ Sample data creation command

### 🚧 In Progress / Planned (Phase 3+)
- Payment processing (Stripe, PayPal, and more)
- Email and SMS notifications
- Calendar integration (Google, Outlook, Apple) - All roles can sync
- Custom event creation to external calendars (all roles)
- Subscription system (recurring services: weekly/biweekly/monthly for 1-12 months)
- Multi-service orders (request multiple services in one order)
- Order management (request date/time changes, cancel with 24h policy)
- Subscription management (pause, cancel, manage individual appointments)
- Google Places API integration (address autocomplete)
- Postcode-first booking flow
- Staff area/postcode assignment with radius
- Coupon/discount system
- Custom fields support
- Recurring appointments
- Extras/add-ons system

## Project Structure

```
booking_system/
├── config/              # Django settings
├── apps/
│   ├── core/           # Core models, utilities
│   ├── accounts/       # User authentication
│   ├── services/       # Service & category management
│   ├── staff/          # Staff member management
│   ├── customers/      # Customer management
│   ├── appointments/   # Appointment booking & scheduling
│   ├── payments/       # Payment processing
│   ├── coupons/        # Discount coupons
│   ├── notifications/  # Email/SMS notifications
│   ├── calendar_sync/  # Multi-calendar sync (Google, Outlook, Apple)
│   ├── integrations/   # Third-party integrations
│   ├── admin_panel/    # Admin dashboard
│   └── api/            # REST API endpoints
├── static/             # CSS, JS, images
├── templates/          # HTML templates
├── media/              # User uploads
└── requirements.txt
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- SQLite (for development - included with Python)
- Redis (optional for development, required for production)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd booking_system

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Redis (Optional for development)
REDIS_URL=redis://localhost:6379/0

# Add other API keys as needed
```

### 4. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (already created with default credentials)
python manage.py createsuperuser
```

**Default Admin Credentials (Development):**
- **Username:** `admin`
- **Email:** `admin@valclean.uk`
- **Password:** `*******`
- **Admin Panel:** http://localhost:8000/admin/

**⚠️ Important:** Change the admin password in production!

### 5. Create Sample Data (Optional)

```bash
# Create sample services, staff, customers, and appointments
python manage.py create_sample_data
```

This will create:
- 3 Categories (Cleaning Services, Maintenance Services, Green Spaces)
- 7 Services (based on VALclean website)
- 3 Staff members with schedules
- 3 Test users/customers
- 5 Sample appointments

### 6. Run Development Server

**IMPORTANT:** Always use the virtual environment Python for Django commands.

```bash
# On Windows (PowerShell):
.\venv\Scripts\python.exe manage.py runserver

# Or activate the virtual environment first:
.\venv\Scripts\Activate.ps1
python manage.py runserver

# On Linux/Mac:
source venv/bin/activate
python manage.py runserver
```

**Alternative:** Use the provided convenience script:
```powershell
.\runserver.ps1  # Windows PowerShell
```

The Django backend will be available at `http://localhost:8000`

### 7. Start Frontend (Next.js)

```bash
# Navigate to frontend directory (if separate)
cd frontend  # or wherever your Next.js app is

# Install dependencies
npm install

# Start development server
npm run dev
```

The Next.js frontend will be available at `http://localhost:3000`

### 8. Access the Application

**Frontend (Next.js):**
- **Home**: http://localhost:3000/
- **Book Appointment**: http://localhost:3000/booking/
- **Login**: http://localhost:3000/login/
- **Customer Dashboard**: http://localhost:3000/cus/dashboard/ (Security: /cus/)
- **Staff Dashboard**: http://localhost:3000/st/dashboard/ (Security: /st/)
- **Manager Dashboard**: http://localhost:3000/man/dashboard/ (Security: /man/)
- **Admin Dashboard**: http://localhost:3000/ad/dashboard/ (Security: /ad/)

**Backend (Django):**
- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

## Documentation

### 🎯 Best Professional Solution (NEW - Start Here!)
- **`VALCLEAN_BEST_SOLUTION.md`** ⭐ - **Complete professional solution** combining best features from HouseCallPro and Bookly, tailored for VALClean
- **`IMPLEMENTATION_ROADMAP.md`** - **Step-by-step implementation guide** with detailed tasks, acceptance criteria, and deliverables for each phase
- **`FEATURE_COMPARISON.md`** - **Feature comparison** between HouseCallPro, Bookly, and our VALClean solution
- **`TECHNICAL_ARCHITECTURE.md`** - **Detailed technical architecture** covering system design, data flow, scalability, and deployment
- **`SOLUTION_OVERVIEW.md`** - Quick start guide and overview

### Main Documentation
- `BOOKING_SYSTEM_PLAN.md` - Complete development plan and feature specifications
- `PHASE1_COMPLETE.md` - Phase 1 implementation details
- `PHASE2_COMPLETE.md` - Phase 2 implementation details
- `PROJECT_STATUS.md` - Current project status and progress

### Implementation Details
- `HTTPS_ENFORCEMENT.md` - HTTPS enforcement documentation
- `SAMPLE_DATA_CREATED.md` - Sample data creation guide
- `BOOKING_FIX.md` - Booking system fixes
- `BOOKING_PAGES_FIX.md` - Booking pages fixes
- `DASHBOARD_FIXES.md` - Dashboard fixes
- `AUTHENTICATION_FIXES.md` - Authentication flow fixes
- `PROFILE_EDIT_FIXES.md` - Profile editing fixes
- `ROLE_BASED_DASHBOARDS.md` - Dashboard implementation

## License

[Add your license here]


# Customer Requirements Document

**Purpose:** Information needed from customers/mentors to properly configure the G.Creators platform

---

## 👤 Information Needed from Each Mentor

### 1. **Profile & Expertise** (Already Collected)
- [ ] Full name
- [ ] Professional title
- [ ] Areas of expertise
- [ ] Biography
- [ ] Profile photo
- [ ] Social media links

---

### 2. **Payment & Payout Information** 🔴 CRITICAL

#### Stripe Account Setup:
- [ ] **Legal business name** (or personal name if sole proprietor)
- [ ] **Business type:**
  - [ ] Individual/Sole Proprietor
  - [ ] Company/LLC
  - [ ] Non-profit
- [ ] **Tax ID:** (EIN for US, VAT for EU, etc.)
- [ ] **Country of residence**
- [ ] **Bank account information:**
  - Bank name
  - Account holder name
  - Account number
  - Routing number (US) or IBAN (International)
  - SWIFT/BIC code (for international)

#### Payment Preferences:
- [ ] **Payout schedule:** Weekly / Bi-weekly / Monthly
- [ ] **Minimum payout threshold:** (e.g., $50, $100)
- [ ] **Currency preference:** USD / EUR / UAH / Other

#### Platform Fees Agreement:
- [ ] Accept platform commission rate (e.g., 15-20% per transaction)
- [ ] Understand Stripe processing fees (2.9% + $0.30)

**Important Notes:**
- Stripe will require ID verification (passport or driver's license)
- Some countries require additional business documentation
- Payouts may take 2-7 days depending on country

---

### 3. **Consultation Services** 🔴 CRITICAL

#### Consultation Types:
For each consultation type offered:

**Type 1:** (e.g., "1-on-1 Strategy Session")
- [ ] **Service name**
- [ ] **Description** (what's included)
- [ ] **Duration:** ___ minutes (e.g., 30, 60, 90)
- [ ] **Price:** $___ USD (or other currency)
- [ ] **Delivery method:**
  - [ ] Video call (Zoom/Google Meet link)
  - [ ] Phone call
  - [ ] In-person (if applicable)
  - [ ] Chat-based
- [ ] **Preparation required:** (e.g., "Send questions 24h in advance")
- [ ] **Booking lead time:** (e.g., "Must book at least 48h in advance")

**Type 2:** (repeat for each service)
- [ ] Same information as above

**Type 3:** (e.g., "Group Workshop")
- [ ] Same information as above
- [ ] **Maximum participants:** ___ people
- [ ] **Group pricing:** $___

#### Cancellation Policy:
- [ ] **Cancellation deadline:** ___ hours before session
- [ ] **Refund policy:**
  - Full refund if canceled ___+ hours before
  - 50% refund if canceled ___-___ hours before
  - No refund if canceled less than ___ hours before
- [ ] **Rescheduling policy:** (allowed/not allowed, how many times)

---

### 4. **Availability & Calendar** 🔴 CRITICAL

#### General Availability:
Mark available times (in mentor's local time zone):

**Monday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

**Tuesday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

**Wednesday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

**Thursday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

**Friday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

**Saturday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

**Sunday:**
- [ ] Available: Yes / No
- Times: __:__ AM/PM to __:__ AM/PM

#### Calendar Integration:
- [ ] **Primary calendar:** Google Calendar / Outlook / Apple Calendar / Other
- [ ] **Google Calendar email:** ________________@gmail.com
- [ ] **Microsoft account email:** ________________@outlook.com
- [ ] **Grant calendar access:** (mentor must authorize during setup)

#### Booking Settings:
- [ ] **Time zone:** (e.g., "Europe/Kyiv", "America/New_York")
- [ ] **Buffer time between bookings:** ___ minutes
- [ ] **Advance booking limit:** ___ days ahead
- [ ] **Same-day bookings allowed:** Yes / No

---

### 5. **Digital Products** 🟡 HIGH PRIORITY

For each digital product:

**Product 1:**
- [ ] **Product name**
- [ ] **Category:** Course / eBook / Template / Video / Other: _______
- [ ] **Description:** (detailed, what customer will get)
- [ ] **Price:** $___ USD
- [ ] **File(s) to upload:**
  - File name: ____________
  - File type: PDF / Video (MP4) / Audio / ZIP / Other
  - File size: ___ MB/GB
- [ ] **Preview/sample:** (optional, for customers to see before buying)
- [ ] **Delivery method:** 
  - [ ] Instant download after purchase
  - [ ] Email delivery
  - [ ] Access to online portal

**Product 2:** (repeat for each product)
- Same information as above

#### Product Settings:
- [ ] **Allow refunds:** Yes / No
  - If yes, within ___ days
  - Conditions: _________________
- [ ] **Product updates:** Will you provide updates? Yes / No
- [ ] **Support included:** Email support / No support / Community forum

---

### 6. **AI Avatar Configuration** 🟡 HIGH PRIORITY

#### Knowledge Base Content:
Upload materials for AI avatar training:

- [ ] **About you:** Biography, credentials, experience (200-500 words)
- [ ] **Teaching philosophy:** Your approach and methods
- [ ] **Frequently asked questions:** List of common questions + answers
- [ ] **Product knowledge:** Detailed info about each digital product/service
- [ ] **Sample conversations:** Examples of how you'd answer questions
- [ ] **Additional resources:**
  - [ ] Blog posts / articles you've written
  - [ ] Transcripts from previous consultations (anonymized)
  - [ ] Course outlines or curricula
  - [ ] Presentation slides

#### Avatar Personality Settings:
- [ ] **Tone:** Professional / Friendly / Casual / Formal / Mix
- [ ] **Communication style:**
  - [ ] Direct and concise
  - [ ] Detailed and thorough
  - [ ] Conversational
  - [ ] Academic/Technical
- [ ] **Language(s) avatar should support:**
  - [ ] English
  - [ ] Ukrainian
  - [ ] Russian
  - [ ] Spanish
  - [ ] Other: __________

#### Avatar Limitations:
- [ ] **Topics avatar should NOT discuss:** _________________
- [ ] **Disclaimer text:** (e.g., "This is an AI assistant. For detailed advice, book a consultation.")
- [ ] **Conversation limits:**
  - [ ] Max ___ messages per user per day
  - [ ] Max ___ characters per response
- [ ] **When to refer to human mentor:** (e.g., "Complex technical questions", "Pricing negotiations")

#### Voice Settings (Optional):
- [ ] **Enable voice responses:** Yes / No
- [ ] **Voice type:** Male / Female / Neutral
- [ ] **Voice sample:** (upload 30-60 second audio of your voice for cloning)
- [ ] **Accent/language:** _________________

---

### 7. **Content Localization Preferences** 🟡 HIGH PRIORITY

#### Languages to Support:
Which languages should your content be available in?

- [ ] **English** (original)
- [ ] **Ukrainian**
- [ ] **Russian**
- [ ] **Spanish**
- [ ] **French**
- [ ] **German**
- [ ] **Polish**
- [ ] **Portuguese**
- [ ] Other: __________

#### Translation Preferences:
- [ ] **Review translations before publishing:** Yes / No
  - If yes, who will review? _________________
- [ ] **Technical terms dictionary:** (list terms that should NOT be translated)
  - Example: "Machine Learning" → keep in English, don't translate
  - Term 1: _________________
  - Term 2: _________________
- [ ] **Cultural adaptation:** Allow content adaptation for different cultures? Yes / No

#### Format Conversion Preferences:
Which formats should be generated from your content?

For **Video content**, create:
- [ ] Text transcript (searchable document)
- [ ] PDF guide (formatted document)
- [ ] Presentation slides (key points extracted)
- [ ] Audio-only version (MP3)
- [ ] Subtitles/captions file (SRT)

For **Text content** (eBooks, guides), create:
- [ ] PDF (formatted)
- [ ] EPUB (e-reader format)
- [ ] Audio version (text-to-speech)
- [ ] Presentation slides
- [ ] Summary/cheat sheet

Pricing for different formats:
- [ ] **Same price for all formats** (bundle)
- [ ] **Different pricing:**
  - Video: $___ 
  - Text: $___
  - Audio: $___
  - Presentation: $___

---

### 8. **Communication & Notifications** 📧

#### Contact Information:
- [ ] **Email:** _________________ (for bookings, payments)
- [ ] **Phone:** _________________ (optional, for urgent notifications)
- [ ] **Preferred notification method:**
  - [ ] Email
  - [ ] SMS
  - [ ] In-app notifications only

#### Notification Preferences:
Which notifications do you want to receive?

- [ ] **New booking confirmed** (Email / SMS / In-app)
- [ ] **Booking canceled by user** (Email / SMS / In-app)
- [ ] **Booking approaching** (1 day before, 1 hour before)
- [ ] **Payment received** (Email / In-app)
- [ ] **New message from user** (Email / In-app)
- [ ] **Product purchased** (Email / In-app)
- [ ] **Review/rating received** (Email / In-app)
- [ ] **Monthly earnings report** (Email)

#### Booking Confirmation Settings:
- [ ] **Automatic confirmation:** Yes (instant) / No (manual approval)
- [ ] **Confirmation message template:** (customize the message sent to users)
  - Example: "Thank you for booking! I'm looking forward to our session. Here's what to prepare..."
- [ ] **Include in confirmation:**
  - [ ] Video call link (Zoom/Google Meet)
  - [ ] Phone number
  - [ ] Preparation instructions
  - [ ] Cancellation policy reminder

---

### 9. **Video Call Integration** 🎥

#### Video Platform Preference:
- [ ] **Zoom**
  - Zoom account email: _________________
  - Personal Meeting ID: _________________
  - OR: Generate unique link per booking
- [ ] **Google Meet**
  - Google account: _________________
  - Generate unique link per booking
- [ ] **Microsoft Teams**
  - Teams account: _________________
- [ ] **Other:** _________ (provide details)

#### Meeting Settings:
- [ ] **Waiting room:** Enabled / Disabled
- [ ] **Recording allowed:** Yes (with permission) / No
- [ ] **Screen sharing:** Enabled / Disabled

---

### 10. **Legal & Compliance** ⚖️

#### Terms & Policies:
- [ ] **Accept platform Terms of Service**
- [ ] **Accept payment processing terms** (Stripe)
- [ ] **Privacy policy acknowledgment**
- [ ] **Data handling consent** (customer data, recordings, etc.)

#### Content Rights:
- [ ] **Confirm you own rights to all uploaded content**
- [ ] **Grant platform license to:**
  - [ ] Host and distribute your content
  - [ ] Create translations
  - [ ] Create format conversions
  - [ ] Use for AI avatar training
  - [ ] Use excerpts for marketing (with attribution)

#### Tax Information:
- [ ] **Country of tax residence:** _________________
- [ ] **Tax ID / VAT number:** _________________
- [ ] **Tax exempt:** Yes / No
- [ ] **W-9 form** (US mentors) - to be provided
- [ ] **W-8BEN form** (Non-US mentors) - to be provided

---

### 11. **Marketing & Visibility** 📢

#### Profile Visibility:
- [ ] **Public profile:** Visible to all users
- [ ] **Searchable:** Appear in search results
- [ ] **Featured mentor:** (requires approval + fee)

#### Marketing Materials:
- [ ] **Professional headshot:** (high resolution, 1000x1000px min)
- [ ] **Intro video:** (30-60 seconds, optional but recommended)
- [ ] **Portfolio/work samples:** (links or uploads)
- [ ] **Testimonials:** (from previous clients, 3-5 recommended)
- [ ] **Certifications:** (copies of certificates, licenses)

#### Social Proof:
- [ ] **LinkedIn profile:** https://linkedin.com/in/_________
- [ ] **Personal website:** https://_________________
- [ ] **YouTube channel:** https://youtube.com/@_________
- [ ] **Other professional profiles:** _________________

---

### 12. **Additional Preferences** ⚙️

#### User Matching:
Help AI match you with right users:
- [ ] **Ideal client profile:** (who benefits most from your services)
- [ ] **Experience level you work with:**
  - [ ] Beginners
  - [ ] Intermediate
  - [ ] Advanced
  - [ ] All levels
- [ ] **Age group preference:** (if applicable)
- [ ] **Industry focus:** (if applicable)

#### Special Requirements:
- [ ] **Accessibility needs:** (e.g., provide captions, transcripts)
- [ ] **Content warnings:** (if your content discusses sensitive topics)
- [ ] **Prerequisites:** (what users should know/have before booking)

---

## 📋 Onboarding Checklist

Complete these steps during mentor onboarding:

### Step 1: Profile Setup (10 minutes)
- [ ] Fill out profile information
- [ ] Upload profile photo
- [ ] Write biography
- [ ] Add expertise tags

### Step 2: Payment Setup (15 minutes)
- [ ] Create/connect Stripe account
- [ ] Verify identity with Stripe
- [ ] Add bank account information
- [ ] Review and accept fee structure

### Step 3: Services Setup (20 minutes)
- [ ] Define consultation types
- [ ] Set pricing for each service
- [ ] Upload digital products (if applicable)
- [ ] Set cancellation policies

### Step 4: Calendar Setup (10 minutes)
- [ ] Connect Google/Outlook calendar
- [ ] Set weekly availability
- [ ] Configure booking buffer times
- [ ] Set time zone

### Step 5: AI Avatar Setup (30 minutes)
- [ ] Upload knowledge base content
- [ ] Configure avatar personality
- [ ] Test avatar responses
- [ ] Set conversation limits

### Step 6: Content Localization (Optional, 15 minutes)
- [ ] Select languages for translation
- [ ] Provide technical terms dictionary
- [ ] Choose format conversions
- [ ] Set pricing for formats

### Step 7: Communication Setup (5 minutes)
- [ ] Configure notification preferences
- [ ] Set up video call integration
- [ ] Customize confirmation messages

### Step 8: Legal & Compliance (10 minutes)
- [ ] Accept Terms of Service
- [ ] Confirm content ownership
- [ ] Provide tax information
- [ ] Sign mentor agreement

### Step 9: Review & Launch (5 minutes)
- [ ] Preview public profile
- [ ] Test booking flow
- [ ] Verify payment connection
- [ ] Activate profile

**Total Onboarding Time: ~2 hours**

---

## 📝 Data Collection Methods

### Option 1: Interactive Onboarding Wizard
Create step-by-step web form with sections above, saving progress automatically.

### Option 2: PDF Form + Manual Entry
Send PDF checklist, mentor fills out, admin enters into system.

### Option 3: Video Call + Screen Share
Schedule 30-minute onboarding call, collect info live, more personal.

**Recommendation: Option 1 (Interactive Wizard) + Option 3 (support call for complex setups)**

---

## 🎯 Priority Levels

### 🔴 Critical (Required to Go Live):
- Payment/payout information
- Consultation services and pricing
- Availability and calendar
- Basic profile information

### 🟡 High Priority (Needed Soon):
- Digital products
- AI avatar knowledge base
- Content localization preferences

### 🟢 Optional (Can Add Later):
- Voice for AI avatar
- Advanced format conversions
- Marketing materials beyond basics

---

## 📞 Support During Onboarding

Provide mentors with:
- [ ] **Email support:** support@gcreators.me
- [ ] **Video tutorials:** For each onboarding step
- [ ] **Live chat support:** During business hours
- [ ] **Onboarding checklist:** Printable PDF
- [ ] **FAQ document:** Common questions answered
- [ ] **Sample mentor profile:** To show best practices

---

**Document Status:** Ready for use  
**Last Updated:** February 20, 2026  
**Next Step:** Create interactive onboarding form based on this document
