from bson import ObjectId
from typing import Optional, List, Dict, Any

class DealService:
    def __init__(self, db):
        self.db = db
        self.collection = db["deals"]

    def create(self, deal_data: Dict[str, Any]):
        return self.collection.insert_one(deal_data)

    def get_all(self, client_name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
        query = {}

        if client_name:
            query["clientName"] = {"$regex": client_name, "$options": "i"}

        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["createdAt"] = date_query

        return list(self.collection.find(query))

    def get_by_id(self, deal_id: str):
        query_id = ObjectId(deal_id) if ObjectId.is_valid(deal_id) else deal_id
        return self.collection.find_one({"_id": query_id})

    def update(self, deal_id: str, update_data: Dict[str, Any]):
        query_id = ObjectId(deal_id) if ObjectId.is_valid(deal_id) else deal_id
        return self.collection.update_one({"_id": query_id}, {"$set": update_data})

    def delete(self, deal_id: str): 
        query_id = ObjectId(deal_id) if ObjectId.is_valid(deal_id) else deal_id
        return self.collection.delete_one({"_id": query_id})


def apply_template_projection(deal: Dict[str, Any], visible_fields: List[str]) -> Dict[str, Any]:
    
    if not visible_fields:
        return deal

    projected_deal = {}

    if "_id" in deal:
        projected_deal["_id"] = str(deal["_id"])

    for field_path in visible_fields:
        parts = field_path.split('.')
        current_data = deal
        
        found = True
        for part in parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                found = False
                break
        
        if found:
            projected_deal[field_path] = current_data

    return projected_deal