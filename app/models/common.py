from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchemaModel(BaseModel):
    """Provide shared validation settings for all application models."""
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class EvidenceSourceType(StrEnum):
    """Define the supported origins of facts used by the application."""

    RESUME = "resume"
    CV = "cv"
    VACANCY = "vacancy"
    MARKET_DATA = "market_data"
    USER_INPUT = "user_input"
    RAG = "rag"
    LLM_INTERFACE = "llm_interface"
    INTERVIEW_ANSWER = "interview_answer"


class SourceReference(BaseSchemaModel):
    """Reference the source that supports a skill, requirement or recommendation."""

    reference_id: str = Field(
        min_length=1,
        description="Unique identifier of the source.",
    )
    source_type: EvidenceSourceType
    source_name: str | None = Field(
        default=None,
        description="Name of the source"
    )
    fragment: str | None = Field(
        default=None,
        description="The part of the source that confirms the claim"
    )
    url: str | None = Field(
        default=None,
        description="Optional URL of the original source.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional source-specific metadata.",
    )
