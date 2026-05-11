from pydantic import BaseModel, Field
from typing import Optional

class Project(BaseModel):
    # الـ ID بتاع MongoDB
    id: Optional[str] = Field(default=None, alias="_id")
    # اسم أو معرف المشروع (زي اسم ملف الـ PDF)
    project_id: str