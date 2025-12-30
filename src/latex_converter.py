import os
import argparse
import sys
from pdf2image import convert_from_path
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
import fitz  # PyMuPDF

# Load env variables
load_dotenv()

class LatexConverter:
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API Key is required.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def extract_images_from_page(self, pdf_path, page_num, output_dir):
        """Extracts images from a specific page."""
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num - 1)
        image_list = page.get_images(full=True)
        
        saved_images = []
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"page_{page_num}_img_{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_name)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            saved_images.append(image_name)
        return saved_images

    def contains_devanagari(self, text):
        """Check if text contains any Indic script characters (Devanagari, Telugu, Tamil, etc.)."""
        for char in text:
            code = ord(char)
            # Devanagari: 0900-097F
            # Bengali: 0980-09FF
            # Tamil: 0B80-0BFF
            # Telugu: 0C00-0C7F
            # Kannada: 0C80-0CFF
            # Malayalam: 0D00-0D7F
            # All Indic scripts: 0900-0D7F
            if 0x0900 <= code <= 0x0D7F:
                return True
        return False

    def convert_page_to_latex(self, image, page_num, available_images):
        """
        Sends page image to Gemini and gets LaTeX code with Hinglish translation.
        Automatically retries if Devanagari script is detected.
        """
        print(f"Propcessing page {page_num}...")
        
        img_list_str = ", ".join(available_images) if available_images else "None"
        
        # Create an example string safely
        example_img = available_images[0] if available_images else "images/placeholder.png"

        prompt = f"""
        You are an expert Document-to-LaTeX converter and Translator. 
        
        Your Goal:
        1. **Visual to LaTeX**: Convert the visual layout into valid LaTeX.
           - Use `\\section{{...}}`, `\\subsection{{...}}` for headers.
           - If you see a **Table of Contents**:
             - Just write `\\tableofcontents`.
             - **CRITICAL**: Do NOT manually transcribe the TOC entries as `\\section` commands. The `\\tableofcontents` command will auto-generate it from the rest of the document.
        
        2. **Translation (Romanized Hindi - TRANSLITERATED)**: Translate English to Hindi, but write ONLY in Roman/Latin script.
           - **ABSOLUTELY CRITICAL**: DO NOT use Devanagari script (देवनागरी). Use ONLY a-z characters.
           - **Example of CORRECT output**: "Hum dikhate hain ki hani kam ho gayi hai."
           - **Example of WRONG output**: "हम दिखाते हैं कि हानि कम हो गई है।" ← NEVER DO THIS
           - **Vocabulary**: Use pure Hindi words (not English verbs).
           - **Grammar Guide**:
             - English: "This process is used to create mirrors."
             - WRONG: "Yeh process mirrors create karne ke liye use kiya jata hai." (English verbs)
             - CORRECT: "Yeh prakriya mirrors banane ke liye upyog ki jaati hai." (Hindi verbs)
             - English: "We show that the loss is reduced."
             - WRONG: "Hum show karte hain ki loss reduce ho gaya hai."
             - CORRECT: "Hum dikhate hain ki hani kam ho gayi hai."
           - **Exceptions**: Keep technical nouns (Birefringence, Cavity, Laser) in English.
        
        3. **Math & Science**:
           - **CRITICAL**: Transcribe equations EXACTLY as they appear using LaTeX math mode.
           - Use `\\begin{{equation}} ... \\end{{equation}}` for NUMBERED equations.
           - Use `$$ ... $$` for unnumbered display math.
           - **NEVER** use `\\tag` inside `$$ ... $$`.
        
        4. **Images**: 
           - I have extracted the following images from this page: [{img_list_str}].
           - Use smart sizing to avoid pushing images to next page:
             * For SMALL images (diagrams, icons): `\\begin{{figure}}[h] \\centering \\includegraphics[width=0.5\\linewidth]{{{example_img}}} \\caption{{Caption}} \\end{{figure}}`
             * For MEDIUM images (charts, graphs): `\\begin{{figure}}[h] \\centering \\includegraphics[width=0.7\\linewidth]{{{example_img}}} \\caption{{Caption}} \\end{{figure}}`
             * For LARGE images (full-page plots): `\\begin{{figure}}[h] \\centering \\includegraphics[width=0.85\\linewidth]{{{example_img}}} \\caption{{Caption}} \\end{{figure}}`
           - **CRITICAL**: Use `[h]` (lowercase h) to allow flexible placement, NOT `[H]`. This prevents blank spaces.
           - If no extracted image matches the figure, use a placeholder.
        
        Strict Rules:
        - Return ONLY the LaTeX body content.
        - No markdown formatting.
        - No chatty intro/outro.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add progressively stronger warnings
                current_prompt = prompt
                if attempt > 0:
                    current_prompt += f"\n\n**EMERGENCY OVERRIDE (Attempt {attempt + 1})**: You MUST use ONLY English letters (a-z). NO देवनागरी script allowed!"
                if attempt == max_retries - 1:
                    current_prompt += "\n\n**FINAL WARNING**: If you CANNOT translate a word to Roman script, just LEAVE IT IN ENGLISH as-is. Do NOT use Devanagari under any circumstances!"
                
                response = self.model.generate_content([current_prompt, image])
                content = response.text.replace("```latex", "").replace("```", "").strip()
                
                # Check for Devanagari
                if self.contains_devanagari(content):
                    print(f"⚠️  Warning: Devanagari detected on page {page_num}. Retrying (attempt {attempt + 1}/{max_retries})...")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        # Final fallback: Strip Devanagari and replace with English placeholder
                        print(f"❌ Failed to get Roman script after {max_retries} attempts.")
                        print(f"🔧 Applying emergency fix: Removing Devanagari characters...")
                        content = self.remove_devanagari_fallback(content)
                        print(f"✓ Page {page_num} converted with fallback (Devanagari removed)")
                        return content
                
                print(f"✓ Page {page_num} converted successfully (Pure Romanized Hindi)")
                return content
                
            except Exception as e:
                print(f"Error converting page {page_num}: {e}")
                if attempt == max_retries - 1:
                    return f"% Error converting page {page_num}: {e}"
        
        return f"% Failed to convert page {page_num} after {max_retries} attempts"
    
    def remove_devanagari_fallback(self, text):
        """Remove Devanagari characters and replace with descriptive placeholder."""
        result = []
        current_word = []
        has_devanagari = False
        
        for char in text:
            code = ord(char)
            if 0x0900 <= code <= 0x0D7F:
                # Devanagari/Indic character detected
                has_devanagari = True
                current_word.append(char)
            else:
                if has_devanagari and current_word:
                    # End of Devanagari word - replace it
                    result.append("[TERM]")  # Placeholder for untranslatable term
                    current_word = []
                    has_devanagari = False
                result.append(char)
        
        return ''.join(result)

    def generate_pdf(self, input_pdf, output_pdf, max_pages=None):
        print(f"Converting {input_pdf} to images...")
        try:
            images = convert_from_path(input_pdf)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return

        if max_pages:
            images = images[:max_pages]

        # Prepare output dir for images
        output_dir = os.path.dirname(output_pdf)
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        latex_body_parts = []
        
        for i, img in enumerate(images):
            page_num = i + 1
            available_images = self.extract_images_from_page(input_pdf, page_num, images_dir)
            # Pass relative path to Gemini so it generates correct LaTeX
            # But wait, LaTeX needs path relative to .tex file.
            # .tex file is in output_dir. images are in output_dir/images.
            # So latex path should be "images/filename".
            
            # Update available_images list to include "images/" prefix for prompt clarity?
            # Actually, I'll handle the pathing in the prompt logic above or just pass filenames and tell prompt to prefix.
            # Let's adjust the prompt injection to be cleaner.
            
            # Re-inject logic for prompt:
            # I need to pass 'images/' + name to the prompt instruction.
            prompt_images = [f"images/{name}" for name in available_images]
            
            latex_content = self.convert_page_to_latex(img, page_num, prompt_images)
            latex_body_parts.append(f"% --- Page {page_num} ---\n{latex_content}\n\\newpage\n")

        full_latex = r"""
\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{a4paper, margin=0.8in}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}

\title{Translated Document (Hinglish)}
\date{\today}

\begin{document}

""" + "\n".join(latex_body_parts) + r"""

\end{document}
"""
        
        # Save tex file
        output_tex = output_pdf.replace(".pdf", ".tex")
        with open(output_tex, "w") as f:
            f.write(full_latex)
        
        print(f"LaTeX source saved to {output_tex}")
        print("Compiling with Tectonic...")
        
        # Compile
        subprocess.run(["tectonic", output_tex], check=True)
        
        print(f"Done! Output saved to {output_pdf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF to Hinglish via LaTeX")
    parser.add_argument("input_pdf", help="Input PDF")
    parser.add_argument("output_pdf", help="Output PDF")
    parser.add_argument("--pages", type=int, help="Limit pages", default=None)
    
    args = parser.parse_args()
    
    converter = LatexConverter()
    converter.generate_pdf(args.input_pdf, args.output_pdf, args.pages)
