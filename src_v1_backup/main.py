import argparse
import os
import sys
from extractor import PDFExtractor
from translator import Translator
from generator import PDFGenerator

def main():
    parser = argparse.ArgumentParser(description="PDF to Hinglish Converter")
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_pdf", help="Path to save the output PDF file")
    parser.add_argument("--api-key", help="Google Gemini API Key (optional if GOOGLE_API_KEY env var is set)", default=None)
    parser.add_argument("--save-key", action="store_true", help="Save the provided API key to a .env file for future use")
    parser.add_argument("--pages", type=int, help="Number of pages to convert (default: all)", default=None)
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR for images")

    args = parser.parse_args()

    # Load from .env if exists
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    os.environ["GOOGLE_API_KEY"] = line.strip().split("=", 1)[1]

    if args.api_key:
        os.environ["GOOGLE_API_KEY"] = args.api_key
        if args.save_key:
            with open(env_path, "w") as f:
                f.write(f"GOOGLE_API_KEY={args.api_key}\n")
            print(f"API Key saved to {env_path}")
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found. Please provide it via --api-key or use --save-key to store it.")
        sys.exit(1)

    print(f"Processing {args.input_pdf}...")

    # 1. Extract
    print("Extracting text and layout...")
    extractor = PDFExtractor(args.input_pdf, use_ocr=not args.no_ocr)
    pages_data = extractor.extract_text_content(max_pages=args.pages)
    extractor.close()
    print(f"Extracted {len(pages_data)} pages.")

    # 2. Collect unique text for translation (Block Level)
    print("Preparing text for translation (Block Level)...")
    unique_texts = set()
    for page in pages_data:
        for block in page["blocks"]:
            # Aggregate text from all lines/spans in the block
            block_text_parts = []
            for line in block["lines"]:
                for span in line["spans"]:
                    block_text_parts.append(span["text"])
            
            full_block_text = " ".join(block_text_parts).strip()
            if full_block_text:
                unique_texts.add(full_block_text)
                # Store it back in the block for easier access later? 
                # No, we just use the map. But we need to reconstruct the key exactly.
                # To be safe, let's store the aggregated text in the block structure itself in memory
                block["aggregated_text"] = full_block_text
        
        # Add OCR text if any
        for img in page["images"]:
            if img.get("ocr_text"):
                unique_texts.add(img["ocr_text"])

    sorted_texts = sorted(list(unique_texts))
    print(f"Found {len(sorted_texts)} blocks to translate.")

    # 3. Translate
    print("Translating to Hinglish (this may take a while)...")
    translator = Translator()
    # Batch translation could be implemented here for efficiency
    # For now, simplistic loop
    translation_map = {}
    
    # Simple progress indicator
    total = len(sorted_texts)
    for i, text in enumerate(sorted_texts):
        if i % 10 == 0:
            print(f"Translating {i}/{total}...")
        try:
             translated = translator.translate_text(text)
             translation_map[text] = translated
        except Exception as e:
            print(f"Failed to translate '{text}': {e}")
            translation_map[text] = text

    print("Translation complete.")

    # 4. Generate
    print(f"Generating output PDF at {args.output_pdf}...")
    generator = PDFGenerator(args.output_pdf)
    generator.generate(pages_data, translation_map)
    print("Done!")

if __name__ == "__main__":
    main()
