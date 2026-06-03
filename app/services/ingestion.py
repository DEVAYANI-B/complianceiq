from app.services.ocr import extract_text_from_image


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF. Falls back to OCR if no text layer.

    Uses a lazy import for PyMuPDF (`fitz`) so the application can start
    even if `pymupdf` is not installed or fails to build. The import error
    will be raised only when this function is called.
    """
    try:
        import fitz  
    except Exception as e:
        raise ImportError(
            "PyMuPDF (fitz) is required to extract text from PDFs. "
            "Install pymupdf or provide text/plain documents. Original error: "
            f"{e}"
        ) from e

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text and text.strip():
            full_text += f"\n[Page {page_num + 1}]\n{text}"
        else:
           
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            ocr_text = extract_text_from_image(img_bytes)
            full_text += f"\n[Page {page_num + 1} - OCR]\n{ocr_text}"
    return full_text.strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Route to correct extractor based on file type."""
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ["png", "jpg", "jpeg"]:
        return extract_text_from_image(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
