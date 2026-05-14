from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str):

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    return text


def extract_text_from_docx(file_path: str):

    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"

    return text