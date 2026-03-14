from fastapi import APIRouter, Request, HTTPException, Body, Path, Query
from typing import Optional
from bson import ObjectId
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
    try:
        deal = service.get_by_id(id)
    except:
        raise HTTPException(status_code=400, detail="Format d'ID invalide")
        
    if not deal:
        raise HTTPException(status_code=404, detail="Deal non trouvé")
    
    deal["_id"] = str(deal["_id"])
    return deal

@router.put("/{id}")
def update_deal(request: Request, id: str = Path(...), update_data: dict = Body(...)):
    service = DealService(request.app.database)
    try:
        res = service.update(id, update_data)
    except:
         raise HTTPException(status_code=400, detail="Erreur lors de la mise à jour")
         
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deal non trouvé")
    return {"message": "Deal mis à jour avec succès"}

@router.delete("/{id}")
def delete_deal(request: Request, id: str = Path(...)):
    service = DealService(request.app.database)
    res = service.delete(id)
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deal non trouvé")
    return {"message": "Deal supprimé"}

@router.get("/{deal_id}/view")
def get_projected_deal(request: Request, deal_id: str, templateId: str):
    db = request.app.database

    deal = db["deals"].find_one({"_id": ObjectId(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal non trouvé")

    template = db["templates"].find_one({"_id": ObjectId(templateId)})
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")

    visible_fields = template.get("visibleFields", [])
    deal["_id"] = str(deal["_id"])
    
    return apply_template_projection(deal, visible_fields)