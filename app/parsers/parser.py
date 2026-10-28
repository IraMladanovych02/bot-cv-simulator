from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence

from app.parsers.base import (
    BaseDocumentParser,
    EmptyDocumentError,
    ParsedDocument,
    DocumentTooLargeError,
    UnsupportedDocumentError
)
from app.parsers.docx import DocxDocumentParser

from app.parsers.pdf import PdfDocumentParser
from app.parsers.text import TextDocumentParser


DEFAULT_MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024


class InvalidFilenameError(ValueError):
    """Raised when an uploaded document has no valid filename."""


class DocumentParser:
    """Select a format-specific parser and extract normalized document text."""

    def __init__(
        self,
        parsers: Sequence[BaseDocumentParser] | None = None,
        max_file_size_bytes: int = DEFAULT_MAX_DOCUMENT_SIZE_BYTES,
    ) -> None:
        if max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be greater than zero")

        # Parser order follows the implementation plan:
        # TXT first, DOCX second, and PDF third.
        self._parsers = tuple(
            parsers or (TextDocumentParser(), DocxDocumentParser(), PdfDocumentParser(),)
        )
        self._max_file_size_bytes = max_file_size_bytes

    @property
    def supported_extensions(self) -> frozenset[str]:
        """Return all file extensions supported by registered parsers."""

        return frozenset(
            extension
            for parser in self._parsers
            for extension in parser.supported_extensions
        )

    def parse(self, *, content: bytes, filename: str) -> ParsedDocument:
        """Validate an uploaded file and extract normalized text."""

        normalized_filename = filename.strip()

        if not normalized_filename:
            raise InvalidFilenameError("The document filename cannot be empty.")
        if not content:
            raise EmptyDocumentError("The uploaded document is empty.")

        if len(content) > self._max_file_size_bytes:
            max_size_mb = (self._max_file_size_bytes / 1024 / 1024)
            raise DocumentTooLargeError(f"The document exceeds the {max_size_mb:g} MB limit.")

        extension = Path(normalized_filename).suffix.lower()

        for parser in self._parsers:
            if parser.supports(extension):
                return parser.parse(content=content, filename=normalized_filename)

        supported_formats = ", ".join(sorted(self.supported_extensions))
        raise UnsupportedDocumentError(
            "Unsupported document format. "
            f"Supported extensions: {supported_formats}."
        )
