from pydantic import BaseModel
from typing import List


class ProjectCreate(BaseModel):
    title: str

    description: str

    objective: str

    requirements: str

    domain: str

    year_from: int

    year_to: int

    preferred_sources: List[str]