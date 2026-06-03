import pytesseract
from PIL import Image
import io

def extract_text_from_image(file_bytes: bytes) -> str:
    """Extract text from image using Tesseract OCR."""
    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)
    return text.strip()
