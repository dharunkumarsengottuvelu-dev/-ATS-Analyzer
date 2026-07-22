import pypdf
import docx
import io
from fastapi import UploadFile
from backend.ai.ocr.tesseract import extract_text_with_ocr

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extracts raw text from a PDF or DOCX file.
    Uses OCR if the PDF is scanned (contains no text).
    """
    file_bytes = await file.read()
    
    if file.filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif file.filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif file.filename.lower().endswith(".txt"):
        return file_bytes.decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT.")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    full_text = ""
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
        
    # Check if PDF is likely scanned (very little text extracted)
    if len(full_text.strip()) < 50:
        print("Scanned PDF detected. Falling back to OCR...")
        full_text = extract_text_with_ocr(pdf_bytes)
        
    return full_text

def extract_text_from_docx(docx_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(docx_bytes))
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return full_text
