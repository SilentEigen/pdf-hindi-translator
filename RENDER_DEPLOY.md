# Render.com Deployment Guide

## Quick Deploy to Render.com (FREE)

### Step 1: Push Code to GitHub

```bash
cd "/Users/gobindkumar/Documents/My Projects/PDF Hinglish Converter"

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit - PDF Hindi Translator"

# Create a new GitHub repo at https://github.com/new
# Then connect it:
git remote add origin https://github.com/YOUR_USERNAME/pdf-hindi-translator.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. **Go to:** https://render.com
2. **Sign up** with your GitHub account (free)
3. Click **"New +"** → **"Web Service"**
4. **Connect your GitHub repo:** `pdf-hindi-translator`
5. **Configure:**
   - **Name:** `pdf-hindi-translator-api`
   - **Root Directory:** `api-server`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`

6. **Add Environment Variable:**
   - Key: `GOOGLE_API_KEY`
   - Value: `your_gemini_api_key_here`

7. Click **"Create Web Service"**

### Step 3: Wait for Deployment (~5-10 minutes)

Render will:
- Install dependencies
- Build your app
- Deploy it

You'll get a URL like: `https://pdf-hindi-translator-api.onrender.com`

### Step 4: Update Chrome Extension

Edit `chrome-extension/popup.js`:
```javascript
// Line 1: Change from
const API_URL = 'http://localhost:5001';

// To your Render URL
const API_URL = 'https://pdf-hindi-translator-api.onrender.com';
```

### Step 5: Test It!

1. Reload extension in `chrome://extensions/`
2. Open a PDF
3. Click extension
4. Translate! ✨

---

## Important Notes

⚠️ **Free tier limitation:** 
- App sleeps after 15 min of inactivity
- First request after sleep takes ~30-60 seconds to wake up
- After that, works instantly

✅ **To upgrade:** $7/month for always-on instance

---

## Already Deployed?

Your API URL: `https://pdf-hindi-translator-api.onrender.com`

Just update the extension URL and you're done!
