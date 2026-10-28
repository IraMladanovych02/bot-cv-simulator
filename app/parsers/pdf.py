from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.parsers.base import (
    BaseDocumentParser,
    DocumentFormat,
    EmptyDocumentError,
    EncryptedDocumentError,
    InvalidDocumentError,
    ParsedDocument
)
from app.parsers.text import normalize_document_text


class PdfDocumentParser(BaseDocumentParser):
    """Extract text from searchable PDF documents."""

    supported_extensions = frozenset({".pdf"})

    def parse(self, *, content: bytes, filename: str) -> ParsedDocument:
        """Extract and normalize text from a PDF document."""

        try:
            reader = PdfReader(BytesIO(content))
        except (PdfReadError, ValueError, OSError) as error:
            raise InvalidDocumentError("The PDF document is corrupted or invalid.") from error

        if reader.is_encrypted:
            raise EncryptedDocumentError("Password-protected PDF documents are not supported.")
        text_parts: list[str] = []

        try:
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text)
        except (PdfReadError, KeyError, ValueError) as error:
            raise InvalidDocumentError("Text could not be extracted from the PDF document.") from error

        text = normalize_document_text("\n".join(text_parts))

        if not text:
            raise EmptyDocumentError("No text was found in the PDF. The document may be scanned and require OCR.")

        return ParsedDocument(
            filename=filename,
            document_format=DocumentFormat.PDF,
            text=text,
            page_count=len(reader.pages),
        )
