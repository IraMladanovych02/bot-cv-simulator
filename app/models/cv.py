from __future__ import annotations

from pydantic import Field

from app.models.common import BaseSchemaModel
from app.models.vacancy import SkillEvidence


class ExperienceItem(BaseSchemaModel):
    """Represents one experience item from CV."""

    role: str = Field(
        min_length=1,
        description="Candidate role or job title.",
    )
    company: str | None = None
    period: str | None = Field(
        default=None,
        description="Employment period.",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
    )
    achievements: list[str] = Field(
        default_factory=list,
    )
    technologies: list[str] = Field(
        default_factory=list,
    )


class ProjectItem(BaseSchemaModel):
    """Represents one personal or commercial project from CV."""

    name: str = Field(min_length=1)
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    url: str | None = None


class EducationItem(BaseSchemaModel):
    """Represents education or a professional training program from CV."""

    university: str = Field(min_length=1)
    degree: str | None = None
    field_of_study: str | None = None
    period: str | None = None
    details: list[str] = Field(default_factory=list)


class ResumeProfile(BaseSchemaModel):
    """Represents all candidate information from CV."""

    candidate_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    years_of_experience: float | None = Field(default=None, ge=0.0)
    skills: list[SkillEvidence] = Field(default_factory=list)
    experiences: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    educations: list[EducationItem] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


class CandidatePreferences(BaseSchemaModel):
    """Represents the candidate's target role and interview preferences."""

    target_role: str = Field(min_length=2)
    target_seniority: str | None = None
    interview_language: str = "uk"
    interview_question_count: int = Field(
        default=10,
        ge=3,
        le=30,
    )