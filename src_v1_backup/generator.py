from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from PIL import Image

class PDFGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print(f"Error creating directory {output_dir}: {e}")
        
        self.c = canvas.Canvas(self.output_path)
        # Register simplified fonts if needed, otherwise use standard fonts
        # For now, we rely on standard fonts or we could register a generic Unicode font if needed for Hindi characters
        # ReportLab standard fonts (Helvetica, Times, etc.) might not support Hindi characters well.
        # We really need a font that supports Devanagari/Latin.
        # Ideally, we should check if the system has a font or bundle one.
        # For this prototype, we'll try to use a standard font or assume English characters (Hinglish is Roman script).
        # Since Hinglish is Romanized, standard fonts like Helvetica should work fine.

    def generate(self, pages_data: list, translated_texts: dict):
        """
        Generates the PDF based on extracted data and translated texts.
        translated_texts: dictionary mapping original text to translated text (or just a list corresponding to blocks)
        """
        for page_data in pages_data:
            # Set page size
            self.c.setPageSize((page_data["page_width"], page_data["page_height"]))
            
            # Draw images first
            for img in page_data["images"]:
                if img["image"]:
                    try:
                        image_reader = io.BytesIO(img["image"])
                        # Convert to PIL Image to get dimensions if needed, or draw directly
                        # reportlab drawImage requires a file path or an ImageReader object
                        # We use ImageReader from reportlab.lib.utils? No, canvas.drawImage accepts ImageReader
                        from reportlab.lib.utils import ImageReader
                        img_obj = ImageReader(image_reader)
                        x0, y0, x1, y1 = img["bbox"]
                        width = x1 - x0
                        height = y1 - y0
                        # PDF coordinates are bottom-up, PyMuPDF are top-down?
                        # PyMuPDF: (x0, y0, x1, y1) where (0,0) is top-left.
                        # ReportLab: (0,0) is bottom-left.
                        # We need to invert Y.
                        
                        rl_y = page_data["page_height"] - y1
                        
                        self.c.drawImage(img_obj, x0, rl_y, width=width, height=height)
                        
                        # If OCR text exists, we might want to overlay it (complex) or just ignore 
                        # as per current scope we are just placing images back.
                        # If we translated OCR text, we would need to draw it.
                        if img.get("ocr_text_translated"):
                            # Very basic overlay - drawing white rect and text
                            # self.c.setFillColor("white")
                            # self.c.rect(x0, rl_y, width, height, fill=1)
                            # self.c.setFillColor("black")
                            # self.c.drawString(x0, rl_y + height/2, img["ocr_text_translated"])
                             pass

                    except Exception as e:
                        print(f"Error drawing image: {e}")

            # Draw text (Block Level)
            from reportlab.lib.utils import simpleSplit
            
            for block in page_data["blocks"]:
                # Get the aggregated text we flagged earlier (or reconstruct)
                # We need to reconstruct if we didn't save it, but we modified main.py to save it?
                # Actually main.py modified the dict in memory, so it should be there if we passed the same object.
                # Let's reconstruct to be safe and consistent with main.py's logic if it wasn't saved.
                
                block_text_parts = []
                # We also need to determine the dominant style (font, size, color)
                # We'll take the first span's style as the representative one.
                first_span = None
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text_parts.append(span["text"])
                        if not first_span:
                            first_span = span
                
                original_text = " ".join(block_text_parts).strip()
                if not original_text:
                    continue
                    
                text_to_draw = translated_texts.get(original_text, original_text)
                
                if not first_span:
                    continue

                # Block BBox
                x0, y0, x1, y1 = block["bbox"]
                block_width = x1 - x0
                block_height = y1 - y0

                # Draw white background to erase underlying original text (if scanned/image-based)
                # Invert Y for rect. ReportLab Y is bottom-up.
                rect_y = page_data["page_height"] - y1
                self.c.setFillColorRGB(1, 1, 1) # White
                self.c.rect(x0, rect_y, block_width, block_height, stroke=0, fill=1)
                
                # Font settings from first span
                font_name = "Helvetica"
                if "Bold" in first_span["font"]:
                    font_name = "Helvetica-Bold"
                if "Italic" in first_span["font"]:
                     if font_name == "Helvetica-Bold":
                         font_name = "Helvetica-BoldOblique"
                     else:
                         font_name = "Helvetica-Oblique"
                
                font_size = first_span["size"]
                color = first_span["color"]
                
                self.c.setFillColorRGB(*self._int_to_rgb(color))
                
                # Wraps text into lines with padding
                lines = simpleSplit(text_to_draw, font_name, font_size, block_width - 2)
                
                # Check if it fits vertically. Compact leading.
                leading_factor = 1.1 
                leading = font_size * leading_factor
                total_text_height = len(lines) * leading
                
                # Dynamic scaling
                while total_text_height > block_height and font_size > 5:
                    font_size *= 0.95 
                    leading = font_size * leading_factor
                    lines = simpleSplit(text_to_draw, font_name, font_size, block_width - 2)
                    total_text_height = len(lines) * leading
                
                self.c.setFont(font_name, font_size)
                
                # Draw lines
                # Start from top-left of the block (converted to bottom-left Y)
                # PyMuPDF y0 is top. ReportLab Y is from bottom.
                # So top of block in RL is (page_height - y0)
                
                cursor_y = page_data["page_height"] - y0 - font_size # Start roughly at the first line baseline (approx)
                # Actually simpleSplit doesn't handle baseline, we just draw down.
                # Better: start at (page_height - y0) - leading?
                # Let's align top:
                cursor_y = (page_data["page_height"] - y0) - font_size 
                
                for line in lines:
                    self.c.drawString(x0, cursor_y, line)
                    cursor_y -= leading

            self.c.showPage()
        
        self.c.save()

    def _int_to_rgb(self, color_int):
        """
        Converts PyMuPDF color integer to ReportLab RGB (0-1).
        PyMuPDF color is sRGB int (if strictly integer) or tuple/list. 
        Actually PyMuPDF span['color'] is an integer.
        Format: 0xRRGGBB
        """
        if isinstance(color_int, int):
            r = ((color_int >> 16) & 0xFF) / 255.0
            g = ((color_int >> 8) & 0xFF) / 255.0
            b = (color_int & 0xFF) / 255.0
            return (r, g, b)
        return (0, 0, 0) # Default black if unknown format

