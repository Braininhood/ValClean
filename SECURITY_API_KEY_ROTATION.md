# ⚠️ SECURITY ALERT: API Key Exposure

## Issue

A Google Maps API key was exposed in commit `4a1200e` in the file `GOOGLE_MAPS_API_SETUP.md`.

**Exposed Key:** `AIzaSyCHEjIDd9JI0xMOXyp7WILxeFvwUsB---0`

---

## ✅ Immediate Actions Taken

1. ✅ Removed API key from documentation
2. ✅ Updated documentation with placeholder
3. ✅ Verified `.env` file is gitignored
4. ✅ Committed security fix

---

## 🔒 Required Actions

### 1. Rotate the API Key (CRITICAL)

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Credentials"
3. Find the exposed API key: `AIzaSyCHEjIDd9JI0xMOXyp7WILxeFvwUsB---0`
4. **Delete/Revoke** the old key
5. Create a new API key
6. Update `backend/.env` with the new key:
   ```env
   GOOGLE_MAPS_API_KEY=new_api_key_here
   GOOGLE_PLACES_API_KEY=new_api_key_here
   ```

### 2. Secure the New API Key

**Restrictions to Add:**
- **API Restrictions:** Only allow:
  - Geocoding API
  - Places API
- **Application Restrictions:**
  - **Development:** IP restrictions (your development IPs)
  - **Production:** HTTP referrer restrictions: `https://valclean.uk/*`

### 3. Monitor Usage

- Check Google Cloud Console for any unauthorized usage
- Set up billing alerts
- Monitor API usage patterns

---

## 📋 Prevention Checklist

- [x] `.env` file is in `.gitignore`
- [x] `env.example` uses placeholders only
- [x] Documentation uses placeholders
- [x] No API keys in code files
- [x] No API keys in commit messages
- [ ] API key rotated (ACTION REQUIRED)
- [ ] New key has restrictions applied (ACTION REQUIRED)

---

## 🔍 How to Check for Exposed Secrets

```bash
# Search for potential API keys in git history
git log --all --full-history -p | grep -i "AIzaSy"

# Search for API keys in current files
grep -r "AIzaSy" --exclude-dir=venv --exclude-dir=node_modules .
```

---

## 📝 Best Practices

1. **Never commit API keys to git**
2. **Use environment variables** for all secrets
3. **Use `.env.example`** with placeholders
4. **Review commits** before pushing
5. **Use git-secrets** or similar tools to prevent commits
6. **Rotate keys immediately** if exposed

---

## ⚠️ Current Status

- ✅ Documentation fixed
- ⚠️ **API key rotation required** - Old key must be revoked
- ⚠️ **New key must be generated** and added to `.env`

**Action Required:** Rotate the Google Maps API key immediately.
