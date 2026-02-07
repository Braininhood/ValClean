# Google Maps API Key Setup - REQUIRED for Address Autocomplete

## ⚠️ IMPORTANT: API Key Not Configured

The address autocomplete feature requires a Google Maps API key. Currently, **the API key is not configured**, which is why autocomplete isn't working.

## Quick Setup Steps:

### 1. Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable these APIs:
   - **Places API** (required for autocomplete)
   - **Geocoding API** (required for postcode validation)
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### 2. Add API Key to Backend

1. Open `backend/.env` file (create it if it doesn't exist)
2. Add this line:
   ```env
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```
   OR
   ```env
   GOOGLE_PLACES_API_KEY=your_api_key_here
   ```

3. **Restart the Django server** for changes to take effect

### 3. Verify Setup

After adding the API key and restarting the server, the autocomplete should work.

## Testing

1. Open the booking details page
2. Type a postcode like "SW1A 1AA" in the search field
3. You should see address suggestions appear

## Troubleshooting

### Still not working?

1. **Check API key is set:**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development'); import django; django.setup(); from django.conf import settings; print('API Key:', bool(getattr(settings, 'GOOGLE_MAPS_API_KEY', None)))"
   ```

2. **Check APIs are enabled:**
   - Go to Google Cloud Console
   - Navigate to "APIs & Services" → "Enabled APIs"
   - Verify "Places API" and "Geocoding API" are enabled

3. **Check API key restrictions:**
   - If you set IP restrictions, make sure your IP is allowed
   - For development, you can temporarily remove restrictions

4. **Check browser console:**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab to see if API calls are being made

## Security Notes

- ⚠️ **Never commit the `.env` file to git** (it's already in .gitignore)
- For production, use environment variables or a secrets manager
- Restrict API key to specific domains/IPs in production

## Cost

- Google Maps API has a free tier (usually $200/month credit)
- Autocomplete requests cost ~$2.83 per 1000 requests
- Geocoding requests cost ~$5.00 per 1000 requests
- For development/testing, you should stay well within the free tier

---

**Status:** ⚠️ API Key Required - Add to `backend/.env` and restart server
