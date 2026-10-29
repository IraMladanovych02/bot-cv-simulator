from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.vacancy import EvidenceStrength


class LLMResponseModel(BaseModel):
    """Provide strict validation for all LLM response models."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ExtractedSkill(LLMResponseModel):
    """Represent a sill extracted from CV text."""

    name: str = Field(description="Normalized skill name.")
    strength: EvidenceStrength
    evidence: list[str] = Field(description="Fragments that prove the skill.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the skill is supported by the CV."
    )

    @model_validator(mode="after")
    def validate_evidence(self) -> "ExtractedSkill":
        """Ensure every extracted skill has at least one proving fact."""

        if not self.evidence:
            raise ValueError("Every extracted skill must include evidence.")
        return self


class ExtractedExperience(LLMResponseModel):
    """Represent one employment entry extracted from CV text."""

    role: str
    company: str | None
    period: str | None
    responsibilities: list[str]
    achievements: list[str]
    technologies: list[str]


class ExtractedProject(LLMResponseModel):
    """Represent personal or commercial project from CV."""

    name: str
    description: str | None
    technologies: list[str]
    achievements: list[str]
    url: str | None


class ExtractedEducation(LLMResponseModel):
    """Represent an education section from CV."""

    university: str
    degree: str | None
    field_of_study: str | None
    period: str | None
    details: list[str]


class ExtractedResume(LLMResponseModel):
    """Represent all information extracted from CV."""

    candidate_name: str | None
    headline: str | None
    summary: str | None
    years_of_experience: float | None
    skills: list[ExtractedSkill]
    experience: list[ExtractedExperience]
    projects: list[ExtractedProject]
    education: list[ExtractedEducation]
    languages: list[str] | None

