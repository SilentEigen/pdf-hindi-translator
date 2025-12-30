# Quick Start - Test Extension Locally

## 1. Start API Server
```bash
cd "/Users/gobindkumar/Documents/My Projects/PDF Hinglish Converter"
python3 api-server/app.py
```

**You should see:**
```
🚀 Starting PDF Translation API Server...
📍 Endpoint: http://localhost:5001/translate
💡 Health Check: http://localhost:5001/health
```

## 2. Load Extension in Chrome

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable **"Developer mode"** (toggle in top right)
4. Click **"Load unpacked"**
5. Select folder: `/Users/gobindkumar/Documents/My Projects/PDF Hinglish Converter/chrome-extension`
6. Extension appears with icon!

## 3. Test It

1. Open any PDF in Chrome (e.g., from Google, arXiv, etc.)
2. Click the extension icon in toolbar
3. Click **"🌐 Translate This PDF"**
4. Wait (~2-5 minutes for translation)
5. Translated PDF opens in new tab!

## Troubleshooting

### "API server not running"
- Make sure `python3 api-server/app.py` is running in terminal
- Check it shows port 5001

### "Failed to download PDF"
- Some PDFs are blocked by CORS
- Try a different PDF
- Or use a local PDF file

### Extension not appearing
- Refresh `chrome://extensions/` page
- Check for errors in extension details

## You're All Set! 🎉

The extension works **locally** without any deployment. When you want to publish to Chrome Web Store later, then you'll need to deploy the server.
