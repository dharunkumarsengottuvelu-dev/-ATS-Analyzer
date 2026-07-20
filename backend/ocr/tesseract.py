import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF

def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    """
    Extracts text from a scanned PDF using Tesseract OCR.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"
        
    return full_text
