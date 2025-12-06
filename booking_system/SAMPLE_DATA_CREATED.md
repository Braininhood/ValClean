# Sample Data Created ✅

## Overview
Sample data has been successfully created for the booking system based on VALclean services from [https://valclean.uk/booking/](https://valclean.uk/booking/).

## 📊 Created Data Summary

### Categories (3)
1. **Cleaning Services** - Professional cleaning services for your home
2. **Maintenance Services** - Handyman and maintenance services
3. **Green Spaces** - Garden and outdoor maintenance

### Services (7)
Based on VALclean website services:

1. **Basic Home Cleaning** - £45.00
   - Duration: 2 hours (120 minutes)
   - Category: Cleaning Services
   - Description: Standard home cleaning service including dusting, vacuuming, mopping, and bathroom cleaning.

2. **Duo Automatic Home Cleaning Service** - £85.00
   - Duration: 3 hours (180 minutes)
   - Category: Cleaning Services
   - Description: Premium cleaning service with two cleaners for faster and more thorough cleaning.

3. **Post Renovation Cleaning** - £120.00
   - Duration: 4 hours (240 minutes)
   - Category: Cleaning Services
   - Description: Deep cleaning service after renovation work, including dust removal and thorough sanitization.

4. **Move In/Out Service** - £150.00
   - Duration: 5 hours (300 minutes)
   - Category: Cleaning Services
   - Description: Comprehensive cleaning service for moving in or out of a property.

5. **Window Cleaning** - £35.00
   - Duration: 1.5 hours (90 minutes)
   - Category: Cleaning Services
   - Description: Professional window cleaning service for interior and exterior windows.

6. **Handyman Service** - £60.00
   - Duration: 2 hours (120 minutes)
   - Category: Maintenance Services
   - Description: General handyman services including repairs, installations, and maintenance tasks.

7. **Green Spaces Maintenance** - £70.00
   - Duration: 3 hours (180 minutes)
   - Category: Green Spaces
   - Description: Garden maintenance including mowing, trimming, weeding, and general garden care.

### Staff Members (3)

1. **Sarah Johnson**
   - Email: sarah.johnson@valclean.uk
   - Phone: 07493465560
   - Specializes in: Cleaning services (all types)
   - Schedule: Monday-Friday, 9:00 AM - 8:00 PM (with 1-hour lunch break 1-2 PM)
   - Bio: Experienced cleaning professional with 5+ years in the industry. Specializes in deep cleaning and post-renovation services.

2. **Michael Brown**
   - Email: michael.brown@valclean.uk
   - Phone: 07493465561
   - Specializes in: Handyman and Green Spaces services
   - Schedule: Monday-Friday, 9:00 AM - 8:00 PM (with 1-hour lunch break 1-2 PM)
   - Bio: Skilled handyman and maintenance specialist. Expert in repairs, installations, and garden maintenance.

3. **Emma Wilson**
   - Email: emma.wilson@valclean.uk
   - Phone: 07493465562
   - Specializes in: All cleaning services
   - Schedule: Monday-Friday, 9:00 AM - 8:00 PM (with 1-hour lunch break 1-2 PM)
   - Bio: Professional cleaner specializing in regular home cleaning and window cleaning services.

### Users & Customers (3)

1. **John Smith**
   - Username: `john_smith`
   - Email: john.smith@example.com
   - Password: `testpass123`
   - Phone: 07493465570
   - Address: 12 Oak Tree Road, Yelverton, Devon, PL20 6BN
   - Role: Customer

2. **Mary Jones**
   - Username: `mary_jones`
   - Email: mary.jones@example.com
   - Password: `testpass123`
   - Phone: 07493465571
   - Address: 45 High Street, Yelverton, Devon, PL20 7AB
   - Role: Customer

3. **David Taylor**
   - Username: `david_taylor`
   - Email: david.taylor@example.com
   - Password: `testpass123`
   - Phone: 07493465572
   - Address: 8 Meadow View, Near the Park, Yelverton, Devon, PL20 8CD
   - Role: Customer

### Appointments (5)

1. **John Smith - Basic Home Cleaning**
   - Staff: Sarah Johnson
   - Date: 2 days from now at 10:00 AM
   - Status: Approved
   - Service: Basic Home Cleaning (£45.00)

2. **Mary Jones - Window Cleaning**
   - Staff: Emma Wilson
   - Date: 3 days from now at 2:00 PM
   - Status: Pending
   - Service: Window Cleaning (£35.00)

3. **David Taylor - Handyman Service**
   - Staff: Michael Brown
   - Date: 5 days from now at 9:00 AM
   - Status: Approved
   - Service: Handyman Service (£60.00)

4. **John Smith - Duo Automatic Home Cleaning Service**
   - Staff: Sarah Johnson
   - Date: 7 days from now at 11:00 AM
   - Status: Pending
   - Service: Duo Automatic Home Cleaning Service (£85.00)

5. **Mary Jones - Basic Home Cleaning**
   - Staff: Emma Wilson
   - Date: 10 days from now at 1:00 PM
   - Status: Approved
   - Service: Basic Home Cleaning (£45.00)

## 🔧 How to Use

### Run the Command
```bash
python manage.py create_sample_data
```

### Login as Test Users
You can now login with any of the created users:
- Username: `john_smith`, `mary_jones`, or `david_taylor`
- Password: `testpass123`

### Access the Booking System
1. Go to: `/appointments/booking/`
2. Select a service
3. Choose a staff member (or "Any Available")
4. Select date and time
5. Complete the booking

### View Data in Admin
1. Go to: `/admin/`
2. Login as superuser
3. Browse:
   - Services → See all 7 services
   - Staff → See all 3 staff members
   - Customers → See all 3 customers
   - Appointments → See all 5 appointments

## 📍 Location Information

All sample data is based on VALclean's service area:
- **Location**: Yelverton, Devon, UK
- **Phone**: 07493465559
- **Hours**: 9:00 AM - 8:00 PM (Monday-Friday)

## 🎯 Testing Scenarios

### Test Booking Flow
1. Login as `john_smith` (password: `testpass123`)
2. Go to booking page
3. Select "Basic Home Cleaning"
4. Choose "Sarah Johnson" or "Any Available"
5. Select a date (should show available slots)
6. Complete booking

### Test Staff Schedules
- All staff work Monday-Friday, 9 AM - 8 PM
- Lunch break: 1:00 PM - 2:00 PM
- No weekend availability (for testing)

### Test Time Slot Calculation
- Minimum booking time: 2 hours before appointment
- Maximum advance booking: 90 days
- Slot length: 15 minutes

## 📝 Notes

- All services are active and public
- All staff members are active and public
- Staff schedules are set for Monday-Friday only
- Appointments are created with various statuses (Pending/Approved)
- Customer addresses are in Yelverton, Devon area
- Prices match VALclean website pricing structure

## 🔄 Re-running the Command

The command uses `get_or_create()`, so it's safe to run multiple times:
- Existing data won't be duplicated
- New data will be created if it doesn't exist
- Useful for resetting test data

---

**Status**: ✅ Sample Data Created Successfully
**Date**: December 2025
**Based on**: [VALclean Booking System](https://valclean.uk/booking/)

