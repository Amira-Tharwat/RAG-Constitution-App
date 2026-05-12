from pydantic import BaseModel, Field
from typing import Optional

class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str