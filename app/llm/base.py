from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

class LLMError(Exception):
    """Base exception for all LLM errors."""


class LLMConfigurationError(LLMError):
    """Exception raised when the LLM client is incorrectly configured."""


class LLMAuthenticationError(LLMError):
    """Exception raised when the LLM provider rejects API credentials."""


class LLMTimeoutError(LLMError):
    """Exception raised when the LLM does not respond in time."""


class LLMRateLimitError(LLMError):
    """Exception raised when the LLM provider rate limit is exceeded."""


class LLMUnavailableError(LLMError):
    """Exception raised when the LLM provider is unavailable."""


class StructuredResponseError(LLMError):
    """Raised when the model does not return a valid structured response."""


class LLMRejectionError(LLMError):
    """Exception raised when the model deny to process the input."""


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)

class StructuredLLM(Protocol):
    """Define an interface for LLM responses."""

    async def parse(
            self, *, system_prompt: str, user_prompt: str, response_model: type[ResponseModel]
    ) -> ResponseModel:
        """Generate and validate a response against a Pydantic model."""