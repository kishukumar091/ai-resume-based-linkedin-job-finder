from io import BytesIO
from typing import Literal

import docx
import pdfplumber


SupportedMime = Literal[
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]


def parse_pdf(content: bytes) -> str:
    text_parts = []
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                text_parts.append(text)
    return "\n".join(text_parts).strip()


def parse_docx(content: bytes) -> str:
    file_stream = BytesIO(content)
    document = docx.Document(file_stream)
    return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text).strip()


def extract_text(content: bytes, content_type: SupportedMime, filename: str) -> str:
    normalized_name = filename.lower()
    if content_type == "application/pdf" or normalized_name.endswith(".pdf"):
        return parse_pdf(content)
    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or normalized_name.endswith(".docx")
    ):
        return parse_docx(content)
    raise ValueError("Unsupported file format. Please upload a PDF or DOCX resume.")
