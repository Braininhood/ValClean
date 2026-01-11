# Week 3: Basic Booking Flow - Setup Complete

## ✅ What's Been Created

### 1. Sample Data Command

**Location:** `backend/apps/services/management/commands/create_week3_sample_data.py`

**Purpose:** Creates comprehensive sample data for testing Week 3 booking flow features.

**Creates:**
- ✅ 3 Categories (Cleaning Services, Maintenance Services, Green Spaces)
- ✅ 6 Services with different durations and prices
- ✅ 3 Staff members with profiles
- ✅ Staff schedules (Monday-Friday, 9am-5pm with lunch breaks)
- ✅ Staff service area assignments (postcodes with radius)
- ✅ Sample appointments for next week
- ✅ Staff-service assignments

**Usage:**
```bash
# Create sample data
cd backend
python manage.py create_week3_sample_data

# Clear and recreate sample data
python manage.py create_week3_sample_data --clear
```

**Test Postcodes:**
- `SW1A 1AA` (Westminster, London) - All staff
- `W1A 0AX` (West End, London) - John Smith
- `N1 9GU` (Islington, London) - Sarah Johnson
- `E1 6AN` (Whitechapel, London) - Mike Davis

---

### 2. Enhanced UK Postcode Validation with Google Maps API

**Location:** `backend/apps/core/address.py`

**Features:**
- ✅ **UK Postcode Format Validation** - Validates format using regex
- ✅ **Google Maps Geocoding** - Verifies postcode existence and gets coordinates
- ✅ **Address Autocomplete** - Google Places API integration for address suggestions
- ✅ **Postcode Validation Function** - `validate_postcode_with_google()` that combines format + API validation

**Functions Available:**

#### `geocode_postcode(postcode)`
Geocodes a UK postcode to get latitude, longitude, and formatted address.

**Returns:**
```python
{
    'lat': float,
    'lng': float,
    'formatted_address': str,
    'valid': bool,
    'components': {
        'postal_code': str,
        'town': str,
        'county': str,
        'country': str,
    }
}
```

#### `get_address_autocomplete(query)`
Gets address suggestions using Google Places API.

**Returns:**
```python
[
    {
        'place_id': str,
        'description': str,
        'structured_formatting': dict,
        'types': list,
    }
]
```

#### `validate_postcode_with_google(postcode)`
Validates UK postcode format AND verifies with Google Maps API.

**Returns:**
```python
{
    'valid': bool,
    'formatted': str,
    'lat': float or None,
    'lng': float or None,
    'formatted_address': str or None,
    'components': dict,
}
```

---

## 🔧 Google Maps API Setup

### Required Settings

Add to `backend/.env` or Django settings:

```env
# Google Maps API Key (required for geocoding and autocomplete)
GOOGLE_MAPS_API_KEY=your_api_key_here
# OR
GOOGLE_PLACES_API_KEY=your_api_key_here

# Note: Both settings are checked, use whichever you prefer
```

### Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable APIs:
   - **Geocoding API** (for postcode geocoding)
   - **Places API** (for address autocomplete)
   - **Places API (New)** (recommended for new projects)
4. Create API Key:
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Restrict key to specific APIs (Geocoding, Places)
   - Add HTTP referrer restrictions for production

### API Key Restrictions (Recommended)

**For Development:**
- Allow all IPs: `0.0.0.0/0`
- Or specific localhost: `127.0.0.1/32`

**For Production:**
- Restrict to your domain: `https://valclean.uk/*`
- Restrict to specific APIs only

---

## 📋 UK Postcode Validation

### Format Rules

UK postcodes follow this format:
- **Format:** `[A-Z]{1,2}[0-9R][0-9A-Z]?\s?[0-9][ABD-HJLNP-UW-Z]{2}`
- **Examples:**
  - `SW1A 1AA` (Westminster)
  - `M1 1AA` (Manchester)
  - `B33 8TH` (Birmingham)
  - `W1A 0AX` (West End)

### Validation Levels

1. **Format Only** (No API key required)
   - Uses regex pattern
   - Validates format correctness
   - Returns formatted postcode (uppercase)

2. **Format + Existence** (API key required)
   - Validates format
   - Verifies postcode exists via Google Maps API
   - Gets coordinates and formatted address
   - More secure and accurate

### Usage Examples

**Backend (Django):**
```python
from apps.core.address import validate_postcode_with_google, geocode_postcode
from apps.core.validators import validate_uk_postcode

# Format validation only (no API needed)
try:
    formatted = validate_uk_postcode('sw1a 1aa')
    print(formatted)  # 'SW1A 1AA'
except ValidationError as e:
    print(e)

# Format + Google Maps validation (API key needed)
result = validate_postcode_with_google('SW1A 1AA')
if result['valid']:
    print(f"Valid postcode: {result['formatted']}")
    print(f"Coordinates: {result['lat']}, {result['lng']}")
    print(f"Address: {result['formatted_address']}")

# Geocode postcode
geo_result = geocode_postcode('SW1A 1AA')
if geo_result and geo_result.get('valid'):
    lat = geo_result['lat']
    lng = geo_result['lng']
```

**Frontend (React/Next.js):**
```typescript
import { validateUKPostcode, formatPostcode } from '@/lib/utils'

// Format and validate postcode
const postcode = 'sw1a 1aa'
const formatted = formatPostcode(postcode)  // 'SW1A 1AA'
const isValid = validateUKPostcode(formatted)  // true
```

---

## 🧪 Testing Week 3 Features

### 1. Create Sample Data

```bash
cd backend
python manage.py create_week3_sample_data
```

### 2. Test Postcode Validation

**Test URLs:**
- `http://localhost:3000/booking/postcode` (Frontend postcode entry)
- `http://localhost:8000/api/bkg/services-by-postcode/` (Backend API)

**Test Postcodes:**
- ✅ Valid: `SW1A 1AA`, `W1A 0AX`, `N1 9GU`, `E1 6AN`
- ❌ Invalid: `12345`, `ABC`, `SW1A` (incomplete)

### 3. Test Staff/Service Filtering by Postcode

The sample data includes:
- **John Smith** - Covers `SW1A 1AA` (15km) and `W1A 0AX` (10km)
- **Sarah Johnson** - Covers `SW1A 1AA` (20km) and `N1 9GU` (15km)
- **Mike Davis** - Covers `SW1A 1AA` (25km) and `E1 6AN` (20km)

**Test Scenario:**
1. Enter postcode `SW1A 1AA`
2. Should see services available from all 3 staff members
3. Services should be filtered by staff who cover that postcode area

---

## 📝 Next Steps (Week 3 Day 1-2)

Now that sample data is ready, you can:

1. ✅ **Test Postcode Entry UI** (`/booking/postcode`)
   - Validate postcode format
   - Store postcode in booking state

2. ✅ **Create API Endpoint: Get Services by Postcode**
   - Filter services by staff who cover the postcode area
   - Use `StaffArea` model to find staff in range
   - Return available services

3. ✅ **Create API Endpoint: Get Staff by Postcode**
   - Find staff members who cover the postcode area
   - Calculate distance (optional - can use radius_km for now)
   - Return available staff

4. ✅ **Implement Postcode-to-Area Mapping Logic**
   - Use Google Maps API to get postcode coordinates
   - Match against `StaffArea` entries
   - Filter by radius_km

---

## 🎯 API Endpoints Needed

### GET /api/bkg/services-by-postcode/
**Request:**
```json
{
  "postcode": "SW1A 1AA"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "postcode": "SW1A 1AA",
    "services": [
      {
        "id": 1,
        "name": "Window Cleaning",
        "category": "Cleaning Services",
        "price": "35.00",
        "duration": 60,
        "available_staff": [
          {"id": 1, "name": "John Smith"}
        ]
      }
    ]
  }
}
```

### GET /api/bkg/staff-by-postcode/
**Request:**
```json
{
  "postcode": "SW1A 1AA"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "postcode": "SW1A 1AA",
    "staff": [
      {
        "id": 1,
        "name": "John Smith",
        "services": [
          {"id": 1, "name": "Window Cleaning"}
        ],
        "service_area": {
          "postcode": "SW1A 1AA",
          "radius_km": "15.00"
        }
      }
    ]
  }
}
```

---

## ✅ Checklist

- [x] Sample data command created
- [x] UK postcode format validation (backend)
- [x] UK postcode format validation (frontend)
- [x] Google Maps API geocoding integration
- [x] Google Places API autocomplete integration
- [x] Postcode validation with Google Maps API
- [ ] API endpoint: Get services by postcode
- [ ] API endpoint: Get staff by postcode
- [ ] Postcode-to-area mapping logic
- [ ] Service filtering by area
- [ ] Navigation to service selection

---

## 📚 References

- [UK Postcode Format](https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom)
- [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding)
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service)
- [Week 3 Roadmap](./IMPLEMENTATION_ROADMAP.md#week-3-basic-booking-flow)
