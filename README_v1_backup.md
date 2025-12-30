# PDF to Hinglish Converter

A Python tool that converts English PDF documents to Hinglish (Hindi-English mix) while preserving the original layout, formatting, and images.

## Features

- **Layout Preservation**: Maintains the original document's structure, fonts, and image placement.
- **Hinglish Translation**: Uses Google Gemini API for natural-sounding English-to-Hinglish translation.
- **Image Handling**: Extracts and re-places images.
- **OCR Support**: Extracts and text from images (if needed) using Tesseract.
- **Command Line Interface**: Easy-to-use CLI.

## Requirements

- Python 3.8+
- Google Gemini API Key

## Installation

1. Clone the repository or download the source code.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR (if using OCR features):
   - **macOS**: `brew install tesseract`
   - **Windows**: Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt install tesseract-ocr`

## Usage

Set your Google API Key:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

Run the converter:
```bash
python src/main.py input/document.pdf output/document_hinglish.pdf
```

### Options
- `--api-key`: Pass the API key directly if not set in environment.
- `--save-key`: Save the provided API key to a `.env` file for future use.
- `--pages <N>`: Limit conversion to the first N pages.
- `--no-ocr`: Disable OCR processing for images (faster).

## Example

```bash
python src/main.py my_paper.pdf my_paper_hinglish.pdf
```

## Known Limitations

- **Complex Layouts**: Highly complex multi-column layouts might have minor alignment shifts.
- **Font Rendering**: Uses standard fonts (Helvetica) which might slightly differ from embedded fonts in the original PDF.
- **Text Overflow**: If the translated text is significantly longer, it might overlap or look compressed.

## Troubleshooting

- **Google API Error**: Ensure your API key is valid and has access to Gemini models.
- **Tesseract Not Found**: Ensure Tesseract is installed and in your system PATH.
