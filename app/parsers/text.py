from __future__ import annotations

from app.parsers.base import (
    BaseDocumentParser,
    DocumentFormat,
    EmptyDocumentError,
    InvalidDocumentError,
    ParsedDocument
)


class TextDocumentParser(BaseDocumentParser):
    """Extracts plain text from TXT documents."""

    supported_extensions = frozenset({".txt"})

    def parse(self, *, content: bytes, filename: str) -> ParsedDocument:
        """Decode and normalize text document."""

        try:
            # Use utf-8-sig instead of utf-8: it strips the BOM (\ufeff) that Windows
            # editors such as Notepad add, and behaves like plain utf-8 when no BOM exists.
            raw_text = content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise InvalidDocumentError("The TXT document must use UTF-8 encoding") from error

        text = normalize_document_text(raw_text)
        if not text:
            raise EmptyDocumentError("The TXT document must not be empty.")
        return ParsedDocument(
            filename=filename,
            document_format=DocumentFormat.TXT,
            text=text,
        )


def normalize_document_text(text: str) -> str:
    """Normalize whitespace while keeping the meaningful line breaks."""

    normalized_lines: list[str] = []
    for line in text.splitlines():
        normalized_line = " ".join(line.split())
        if normalized_line:
            normalized_lines.append(normalized_line)

    return "\n".join(normalized_lines).strip()
