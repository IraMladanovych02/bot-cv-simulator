from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from app.models.common import BaseSchemaModel, SourceReference


class RequirementImportance(StrEnum):
    """Describe whether a vacancy requirement is mandatory or optional."""

    REQUIRED = "required"
    PREFERRED = "preferred"
    CONTEXT = "context"
    UNKNOWN = "unknown"


class VacancyRequirement(BaseSchemaModel):
    """Represent a normalized skill requirement found in a vacancy."""

    skill_name: str = Field(min_length=1)
    importance: RequirementImportance
    required_years: float | None = Field(
        default=None,
        ge=0.0,
    )
    description: str | None = None
    source: SourceReference


class Vacancy(BaseSchemaModel):
    """Represent a vacancy prepared for matching and RAG indexing."""

    vacancy_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str | None = None
    seniority: str | None = None
    location: str | None = None
    description: str
    requirements: list[VacancyRequirement] = Field(
        default_factory=list,
    )
    responsibilities: list[str] = Field(
        default_factory=list,
    )

    source_url: str | None = None
    source_name: str | None = None


class MarketSkillRequirement(BaseSchemaModel):
    """Describe how frequently a skill appears in relevant vacancies."""

    skill_name: str = Field(min_length=1)
    vacancy_count: int = Field(ge=0)
    total_vacancies: int = Field(gt=0)
    frequency: float = Field(
        ge=0.0,
        le=1.0,
    )
    required_count: int = Field(
        default=0,
        ge=0,
    )
    preferred_count: int = Field(default=0, ge=0)
    sources: list[SourceReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_counts(self) -> "MarketSkillRequirement":
        """Ensure aggregated counts do not exceed the vacancy total."""

        if self.vacancy_count > self.total_vacancies:
            raise ValueError("vacancy_count cannot exceed total_vacancies")
        if self.required_count + self.preferred_count > self.vacancy_count:
            raise ValueError("required_count and preferred_count cannot exceed vacancy_count")
        return self


class MarketRoleProfile(BaseSchemaModel):
    """Represent aggregated market requirements for a target role."""

    target_role: str = Field(min_length=2)
    seniority: str | None = None
    analyzed_vacancies: int = Field(ge=0)
    skill_requirements: list[MarketSkillRequirement] = Field(default_factory=list)
    common_responsibilities: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class SkillCategory(StrEnum):
    """Define categories used to organize candidate skills."""

    PROGRAMMING_LANGUAGE = "programming language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    DEVOPS = "devops"
    DATA = "data"
    AI = "ai"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    TOOL = "tool"
    SOFT_SKILL = "soft skill"
    LANGUAGE = "language"
    OTHER = "other"


class EvidenceStrength(StrEnum):
    """Describe how strongly a source confirms that a candidate has a skill."""

    NONE = "none"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class SkillMatchStatus(StrEnum):
    """Describe how a CV skill matches a market requirement."""

    CONFIRMED = "confirmed"
    WEAK_EVIDENCE = "weak_evidence"
    MISSING = "missing"
    NOT_RELEVANT = "not_relevant"
    REQUIRES_REVIEW = "requires_review"


class StandardizedSkill(BaseSchemaModel):
    """Represents a standardized skill."""

    name: str = Field(
        min_length=1,
        description="Normalized skill name",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names for this skill",
    )
    category: SkillCategory = SkillCategory.OTHER
    description: str | None = None


class SkillEvidence(BaseSchemaModel):
    """Describe CV evidence supporting a candidate skill."""

    skill_name: str = Field(
        min_length=1,
        description="Normalized skill name",
    )
    strength: EvidenceStrength
    evidence: list[SourceReference] = Field(
        default_factory=list,
        description="CV fragments supporting the detected skill.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=0.0,
        description="Confidence that the skill is correctly identifies.",
    )


class SkillMatch(BaseSchemaModel):
    """Represent the comprasion between a candidate skill and a role requirement."""

    skill_name: str
    status: SkillMatchStatus
    candidate_evidence: list[SkillEvidence] = Field(default_factory=list)
    market_sources: list[SourceReference] = Field(default_factory=list)
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )
    explanation: str | None = None