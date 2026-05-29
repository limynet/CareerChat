"""Pydantic model for structured candidate data extracted from military documents."""
from pydantic import BaseModel


class Candidate(BaseModel):
    name: str
    rank: str | None = None
    branch: str | None = None
    mos: str | None = None
    education: list[str] | None = None
    assignments: list[str] | None = None
    skills: list[str] | None = None
    certifications: list[str] | None = None
    years_of_service: int | None = None
    deployments: list[str] | None = None
    awards: list[str] | None = None
    raw_text: str
    source_file: str
