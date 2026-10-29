from __future__ import annotations

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    OpenAIError,
    RateLimitError
)
from pydantic import BaseModel

from app.llm.base import (
    ResponseModel,
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnavailableError,
    StructuredResponseError,
)


class OpenAIStructuredLLM:
    """Generate responses through the OpenAI Response API."""

    def __init__(self, *, api_key: str, model: str, timeout_seconds: float = 30.0, max_retries: int = 2) -> None:
        if not api_key.strip():
            raise LLMConfigurationError("OpenAi API key is required")
        if not model.strip():
            raise LLMConfigurationError("OpenAI model is required")
        self._model = model
        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )

    async def parse(
            self, *, system_prompt: str, user_prompt: str, response_model: type[ResponseModel]
    ) -> ResponseModel:
        """generate a response and parse it into a Pydantic model."""

        if not system_prompt.strip():
            raise ValueError("system_prompt cannot be empty")
        if not user_prompt.strip():
            raise ValueError("user_prompt cannot be empty")
        try:
            response = await self._client.responses.parse(
                model=self._model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=response_model,
            )
        except AuthenticationError as error:
            raise LLMAuthenticationError("The LLM provider rejected the API credentials.") from error
        except APITimeoutError as error:
            raise LLMTimeoutError("The LLM request timed out.") from error
        except RateLimitError as error:
            raise LLMRateLimitError("The LLM request was rate limited.") from error
        except APIConnectionError as error:
            raise LLMUnavailableError("The LLM provider could not be reached.") from error
        except BadRequestError as error:
            raise StructuredResponseError("The LLM request or response is invalid.") from error
        except APIStatusError as error:
            raise LLMUnavailableError(f"The LLM provider returned HTTP {error.status_code}.") from error
        except OpenAIError as error:
            raise LLMUnavailableError("The LLM provider returned an unexpected error.") from error

        parsed_result = response.output_parsed
        if parsed_result is None:
            raise StructuredResponseError(
                "The model returned no structured result. "
                "The response may have been refused or incomplete."
            )
        if not isinstance(parsed_result, response_model):
            raise StructuredResponseError("The parsed result does not match the requested model.")
        return parsed_result

