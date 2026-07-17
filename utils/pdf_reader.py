import fitz

def extract_text(pdf_path):
    """
    Extract all text from a PDF file.
    """

    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text