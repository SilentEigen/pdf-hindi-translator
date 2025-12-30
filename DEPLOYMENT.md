# Chrome Extension Publishing Guide

## Overview
To publish this extension to Chrome Web Store, you need to:
1. Deploy the API server to a cloud platform
2. Update extension to use production API URL
3. Submit to Chrome Web Store

---

## Option 1: Deploy to Google Cloud Run (Recommended)

### Why Google Cloud Run?
- ✅ Serverless (no server management)
- ✅ Pay per use (scales to zero)
- ✅ Free tier available
- ✅ Supports Docker containers

### Steps:

#### 1. Create Dockerfile
```bash
cd api-server
# Dockerfile is already created (see below)
```

#### 2. Deploy to Cloud Run
```bash
# Install Google Cloud CLI
brew install google-cloud-sdk

# Login
gcloud auth login

# Create project
gcloud projects create pdf-hindi-translator

# Enable Cloud Run
gcloud services enable run.googleapis.com --project=pdf-hindi-translator

# Build and deploy
gcloud run deploy pdf-translator-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_api_key_here
```

#### 3. Get Your API URL
After deployment, you'll get a URL like:
```
https://pdf-translator-api-xxxxx-uc.a.run.app
```

**Cost:** ~$0 for low usage (free tier covers most personal use)

---

## Option 2: Deploy to Heroku

### Steps:

#### 1. Install Heroku CLI
```bash
brew install heroku
heroku login
```

#### 2. Create & Deploy
```bash
cd api-server
heroku create pdf-hindi-translator
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a pdf-hindi-translator
git push heroku main
```

#### 3. Set Environment Variables
```bash
heroku config:set GOOGLE_API_KEY=your_api_key_here
```

**Cost:** Free tier available (sleeps after 30 min of inactivity)

---

## Option 3: Run on Your Own Server (VPS)

If you have a VPS (DigitalOcean, AWS EC2, etc.):

```bash
# SSH into server
ssh user@your-server.com

# Clone repo
git clone your-repo-url
cd api-server

# Install dependencies
pip3 install -r requirements.txt

# Install tectonic
apt-get install tectonic  # or equivalent for your OS

# Set env vars
export GOOGLE_API_KEY=your_key

# Run with gunicorn (production WSGI server)
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**Use reverse proxy (nginx):**
```nginx
server {
    listen 80;
    server_name api.yourDomain.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Cost:** ~$5-10/month for basic VPS

---

## Update Extension for Production

### 1. Update API URL
Edit `chrome-extension/popup.js`:
```javascript
// Change from:
const API_URL = 'http://localhost:5001';

// To your deployed URL:
const API_URL = 'https://your-api-url.com';
```

### 2. Update manifest.json
Edit `chrome-extension/manifest.json`:
```json
"host_permissions": [
    "https://your-api-url.com/*",
    "<all_urls>"
]
```

---

## Submit to Chrome Web Store

### 1. Create Developer Account
- Go to https://chrome.google.com/webstore/devconsole
- Pay one-time $5 developer fee

### 2. Prepare Extension Package
```bash
cd chrome-extension
zip -r pdf-hindi-translator.zip .
```

### 3. Upload & Publish
1. Click "New Item"
2. Upload `pdf-hindi-translator.zip`
3. Fill in store listing:
   - **Name:** PDF Hindi Translator
   - **Description:** Translate any PDF to Romanized Hindi with one click
   - **Category:** Productivity
   - **Screenshots:** Take screenshots of the popup and translated PDFs
4. Submit for review (usually 1-3 days)

---

## Security Considerations

### Rate Limiting
Add to `app.py`:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["10 per minute"]
)
```

### API Key Security
- **Never hardcode** your Gemini API key
- Use environment variables
- Consider adding user authentication

### CORS
Already configured with `flask-cors`, but verify:
```python
CORS(app, origins=["chrome-extension://*"])
```

---

## Recommended: Google Cloud Run

**Cost Estimate:**
- First 2 million requests/month: FREE
- 360,000 GB-seconds: FREE
- After that: ~$0.000012 per request

**Setup Time:** ~15 minutes

**Scalability:** Automatic (0 to thousands of users)

This is the best option for a Chrome extension because:
1. No server management
2. Extremely cheap for personal/small scale
3. Automatic scaling
4. Easy deployment
