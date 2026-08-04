from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/acao-guerrilha", response_class=HTMLResponse)
def form_acao_guerrilha(request: Request):
    return templates.TemplateResponse(request, "acao_guerrilha.html", {})


@router.post("/acao-guerrilha", response_class=HTMLResponse)
def submit_acao_guerrilha(
    request: Request,
    id_public: str = Form(...),
    oque_trouxe: str = Form(...),
    regiao: str = Form(...),
):
    visitante = db.buscar_por_id_public(id_public.strip().upper())

    if visitante is None:
        return templates.TemplateResponse(
            request, "resultado.html",
            {"sucesso": False, "ja_respondeu": False, "mensagem": "Código não encontrado. Confere se digitou certo."},
        )

    resultado = db.registrar_acao_guerrilha(
        visitante_id=visitante["id"],
        oque_trouxe=oque_trouxe,
        regiao=regiao,
    )

    if resultado == "ok":
        return templates.TemplateResponse(
            request, "resultado.html",
            {"sucesso": True, "ja_respondeu": False, "mensagem": f"Valeu, {visitante['nome']}! Mensagem Parabéns!"},
        )
    elif resultado == "duplicado":
        return templates.TemplateResponse(
            request, "resultado.html",
            {"sucesso": False, "ja_respondeu": True, "mensagem": "Você já passou por aqui hoje!"},
        )
    else:
        return templates.TemplateResponse(
            request, "resultado.html",
            {"sucesso": False, "ja_respondeu": False, "mensagem": "Não conseguimos registrar agora. Tenta de novo."},
            status_code=500,
        )