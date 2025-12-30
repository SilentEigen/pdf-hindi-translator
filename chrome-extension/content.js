// Content script - runs on all pages to detect PDFs

// Detect if current page is a PDF
const isPDF = () => {
    return document.contentType === 'application/pdf' ||
        window.location.href.endsWith('.pdf') ||
        document.querySelector('embed[type="application/pdf"]') !== null;
};

// Store PDF status
if (isPDF()) {
    chrome.storage.local.set({ currentPageIsPDF: true });
    console.log('📄 PDF detected on this page');
} else {
    chrome.storage.local.set({ currentPageIsPDF: false });
}
