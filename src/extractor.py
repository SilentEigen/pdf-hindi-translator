import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
try:
    from .ocr import OCRProcessor
except ImportError:
    # Fallback for when running as script
    from ocr import OCRProcessor

class PDFExtractor:
    def __init__(self, pdf_path: str, use_ocr: bool = True):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.ocr_processor = OCRProcessor() if use_ocr else None

    def extract_text_content(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extracts content from the PDF page by page.
        Returns a list of dictionaries containing page number and elements.
        """
        extracted_data = []
        
        total_pages = len(self.doc)
        if max_pages:
            total_pages = min(total_pages, max_pages)

        for page_num in range(total_pages):
            page = self.doc.load_page(page_num)
            page_data = {
                "page": page_num + 1,
                "blocks": [],
                "images": [],
                "page_width": page.rect.width,
                "page_height": page.rect.height
            }

            # Extract text blocks
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    text_block = {
                        "bbox": block["bbox"],
                        "lines": []
                    }
                    for line in block["lines"]:
                        line_data = {
                            "bbox": line["bbox"],
                            "spans": []
                        }
                        for span in line["spans"]:
                            span_data = {
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "size": span["size"],
                                "font": span["font"],
                                "color": span["color"],
                                "flags": span["flags"],
                                "origin": span["origin"]
                            }
                            line_data["spans"].append(span_data)
                        text_block["lines"].append(line_data)
                    page_data["blocks"].append(text_block)

                elif block["type"] == 1:  # Image block
                    image_block = {
                        "bbox": block["bbox"],
                        "image": block.get("image", None), # binary data
                        "ext": block.get("ext", "png"),
                        "ocr_text": ""
                    }
                    
                    # If we have OCR capability and image data, try to extract text
                    if self.ocr_processor and image_block["image"]:
                         image_block["ocr_text"] = self.ocr_processor.extract_text_from_image(image_block["image"])
                    
                    page_data["images"].append(image_block)

            extracted_data.append(page_data)

        return extracted_data

    def close(self):
        self.doc.close()
