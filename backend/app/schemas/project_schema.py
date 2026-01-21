from pydantic import BaseModel
from typing import Optional


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
