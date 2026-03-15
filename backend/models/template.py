from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime, timezone

class Section(BaseModel):
    name: str
    fields: List[str]

class TemplateModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    name: str
    code: str                        
    description: Optional[str] = None
    isActive: bool = True
    visibleFields: List[str] = []
    sections: List[Section] = []
    labels: Dict[str, str] = {}

    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))