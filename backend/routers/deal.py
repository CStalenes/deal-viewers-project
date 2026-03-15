from fastapi import APIRouter, Request, HTTPException, Body, Path, Query
from typing import Optional
from bson import ObjectId
from bson.errors import InvalidId
from backend.services.deal_service import DealService, apply_template_projection

try:
    from backend.models.deal import DealModel
except ImportError:
    DealModel = None

router = APIRouter(prefix="/deals", tags=["deals"])

@router.post("/", status_code=201)
def create_deal(request: Request, deal_data: dict = Body(...)):
    service = DealService(request.app.database)
    res = service.create(deal_data)
    return {"id": str(res.inserted_id)}

@router.get("/")
def list_deals(
    request: Request, 
    clientName: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None)
):
    service = DealService(request.app.database)
    deals = service.get_all(clientName, startDate, endDate)
    for d in deals:
        d["_id"] = str(d["_id"])
    return deals

@router.get("/{id}")
def get_deal(request: Request, id: str = Path(...)):
    service = DealService(request.app.database)
    
    query_id = ObjectId(id) if ObjectId.is_valid(id) else id
    
    deal = service.get_by_id(str(query_id))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal nnot found")
    
    deal["_id"] = str(deal["_id"])
    return deal

@router.put("/{id}")
def update_deal(request: Request, id: str = Path(...), update_data: dict = Body(...)):
    service = DealService(request.app.database)
    try:
        res = service.update(id, update_data)
    except:
         raise HTTPException(status_code=400, detail="Error occurred during update")
         
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deal not found")
    return {"message": "Deal updated successfully"}

@router.delete("/{id}")
def delete_deal(request: Request, id: str = Path(...)):
    service = DealService(request.app.database)
    res = service.delete(id)
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deal not found")
    return {"message": "Deal deleted"}

@router.get("/{deal_id}/view")
def get_projected_deal(request: Request, deal_id: str, templateId: str):
    db = request.app.database

    query_deal_id = ObjectId(deal_id) if ObjectId.is_valid(deal_id) else deal_id
    deal = db["deals"].find_one({"_id": query_deal_id})
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    query_template_id = ObjectId(templateId) if ObjectId.is_valid(templateId) else templateId
    template = db["templates"].find_one({"_id": query_template_id})
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    visible_fields = template.get("visibleFields") or template.get("projectedFields") or []
    
    deal["_id"] = str(deal["_id"])
    
    return apply_template_projection(deal, visible_fields)