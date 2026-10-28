from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class DocumentParserError(Exception):
    """Base exception for all document parsing errors."""


class UnsupportedDocumentError(DocumentParserError):
    """Raised when the uploaded document format is not supported."""


class InvalidDocumentError(DocumentParserError):
    """Raised when a document is corrupted or cannot be parsed."""


class EmptyDocumentError(DocumentParserError):
    """Raised when no useful text can be extracted from a document."""


class DocumentTooLargeError(DocumentParserError):
    """Raised when the uploaded document exceeds the configured size limit."""


class EncryptedDocumentError(DocumentParserError):
    """Raised when a document is password-protected."""


class DocumentFormat(StrEnum):
    """Define document formats supported by the parser."""

    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """Represents normalized text extracted from an uploaded document."""

    filename: str
    document_format: DocumentFormat
    text: str
    page_count: int | None = None


class BaseDocumentParser(ABC):
    """Define the interface implemented by every parser."""

    supported_extensions: frozenset[str]

    def supports(self, extension: str) -> bool:
        """Return whether the parser supports the given file extension."""

        return extension.lower() in self.supported_extensions

    @abstractmethod
    def parse(self, *, content: bytes, filename: str) -> ParsedDocument:
        """Extract normalized text from a document."""