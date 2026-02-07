# Google Maps API Setup - Complete ✅

## API Key Configuration

**⚠️ SECURITY:** API keys should NEVER be committed to git. Always use environment variables.

**Location:** `backend/.env` (gitignored - not committed to repository)

**Setup:**
1. Add your Google Maps API key to `backend/.env`:
   ```env
   GOOGLE_MAPS_API_KEY=your_api_key_here
   GOOGLE_PLACES_API_KEY=your_api_key_here
   ```
2. The same API key works for both Geocoding API and Places API
3. Never commit the `.env` file to version control

---

## Configuration

### Settings (`backend/config/settings/base.py`)

The settings now support both `GOOGLE_MAPS_API_KEY` and `GOOGLE_PLACES_API_KEY` with automatic fallback:

```python
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default='')
GOOGLE_PLACES_API_KEY = env('GOOGLE_PLACES_API_KEY', default='')

# Automatic fallback: if one is set but not the other, use the same key
if not GOOGLE_PLACES_API_KEY and GOOGLE_MAPS_API_KEY:
    GOOGLE_PLACES_API_KEY = GOOGLE_MAPS_API_KEY
if not GOOGLE_MAPS_API_KEY and GOOGLE_PLACES_API_KEY:
    GOOGLE_MAPS_API_KEY = GOOGLE_PLACES_API_KEY
```

**Why both?** The same API key works for both:
- **Geocoding API** (for postcode geocoding) - uses `GOOGLE_MAPS_API_KEY`
- **Places API** (for address autocomplete) - uses `GOOGLE_PLACES_API_KEY`

---

## What It's Used For

### 1. Postcode Geocoding (`geocode_postcode()`)
Converts UK postcodes to latitude/longitude coordinates.

**Location:** `backend/apps/core/address.py`

**Usage:**
```python
from apps.core.address import geocode_postcode

result = geocode_postcode('SW1A 1AA')
# Returns:
# {
#     'lat': 51.4994,
#     'lng': -0.1246,
#     'formatted_address': 'Westminster, London SW1A 1AA, UK',
#     'valid': True,
#     'components': {
#         'postal_code': 'SW1A 1AA',
#         'town': 'London',
#         'county': 'Greater London',
#         'country': 'GB'
#     }
# }
```

### 2. Address Autocomplete (`get_address_autocomplete()`)
Provides address suggestions as user types.

**Location:** `backend/apps/core/address.py`

**Usage:**
```python
from apps.core.address import get_address_autocomplete

suggestions = get_address_autocomplete('SW1A 1')
# Returns list of address predictions with place_id and description
```

### 3. Postcode Validation (`validate_postcode_with_google()`)
Validates UK postcode format AND verifies it exists.

**Location:** `backend/apps/core/address.py`

**Usage:**
```python
from apps.core.address import validate_postcode_with_google

result = validate_postcode_with_google('SW1A 1AA')
# Returns validation result with coordinates and formatted address
```

---

## Testing

### Test in Django Shell

```bash
cd backend
python manage.py shell
```

```python
from apps.core.address import geocode_postcode, validate_postcode_with_google

# Test geocoding
result = geocode_postcode('SW1A 1AA')
print(result)
# Should return coordinates and formatted address

# Test validation
validation = validate_postcode_with_google('SW1A 1AA')
print(validation)
# Should return {'valid': True, ...}
```

### Test API Endpoints

Once API endpoints are created (Week 3 Day 1-2):
- `POST /api/bkg/services-by-postcode/` - Will use geocoding to find services
- `POST /api/bkg/staff-by-postcode/` - Will use geocoding to find staff

---

## Google Cloud Console Setup

### Required APIs

Make sure these APIs are enabled in your Google Cloud project:

1. **Geocoding API**
   - Used for: Postcode → coordinates conversion
   - Status: ✅ Enabled

2. **Places API** (or **Places API (New)**)
   - Used for: Address autocomplete suggestions
   - Status: ✅ Enabled

### API Key Restrictions (Recommended)

**For Development:**
- IP restrictions: `0.0.0.0/0` (allow all IPs)
- Or specific: `127.0.0.1/32`, `localhost`

**For Production:**
- HTTP referrer restrictions: `https://valclean.uk/*`
- API restrictions: Only allow Geocoding API and Places API
- Do NOT allow all APIs

---

## Security Notes

⚠️ **Important:**
- The `.env` file is gitignored - API key is NOT committed to repository
- Never commit API keys to version control
- Use environment variables in production
- Restrict API key to specific domains/IPs in production
- Monitor API usage in Google Cloud Console

---

## Next Steps

1. ✅ API key added to `.env`
2. ✅ Settings configured
3. ⏳ **Restart Django server** to load new environment variables
4. ⏳ Test postcode geocoding
5. ⏳ Create API endpoints for postcode-based services/staff lookup

---

## Troubleshooting

### API Key Not Working?

1. **Check API key is set:**
   ```python
   from django.conf import settings
   print(settings.GOOGLE_MAPS_API_KEY)
   ```

2. **Check APIs are enabled:**
   - Go to Google Cloud Console
   - Navigate to "APIs & Services" → "Enabled APIs"
   - Verify Geocoding API and Places API are enabled

3. **Check API key restrictions:**
   - If IP restrictions are set, make sure your IP is allowed
   - If HTTP referrer restrictions are set, make sure your domain is allowed

4. **Test with curl:**
   ```bash
   curl "https://maps.googleapis.com/maps/api/geocode/json?address=SW1A+1AA&components=country:GB&key=YOUR_API_KEY"
   ```

---

## Files Modified

- ✅ `backend/.env` - API key added (gitignored)
- ✅ `backend/env.example` - Template updated with GOOGLE_MAPS_API_KEY
- ✅ `backend/config/settings/base.py` - Settings updated with fallback logic
- ✅ `backend/apps/core/address.py` - Already configured to use both keys

---

## Summary

✅ Google Maps API key configured and ready to use
✅ Supports both Geocoding API and Places API
✅ Automatic fallback between GOOGLE_MAPS_API_KEY and GOOGLE_PLACES_API_KEY
✅ Ready for Week 3: Basic Booking Flow implementation

**Status:** Ready to use! 🚀
