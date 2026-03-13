from fastapi import APIRouter, Request, HTTPException, Body, Path
from typing import Optional, List
from backend.services.deal_service import DealService

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
    clientName: Optional[str] = None,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None
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