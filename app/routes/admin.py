import os
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import db
from app.services.public_code import gerar_public_code_unico
from app.dependencies import verificar_admin
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

BASE_URL = os.environ["base_url"]

@router.get("/admin/lojas/nova", dependencies=[Depends(verificar_admin)])
def form_nova_loja(request: Request):
    return templates.TemplateResponse(request, "admin_nova_loja.html", {})


@router.post("/admin/lojas/nova", response_class=HTMLResponse)
def submit_nova_loja(
    request: Request,
    nome: str = Form(...),
    pontos_base: int = Form(...),
):
    codigo = gerar_public_code_unico(db.codigo_loja_existe)
    loja = db.inserir_loja(codigo_publico=codigo, nome=nome, pontos_base=pontos_base)

    if loja is None:
        return templates.TemplateResponse(
            request, "admin_resultado_loja.html",
            {"sucesso": False, "mensagem": "Erro ao cadastrar a loja. Tenta de novo."},
            status_code=500,
        )

    url_loja = f"{BASE_URL}/loja/{loja['codigo_publico']}"

    return templates.TemplateResponse(
        request, "admin_resultado_loja.html",
        {"sucesso": True, "loja": loja, "url_loja": url_loja},
    )