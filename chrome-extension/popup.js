const API_URL = 'http://localhost:5001';

let currentTabId = null;

// Check for ongoing translation when popup opens
async function checkTranslationStatus() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    currentTabId = tab.id;

    // Extract PDF URL
    let pdfUrl = tab.url;
    if (pdfUrl.includes('chrome-extension://') && pdfUrl.includes('viewer.html')) {
        const urlParams = new URLSearchParams(pdfUrl.split('?')[1]);
        pdfUrl = urlParams.get('file') || pdfUrl;
    }

    const response = await chrome.runtime.sendMessage({
        action: 'getTranslationStatus',
        pdfUrl: pdfUrl
    });

    if (response.status === 'processing') {
        const button = document.getElementById('translateBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        button.disabled = true;
        button.innerHTML = '<div class="spinner"></div> Translating...';
        cancelBtn.style.display = 'block';
        showStatus('🔄 Translation in progress... (started ' + getTimeAgo(response.startTime) + ')', 'processing');
    }
}

function getTimeAgo(timestamp) {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return seconds + 's ago';
    const minutes = Math.floor(seconds / 60);
    return minutes + 'm ago';
}

document.getElementById('cancelBtn').addEventListener('click', async () => {
    const button = document.getElementById('translateBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    let pdfUrl = tab.url;
    if (pdfUrl.includes('chrome-extension://') && pdfUrl.includes('viewer.html')) {
        const urlParams = new URLSearchParams(pdfUrl.split('?')[1]);
        pdfUrl = urlParams.get('file') || pdfUrl;
    }

    // Clear the translation status
    chrome.runtime.sendMessage({
        action: 'failTranslation',
        pdfUrl: pdfUrl
    });

    // Reset UI
    button.disabled = false;
    button.innerHTML = '🌐 Translate This PDF';
    cancelBtn.style.display = 'none';
    showStatus('⚠️ Translation cancelled', 'error');
});

document.getElementById('translateBtn').addEventListener('click', async () => {
    const button = document.getElementById('translateBtn');
    const status = document.getElementById('status');
    const cancelBtn = document.getElementById('cancelBtn');

    try {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        currentTabId = tab.id;

        // Extract actual PDF URL from Chrome's PDF viewer or extensions
        let pdfUrl = tab.url;

        // Handle Chrome's built-in PDF viewer or extension viewers
        if (pdfUrl.includes('chrome-extension://') && pdfUrl.includes('viewer.html')) {
            const urlParams = new URLSearchParams(pdfUrl.split('?')[1]);
            pdfUrl = urlParams.get('file') || pdfUrl;
        }

        // Check if it's a PDF
        if (!pdfUrl.endsWith('.pdf') && !pdfUrl.includes('.pdf?') && !pdfUrl.includes('pdf')) {
            showStatus('⚠️ Please open a PDF file first', 'error');
            return;
        }

        // Notify background that translation started (using PDF URL)
        chrome.runtime.sendMessage({
            action: 'startTranslation',
            pdfUrl: pdfUrl,
            filename: tab.title || 'document.pdf'
        });

        // Disable button and show processing
        button.disabled = true;
        button.innerHTML = '<div class="spinner"></div> Translating...';
        cancelBtn.style.display = 'block';
        showStatus('🔄 Downloading PDF...', 'processing');

        // Fetch the PDF with CORS handling
        const response = await fetch(pdfUrl, {
            mode: 'cors',
            credentials: 'omit'
        });

        if (!response.ok) {
            throw new Error(`Failed to download PDF: ${response.statusText}`);
        }

        const blob = await response.blob();

        // Verify it's actually a PDF
        if (!blob.type.includes('pdf') && !blob.type.includes('octet-stream')) {
            throw new Error('Downloaded file may not be a valid PDF');
        }

        showStatus('🔄 Translating...', 'processing');

        // Create FormData
        const formData = new FormData();
        formData.append('file', blob, 'document.pdf');

        // Send to API
        const apiResponse = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            body: formData
        });

        if (!apiResponse.ok) {
            throw new Error(`API Error: ${apiResponse.statusText}`);
        }

        // Get translated PDF
        const translatedBlob = await apiResponse.blob();
        const url = URL.createObjectURL(translatedBlob);

        // Open in new tab
        chrome.tabs.create({ url });

        // Notify completion
        chrome.runtime.sendMessage({
            action: 'completeTranslation',
            pdfUrl: pdfUrl
        });

        showStatus('✅ Translation complete! Opening in new tab...', 'success');
        cancelBtn.style.display = 'none';
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = '🌐 Translate This PDF';
        }, 2000);

    } catch (error) {
        console.error('Translation error:', error);

        // Notify failure
        chrome.runtime.sendMessage({
            action: 'failTranslation',
            pdfUrl: pdfUrl
        });

        showStatus(`❌ Error: ${error.message}`, 'error');
        button.disabled = false;
        button.innerHTML = '🌐 Translate This PDF';
        cancelBtn.style.display = 'none';
    }
});

function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = type;
    status.style.display = 'block';
}

// Check API health and translation status on load
Promise.all([
    fetch(`${API_URL}/health`)
        .then(res => res.json())
        .then(data => {
            console.log('✅ API Server connected:', data);
        })
        .catch(err => {
            showStatus('⚠️ API server not running. Please start the server first.', 'error');
            document.getElementById('translateBtn').disabled = true;
        }),
    checkTranslationStatus()
]);
