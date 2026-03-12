"""
TemplateService — business logic layer for templates.
"""
from pymongo.database import Database
from typing import Optional


class TemplateService:

    def __init__(self, db: Database):
        self.collection = db["templates"]

    def get_all(self) -> list:
        """Returns all active templates."""
        return list(self.collection.find({"isActive": True}))

    def get_by_id(self, template_id: str) -> Optional[dict]:
        """Returns a template by its _id."""
        return self.collection.find_one({"_id": template_id})

    def create(self, template_data: dict) -> dict:
        result = self.collection.insert_one(template_data)
        return self.collection.find_one({"_id": result.inserted_id})