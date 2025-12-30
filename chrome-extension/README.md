# Chrome Extension for PDF Translation

## Setup Instructions

### 1. Install API Server Dependencies

```bash
cd api-server
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python3 app.py
```

The server will start on `http://localhost:5000`

### 3. Load Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension/` folder
5. The extension icon will appear in your toolbar

### 4. Add Extension Icons (Placeholder)

For now, you can use emoji icons or simple colored squares. To create proper icons:
- Create 16x16, 48x48, and 128x128 PNG images
- Save them in `chrome-extension/icons/` as `icon16.png`, `icon48.png`, `icon128.png`
- Or use an online icon generator like https://www.favicon-generator.org/

## How to Use

1. **Start the API server** (Step 2 above)
2. **Open any PDF** in Chrome (from web or local file)
3. **Click the extension icon** in toolbar
4. **Click "Translate This PDF"** button
5. **Wait for translation** (progress shown in popup)
6. **Translated PDF opens** in new tab automatically!

## Troubleshooting

### "API server not running"
- Make sure you ran `python3 api-server/app.py`
- Check that port 5000 is not in use
- Verify the server shows "Running on http://0.0.0.0:5000"

### "Translation failed"
- Check the API server terminal for error messages
- Ensure your `GOOGLE_API_KEY` is set in `.env`
- Make sure `tectonic` is installed (`brew install tectonic`)

### Extension not appearing
- Make sure you loaded the unpacked extension
- Check `chrome://extensions/` for errors
- Reload the extension after any code changes

## Architecture

```
User clicks button
      ↓
Chrome Extension (popup.js)
      ↓
Fetches PDF from current tab
      ↓
Sends to Flask API (localhost:5000/translate)
      ↓
Uses latex_converter.py
      ↓
Returns translated PDF
      ↓
Opens in new Chrome tab
```

## Notes

- Server must be running locally for extension to work
- Large PDFs may take several minutes to translate
- The extension works with both online PDFs and local files opened in Chrome
