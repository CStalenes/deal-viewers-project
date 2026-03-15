from bson import ObjectId
from datetime import datetime

class DealService:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["deals"]

    def create(self, deal_data: dict):
        deal_data["createdAt"] = datetime.utcnow().isoformat()
        return self.collection.insert_one(deal_data)

    def get_all(self, client_name: str = None, start_date: str = None, end_date: str = None):
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
        return self.collection.find_one({"_id": ObjectId(deal_id)})

    def update(self, deal_id: str, update_data: dict):
        update_data["updatedAt"] = datetime.utcnow().isoformat()
        return self.collection.update_one(
            {"_id": ObjectId(deal_id)}, 
            {"$set": update_data}
        )

    def delete(self, deal_id: str):
        return self.collection.delete_one({"_id": ObjectId(deal_id)})
    

def apply_template_projection(deal: dict, visible_fields: list):
    
    projected_data = {}

    for path in visible_fields:
        parts = path.split('.')
        current_value = deal
        
        for part in parts:
            if isinstance(current_value, dict):
                current_value = current_value.get(part)
            else:
                current_value = None
                break
        
        if current_value is not None:
            projected_data[path] = current_value

    return projected_data