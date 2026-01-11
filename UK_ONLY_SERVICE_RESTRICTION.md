# UK-Only Service Restriction

## Overview

VALClean booking system is **restricted to UK postcodes only**. The system validates that postcodes are actually in the UK and shows clear messaging to users.

---

## Implementation

### Backend Validation

**Location:** `backend/apps/core/address.py`

#### `geocode_postcode(postcode)`
- ✅ Restricts Google Maps API to `country:GB` (UK only)
- ✅ Validates country code is `GB` in geocoding results
- ✅ Returns `is_uk: bool` flag in response
- ✅ Rejects postcodes that are not in the UK

**Response Format:**
```python
{
    'lat': float,
    'lng': float,
    'formatted_address': str,
    'valid': bool,  # Only True if UK
    'is_uk': bool,  # Explicit UK flag
    'country_code': str,  # 'GB' for UK
    'components': dict,
}
```

#### `validate_postcode_with_google(postcode)`
- ✅ Validates UK postcode format first
- ✅ Verifies postcode is in UK using Google Maps API
- ✅ Returns clear error messages for non-UK postcodes
- ✅ Error messages mention: "VALClean currently operates only in the UK"

**Error Messages:**
- Invalid format: `"Invalid UK postcode format. VALClean currently operates only in the UK."`
- Non-UK postcode: `"This postcode is not in the UK. VALClean currently operates only in the UK. Please enter a UK postcode."`
- Not found: `"Postcode not found. VALClean currently operates only in the UK. Please enter a valid UK postcode."`

---

### Frontend UI

**Location:** `frontend/app/booking/postcode/page.tsx`

#### Visual Indicators:
1. **Page Header:**
   - Title: "Book Your Service"
   - Subtitle: "Enter your UK postcode to see available services in your area"
   - **UK-Only Notice:** Blue banner with flag emoji: "🇬🇧 VALClean currently operates only in the UK"

2. **Input Field:**
   - Placeholder: "e.g., SW1A 1AA"
   - Help text: "We'll show you services available in your UK area"

3. **Error Messages:**
   - Format validation: "Please enter a valid UK postcode (e.g., SW1A 1AA). VALClean currently operates only in the UK."

---

## Google Maps API Configuration

### API Restrictions

All Google Maps API calls are restricted to UK:

1. **Geocoding API:**
   ```python
   params = {
       'address': postcode,
       'components': 'country:GB',  # UK only
       'key': api_key,
   }
   ```

2. **Places API (Autocomplete):**
   ```python
   params = {
       'input': query,
       'components': 'country:gb',  # UK only
       'types': '(regions)',
       'key': api_key,
   }
   ```

---

## Validation Flow

### Step 1: Format Validation
- Checks if postcode matches UK postcode format regex
- Pattern: `^[A-Z]{1,2}[0-9R][0-9A-Z]?\s?[0-9][ABD-HJLNP-UW-Z]{2}$`
- Examples: `SW1A 1AA`, `M1 1AA`, `B33 8TH`

### Step 2: Country Validation (Google Maps API)
- Geocodes postcode using Google Maps API
- Checks `country_code` in response
- Only accepts if `country_code == 'GB'`
- Rejects all other countries

### Step 3: Error Handling
- If format invalid → Show format error
- If format valid but not UK → Show UK-only message
- If not found → Show not found + UK-only message

---

## User Experience

### Valid UK Postcode
1. User enters: `SW1A 1AA`
2. System validates format ✅
3. System geocodes and checks country ✅
4. Country is `GB` ✅
5. User proceeds to service selection ✅

### Invalid Format
1. User enters: `12345`
2. System validates format ❌
3. Error shown: "Please enter a valid UK postcode (e.g., SW1A 1AA). VALClean currently operates only in the UK."

### Non-UK Postcode (if format matches)
1. User enters: `90210` (US ZIP code - but might match UK format)
2. System validates format ✅
3. System geocodes and checks country ❌
4. Country is not `GB` ❌
5. Error shown: "This postcode is not in the UK. VALClean currently operates only in the UK. Please enter a UK postcode."

---

## Testing

### Test UK Postcodes (Should Work)
- `SW1A 1AA` - Westminster, London
- `W1A 0AX` - West End, London
- `N1 9GU` - Islington, London
- `E1 6AN` - Whitechapel, London
- `M1 1AA` - Manchester
- `B33 8TH` - Birmingham

### Test Non-UK (Should Reject)
- Any postcode that geocodes to a country other than GB
- Invalid formats

---

## Future Enhancements

When expanding to other countries:
1. Add `country` parameter to validation functions
2. Update Google Maps API `components` parameter
3. Update UI messaging to show available countries
4. Add country selector in booking flow

---

## Files Modified

- ✅ `backend/apps/core/address.py` - Added UK country validation
- ✅ `frontend/app/booking/postcode/page.tsx` - Added UK-only messaging
- ✅ Google Maps API calls restricted to `country:GB`

---

## Summary

✅ **System is restricted to UK postcodes only**
✅ **Clear messaging: "VALClean currently operates only in the UK"**
✅ **Google Maps API validates country is GB**
✅ **Error messages guide users to enter UK postcodes**
✅ **User-friendly UI with UK flag indicator**

**Status:** Fully implemented and ready for use! 🇬🇧
