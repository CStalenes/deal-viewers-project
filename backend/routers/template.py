"""
Template routes:
  GET /templates          → lists all active templates
  GET /templates/{code}   → details of a template by its code
"""
from fastapi import APIRouter, Request, HTTPException, Body

from models.template import TemplateModel
from services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])

@router.get("/")
def list_templates(request: Request):
    """ List all actives displaying templates """
    service = TemplateService(request.app.database)
    templates = service.get_all()
    for t in templates:
        t["_id"] = str(t["_id"])
    return templates

@router.get("/{id}")
def get_template(request: Request, id: str):
    service = TemplateService(request.app.database)
    template = service.get_by_id(id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template["_id"] = str(template["_id"])
    return template

@router.post("/", status_code=201)
def create_template(request: Request, template: TemplateModel = Body(...)):
    service = TemplateService(request.app.database)
    data = template.model_dump(by_alias=True, exclude={"id"})
    res = service.create(data)
    return {"id": str(res.inserted_id)}






