from pydantic import BaseModel, Field
from typing import Optional

class DataChunk(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: str

# ده كلاس إضافي هنستخدمه بعدين لما نيجي نبحث في الـ Vector DB
class RetrievalDocument(BaseModel):
    text: str
    score: float