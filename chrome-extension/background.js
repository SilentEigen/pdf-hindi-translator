// Background service worker for PDF Translator extension

// Track ongoing translations by PDF URL (not tab ID, since tabs can refresh)
let activeTranslations = {};

chrome.runtime.onInstalled.addListener(() => {
    console.log('PDF Hindi Translator extension installed!');
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'startTranslation') {
        activeTranslations[request.pdfUrl] = {
            status: 'processing',
            filename: request.filename,
            startTime: Date.now()
        };
        sendResponse({ status: 'started' });
    } else if (request.action === 'getTranslationStatus') {
        const status = activeTranslations[request.pdfUrl] || { status: 'idle' };
        sendResponse(status);
    } else if (request.action === 'completeTranslation') {
        if (activeTranslations[request.pdfUrl]) {
            delete activeTranslations[request.pdfUrl];
        }
        sendResponse({ status: 'completed' });
    } else if (request.action === 'failTranslation') {
        if (activeTranslations[request.pdfUrl]) {
            delete activeTranslations[request.pdfUrl];
        }
        sendResponse({ status: 'failed' });
    }
    return true;
});
