from __future__ import annotations

from app.llm.base import StructuredLLM
from app.llm.prompts.prompts import RESUME_EXTRACTION_SYSTEM_PROMPT
from app.llm.schemas import ExtractedResume
from app.models.common import EvidenceSourceType, SourceReference
from app.models.cv import EducationItem, ExperienceItem, ProjectItem, ResumeProfile
from app.models.vacancy import SkillEvidence


MIN_CV_TEXT_LENGTH = 50
MAX_CV_TEXT_LENGTH = 100_000


class ResumeExtractor:
    """Extract a structured and evidence-based profile from resume text."""

    def __init__(self, llm: StructuredLLM) -> None:
        self._llm = llm

    async def extract(self, resume_text) -> ResumeProfile:
        """Extract and validate a candidate profile from resume text."""

        normalized_text = resume_text.strip()
        if len(normalized_text) < MIN_CV_TEXT_LENGTH:
            raise ValueError("Resume text is too short to analyze.")
        if len(normalized_text) > MAX_CV_TEXT_LENGTH:
            raise ValueError("Resume text is too long to analyze.")

        extracted_resume = await self._llm.parse(
            system_prompt=RESUME_EXTRACTION_SYSTEM_PROMPT,
            user_prompt=self._build_user_prompt(normalized_text),
            response_model=ExtractedResume,
        )
        return self._to_domain_model(extracted_resume)

    @staticmethod
    def _build_user_prompt(resume_text: str) -> str:
        """Wrap resume text in precise format."""

        return (
            "Extract factual candidate information from the resume "
            "inside the RESUME_DATA block.\n\n"
            "<RESUME_DATA>\n"
            f"{resume_text}\n"
            "</RESUME_DATA>"
        )

    @staticmethod
    def _to_domain_model(extracted: ExtractedResume) -> ResumeProfile:
        """Convert the LLM transport schema into the domain model."""

        skills: list[SkillEvidence] = []
        for skill_index, extracted_skill in enumerate(
            extracted.skills,
            start=1,
        ):
            references = [
                SourceReference(
                    reference_id=(
                        f"resume-skill-{skill_index}"
                        f"-evidence-{evidence_index}"
                    ),
                    source_type=EvidenceSourceType.RESUME,
                    source_name="Uploaded resume",
                    excerpt=evidence_text,
                )
                for evidence_index, evidence_text in enumerate(
                    extracted_skill.evidence,
                    start=1,
                )
            ]

            skills.append(
                SkillEvidence(
                    skill_name=extracted_skill.name,
                    strength=extracted_skill.strength,
                    evidence=references,
                    confidence=extracted_skill.confidence,
                )
            )

        experience = [
            ExperienceItem(
                role=item.role,
                company=item.company,
                period=item.period,
                responsibilities=item.responsibilities,
                achievements=item.achievements,
                technologies=item.technologies,
            )
            for item in extracted.experience
        ]

        projects = [
            ProjectItem(
                name=item.name,
                description=item.description,
                technologies=item.technologies,
                achievements=item.achievements,
                url=item.url,
            )
            for item in extracted.projects
        ]

        education = [
            EducationItem(
                institution=item.institution,
                degree=item.degree,
                field_of_study=item.field_of_study,
                period=item.period,
                details=item.details,
            )
            for item in extracted.education
        ]

        return ResumeProfile(
            candidate_name=extracted.candidate_name,
            headline=extracted.headline,
            summary=extracted.summary,
            years_of_experience=extracted.years_of_experience,
            skills=skills,
            experience=experience,
            projects=projects,
            education=education,
            languages=extracted.languages,
        )
