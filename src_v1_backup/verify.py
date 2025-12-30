import os
import argparse
import sys
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def stitch_images(image1, image2):
    """Stitches two images side-by-side."""
    width1, height1 = image1.size
    width2, height2 = image2.size
    
    total_width = width1 + width2
    max_height = max(height1, height2)
    
    new_im = Image.new('RGB', (total_width, max_height))
    new_im.paste(image1, (0, 0))
    new_im.paste(image2, (width1, 0))
    
    return new_im

def verify_pdf(input_pdf, output_pdf, api_key, pages_to_check=3):
    """
    Verifies PDF conversion quality using Gemini Vision.
    """
    if not api_key:
        print("Error: API Key is required for verification.")
        return

    genai.configure(api_key=api_key)
    # Using gemini-2.0-flash-exp (or stable) for vision capabilities
    # gemini-1.5-flash is also good for vision. Let's try gemini-2.0-flash as we used it for text.
    model = genai.GenerativeModel('gemini-2.0-flash')

    print(f"Converting PDFs to images for verification (Checking first {pages_to_check} pages)...")
    
    try:
        images_input = convert_from_path(input_pdf, first_page=1, last_page=pages_to_check)
        images_output = convert_from_path(output_pdf, first_page=1, last_page=pages_to_check)
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        print("Note: You need 'poppler' installed. On Mac: `brew install poppler`.")
        return

    report = []
    
    min_len = min(len(images_input), len(images_output))
    
    print("Analyzing pages with Gemini Vision...")
    
    for i in range(min_len):
        print(f"Verifying Page {i+1}...")
        
        img_in = images_input[i]
        img_out = images_output[i]
        
        stitched = stitch_images(img_in, img_out)
        
        # Save stitched for user to see manually if they want
        debug_dir = "verification_debug"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        stitched.save(f"{debug_dir}/page_{i+1}_comparison.png")
        
        prompt = """
        You are a QA expert verifying a PDF translation tool.
        
        LEFT IMAGE: Original English PDF Page.
        RIGHT IMAGE: Translated Hinglish PDF Page.
        
        Your Task:
        Critique the RIGHT image based on the LEFT image. Focus on:
        1. **Layout Fidelity**: Does the text start/end at similar positions? Are paragraphs split correctly?
        2. **Text Overlap**: Is the translated text writing OVER other text or images? (Major Fail)
        3. **Formatting**: Are fonts appropriately sized? (It's okay if they are slightly different, but huge mismatches are bad).
        4. **Translation Quality**: Does the Hinglish look natural (Romanized Hindi) or just English?
        
        Output format:
        - **Status**: [PASS / WARN / FAIL]
        - **Issues**: List of specific issues found.
        - **Suggestion**: How to fix (e.g., "Reduce font size", "Increase line spacing").
        """
        
        try:
            response = model.generate_content([prompt, stitched])
            report.append(f"--- Page {i+1} ---\n{response.text.strip()}\n")
            print(f"Page {i+1} Analysis:\n{response.text.strip()}\n")
        except Exception as e:
            print(f"Error verifying page {i+1}: {e}")
            report.append(f"--- Page {i+1} ---\nError during analysis: {e}\n")

    # Save full report
    with open("verification_report.txt", "w") as f:
        f.write("\n".join(report))
    
    print(f"Verification Check Complete. Report saved to 'verification_report.txt'. Debug images in '{debug_dir}/'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Verification Tool")
    parser.add_argument("input_pdf", help="Original PDF")
    parser.add_argument("output_pdf", help="Translated PDF")
    parser.add_argument("--pages", type=int, default=3, help="Number of pages to verify")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Try finding .env manually if not loaded
        if os.path.exists(".env"):
             with open(".env") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
    
    verify_pdf(args.input_pdf, args.output_pdf, api_key, args.pages)
