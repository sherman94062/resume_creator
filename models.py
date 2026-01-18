from pydantic import BaseModel, Field
from typing import List

class JobAnalysis(BaseModel):
    responsibilities: List[str] = Field(description="Top 5-7 key responsibilities")
    skills: List[str] = Field(description="Required technical skills and tools")
    keywords: List[str] = Field(description="Important ATS keywords")
    experience_requirements: str = Field(description="Required years/level of experience")
    success_metrics: List[str] = Field(description="Quantifiable metrics mentioned")

class ReflectionCritique(BaseModel):
    match_score: int = Field(description="Score from 0-100 on how well the resume matches the JD")
    critique_points: List[str] = Field(description="Specific areas where the resume is weak or missing keywords")
    hallucination_check: bool = Field(description="True if the LLM added experience not found in the original resume")
    needs_revision: bool = Field(description="Whether a second pass is required to improve the resume")