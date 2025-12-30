# 🚀 Deploy in 10 Minutes

## Step 1: Create GitHub Repo (2 min)

1. Go to: **https://github.com/new**
2. Name: `pdf-hindi-translator`
3. Make it **Public**
4. Don't add README (we already have one)
5. Click **"Create repository"**

## Step 2: Push Code (1 min)

Run these commands:
```bash
cd "/Users/gobindkumar/Documents/My Projects/PDF Hinglish Converter"

# I already initialized git and committed for you!
# Just add your GitHub repo URL:

git remote add origin https://github.com/YOUR_USERNAME/pdf-hindi-translator.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render.com (5 min)

1. Go to: **https://render.com** → Sign up (free with GitHub)
2. Click **"New +"** → **"Web Service"**
3. Connect your repo: `pdf-hindi-translator`
4. Settings:
   - **Name:** `pdf-hindi-api`
   - **Root Directory:** `api-server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
5. **Environment Variables** → Add:
   - `GOOGLE_API_KEY` = (paste your Gemini API key)
6. Click **"Deploy"** (wait 5-10 min)

## Step 4: Update Extension (1 min)

After deployment, Render gives you a URL like:
```
https://pdf-hindi-api.onrender.com
```

Update `chrome-extension/popup.js` line 1:
```javascript
const API_URL = 'https://pdf-hindi-api.onrender.com';
```

Save and reload extension in Chrome!

## Step 5: Publish to Chrome Web Store (Optional)

1. Go to: **https://chrome.google.com/webstore/devconsole**
2. Pay $5 one-time fee
3. Zip extension: `cd chrome-extension && zip -r extension.zip .`
4. Upload and publish!

---

**Your extension will be live and work for everyone!** 🎉

**Note:** Free tier sleeps after 15 min inactivity. First request takes ~30s to wake up. Upgrade to $7/month for always-on.
