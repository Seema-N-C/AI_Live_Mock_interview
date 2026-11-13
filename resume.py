from pypdf import PdfReader


def extract_resume(file) -> str:
    """Extract text from an uploaded PDF resume (first 4000 chars)."""
    reader = PdfReader(file)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text.strip()[:4000]
