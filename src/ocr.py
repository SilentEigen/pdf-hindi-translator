import pytesseract
from PIL import Image
import io
import fitz

class OCRProcessor:
    def __init__(self):
        # Assuming tesseract is in path. If not, paths might need configuration.
        pass

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extracts text from an image byte stream.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Error during OCR: {e}")
            return ""

    def process_image_block(self, block: dict) -> dict:
        """
        Process an image block from PyMuPDF, performing OCR if needed.
        """
        # This is a placeholder for logic that decides IF we should OCR.
        # For now, we can just return the block with an added 'ocr_text' field.
        if "image" in block and block["image"]:
            text = self.extract_text_from_image(block["image"])
            block["ocr_text"] = text
        return block
