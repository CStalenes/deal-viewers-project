from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Section(BaseModel):
    name: str
    fields: List[str]

class TemplateModel(BaseModel):
    """
    A display template specifies:
    - which deal fields are visible (visibleFields)
    - how to group them into sections (sections)
    - how to label them (labels)

    """

    id: Optional[str] = Field(None, alias="_id") 
    name: str
    code: str                         # ex: FINANCE_VIEW, COMMERCIAL_VIEW
    description: Optional[str] = None
    isActive: bool = True
    visibleFields: List[str] = []  # list of permitted fields
    sections: List[Section] = []   # visual grouping
    labels: Dict[str, str] = {}    # field name translations


    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True