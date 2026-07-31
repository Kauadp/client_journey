from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/hub-juquita", response_class=HTMLResponse)
def form_hub_juquita(request: Request):
    return templates.TemplateResponse(request, "hub_juquita.html", {})


@router.post("/hub-juquita", response_class=HTMLResponse)
def submit_hub_juquita(
    request: Request,
    id_public: str = Form(...),
    composicao: str = Form(...),
    faixa_etaria: str = Form(...),
    local_origem: str = Form(...),
):
    visitante = db.buscar_por_id_public(id_public.strip().upper())

    if visitante is None:
        return templates.TemplateResponse(
            request, "resultado_hub_juquita.html",
            {"sucesso": False, "ja_respondeu": False, "mensagem": "Código não encontrado. Confere se digitou certo."},
        )

    resultado = db.registrar_hub_juquita(
        visitante_id=visitante["id"],
        composicao=composicao,
        faixa_etaria=faixa_etaria,
        local_origem=local_origem,
    )

    if resultado == "ok":
        return templates.TemplateResponse(
            request, "resultado_hub_juquita.html",
            {"sucesso": True, "ja_respondeu": False, "mensagem": f"Valeu, {visitante['nome']}! Já pode pegar seu ecocopo ou alugar sua frota."},
        )
    elif resultado == "duplicado":
        return templates.TemplateResponse(
            request, "resultado_hub_juquita.html",
            {"sucesso": False, "ja_respondeu": True, "mensagem": "Você já passou por aqui hoje!"},
        )
    else:
        return templates.TemplateResponse(
            request, "resultado_hub_juquita.html",
            {"sucesso": False, "ja_respondeu": False, "mensagem": "Não conseguimos registrar agora. Tenta de novo."},
            status_code=500,
        )