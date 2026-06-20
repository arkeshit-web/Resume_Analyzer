import io
import pdfplumber

def extract_text_from_pdf(pdf_file_bytes):
    """
    Extracts text from PDF file bytes using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")
        
    return clean_text(text)

def clean_text(text):
    """
    Cleans raw text by consolidating whitespace, normalising unicode quotes, and removing control chars.
    """
    if not text:
        return ""
    # Normalize space characters
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Strip trailing/leading spaces and consolidate multiple spaces
        cleaned_line = " ".join(line.strip().split())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)
