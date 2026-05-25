from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/step1", response_class=HTMLResponse)
def step1(request: Request):
    return templates.TemplateResponse(request=request, name="step1_upload.html")


@router.get("/step2", response_class=HTMLResponse)
def step2(request: Request):
    return templates.TemplateResponse(request=request, name="step2_dbscan.html")


@router.get("/step3", response_class=HTMLResponse)
def step3(request: Request):
    return templates.TemplateResponse(request=request, name="step3_ahp.html")


@router.get("/step4", response_class=HTMLResponse)
def step4(request: Request):
    return templates.TemplateResponse(request=request, name="step4_topsis.html")