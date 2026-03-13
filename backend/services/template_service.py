"""
TemplateService — business logic layer for templates.
"""
from pymongo.database import Database
from typing import Optional
from bson import ObjectId



class TemplateService:

    def __init__(self, db):
        self.db = db

    def get_all(self):
        templates = list(self.db["templates"].find())
        for t in templates:
            t["_id"] = str(t["_id"])
        return templates

    def get_by_id(self, template_id: str):
        return self.db["templates"].find_one({"_id": ObjectId(template_id)})

    def create(self, template_data: dict):
        return self.db["templates"].insert_one(template_data)

    def update(self, template_id: str, update_data: dict):
        return self.db["templates"].update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )

    def delete(self, template_id: str):
        return self.db["templates"].delete_one({"_id": ObjectId(template_id)})