from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class OutputType(str, Enum):
    """Supported output formats for optimized prompts."""
    MARKDOWN = "markdown"
    XML = "xml"


class MakeupRequest(BaseModel):
    """Request model for prompt optimization."""

    input_prompt: str = Field(..., min_length=1, description="The prompt to optimize")
    output_type: OutputType = Field(
        default=OutputType.MARKDOWN,
        description="Output format: 'markdown' or 'xml'"
    )


class MakeupResponse(BaseModel):
    """Response model for optimized prompt."""

    output_prompt: str = Field(..., description="The optimized prompt")
    skill_used: str = Field(..., description="Which skill was applied")
    iterations: int = Field(..., description="Number of optimization passes used")


class SkillSummary(BaseModel):
    """Public skill metadata exposed by the API."""

    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="One-line skill summary")


class SkillsResponse(BaseModel):
    """Response model for the skills listing endpoint."""

    skills: list[SkillSummary] = Field(..., description="Available skills with one-line descriptions")
