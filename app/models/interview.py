from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import Field, model_validator

from app.models.common import BaseSchemaModel, SourceReference
from app.models.vacancy import SkillMatchStatus


class InterviewStatus(StrEnum):
    """Define the lifecycle status of an interview session."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionDifficulty(StrEnum):
    """Define the supported interview question difficulty levels."""

    BEGINNER = "beginner"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"


class QuestionType(StrEnum):
    """Define the supported interview question formats."""

    TECHNICAL_THEORY = "technical_theory"
    PRACTICAL = "practical"
    DEBUGGING = "debugging"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    PROJECT_DEEP_DIVE = "project_deep_dive"


class AdaptationAction(StrEnum):
    """Define how the next interview question should be adapted."""

    INCREASE_DIFFICULTY = "increase_difficulty"
    KEEP_DIFFICULTY = "keep_difficulty"
    DECREASE_DIFFICULTY = "decrease_difficulty"
    ASK_FOLLOW_UP = "ask_follow_up"
    CHANGE_TOPIC = "change_topic"
    FINISH_INTERVIEW = "finish_interview"


class EvaluationCriterion(BaseSchemaModel):
    """Represent one criterion used to evaluate an interview answer."""

    criterion: str
    weight: float = Field(
        default=1.0,
        gt=0.0,
    )
    description: str | None = None


class InterviewQuestion(BaseSchemaModel):
    """Represent an interview question with topic, difficulty, and rubric."""

    question_id: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    difficulty: QuestionDifficulty
    question_type: QuestionType
    question: str = Field(min_length=1)

    expected_points: list[EvaluationCriterion] = Field(
        default_factory=list,
    )
    related_skill_gaps: list[str] = Field(
        default_factory=list,
    )
    supporting_sources: list[SourceReference] = Field(
        default_factory=list,
    )


class InterviewAnswer(BaseSchemaModel):
    """Represent a candidate answer submitted during an interview."""

    question_id: str
    answer_text: str = Field(min_length=1)
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class AnswerEvaluation(BaseSchemaModel):
    """Represent the rubric-based evaluation of a candidate answer."""

    question_id: str
    score: float = Field(ge=0.0)
    max_score: float = Field(gt=0.0)

    strengths: list[str] = Field(
        default_factory=list,
    )
    missing_points: list[str] = Field(
        default_factory=list,
    )
    feedback: str

    next_action: AdaptationAction
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    @model_validator(mode="after")
    def validate_score(self) -> "AnswerEvaluation":
        """Ensure the answer score does not exceed the maximum score."""

        if self.score > self.max_score:
            raise ValueError(
                "score cannot exceed max_score"
            )
        return self


class InterviewTurn(BaseSchemaModel):
    """Represent one complete question-and-answer cycle."""

    question: InterviewQuestion
    answer: InterviewAnswer | None = None
    evaluation: AnswerEvaluation | None = None


class InterviewSession(BaseSchemaModel):
    """Represent an adaptive interview session and its accumulated progress."""

    session_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    target_role: str = Field(min_length=2)
    target_seniority: str | None = None

    status: InterviewStatus = InterviewStatus.CREATED
    current_topic: str | None = None
    current_difficulty: QuestionDifficulty = QuestionDifficulty.JUNIOR

    planned_question_count: int = Field(
        default=10,
        ge=3,
        le=30,
    )
    turns: list[InterviewTurn] = Field(
        default_factory=list,
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None


class InterviewReport(BaseSchemaModel):
    """Represent the final evidence-based result of an interview session."""

    session_id: str
    target_role: str
    total_score: float = Field(
        ge=0.0,
        le=100.0,
    )

    strong_topics: list[str] = Field(
        default_factory=list,
    )
    weak_topics: list[str] = Field(
        default_factory=list,
    )
    recommendations: list[str] = Field(
        default_factory=list,
    )
    answer_evaluations: list[AnswerEvaluation] = Field(
        default_factory=list,
    )
    limitations: list[str] = Field(
        default_factory=list,
    )


class SkillGapPriority(StrEnum):
    """Define how urgently the candidate should address a skill gap."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SkillGap(BaseSchemaModel):
    """Represent a skill that is missing or weakly demonstrated in the resume."""

    skill_name: str = Field(min_length=1)
    status: SkillMatchStatus
    priority: SkillGapPriority

    reason: str = Field(
        min_length=1,
        description="Why this skill matters for the target role.",
    )
    current_evidence: list[SourceReference] = Field(
        default_factory=list,
    )
    market_evidence: list[SourceReference] = Field(
        default_factory=list,
    )

    recommendation: str = Field(
        min_length=1,
        description="Specific action the candidate can take.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )
    requires_review: bool = False


class ResumeImprovement(BaseSchemaModel):
    """Describe a factual and actionable resume improvement."""

    section: str
    problem: str
    recommendation: str
    supporting_sources: list[SourceReference] = Field(
        default_factory=list,
    )
    requires_user_input: bool = False


class LearningStep(BaseSchemaModel):
    """Represent one ordered learning activity for closing a skill gap."""

    order: int = Field(ge=1)
    title: str
    description: str
    related_skills: list[str] = Field(
        default_factory=list,
    )
    completion_criteria: list[str] = Field(
        default_factory=list,
    )
    estimated_hours: int | None = Field(
        default=None,
        ge=1,
    )


class SkillGapAnalysis(BaseSchemaModel):
    """Represent the complete evidence-based candidate gap analysis."""

    target_role: str = Field(min_length=2)
    target_seniority: str | None = None
    overall_assessment: str

    demonstrated_strengths: list[str] = Field(
        default_factory=list,
    )
    skill_gaps: list[SkillGap] = Field(
        default_factory=list,
    )
    resume_improvements: list[ResumeImprovement] = Field(
        default_factory=list,
    )
    learning_plan: list[LearningStep] = Field(
        default_factory=list,
    )
    interview_focus: list[str] = Field(
        default_factory=list,
    )
    limitations: list[str] = Field(
        default_factory=list,
    )