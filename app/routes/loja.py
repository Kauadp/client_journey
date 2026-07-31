from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/loja/{loja_id}", response_class=HTMLResponse)
def form_loja(loja_id: int, request: Request):
    loja = db.buscar_loja(loja_id)

    if loja is None:
        return templates.TemplateResponse(
            request, "resultado_loja.html",
            {"sucesso": False, "mensagem": "Loja não encontrada."},
            status_code=404,
        )

    return templates.TemplateResponse(request, "loja.html", {"loja": loja})


@router.post("/loja/{loja_id}", response_class=HTMLResponse)
def submit_loja(loja_id: int, request: Request, id_public: str = Form(...)):
    loja = db.buscar_loja(loja_id)
    if loja is None:
        return templates.TemplateResponse(
            request, "resultado_loja.html",
            {"sucesso": False, "ja_pontuou": False, "mensagem": "Loja não encontrada."},
            status_code=404,
        )

    visitante = db.buscar_por_id_public(id_public.strip().upper())
    if visitante is None:
        return templates.TemplateResponse(
            request, "resultado_loja.html",
            {"sucesso": False, "ja_pontuou": False, "mensagem": "Código não encontrado. Confere se digitou certo."},
        )

    resultado = db.registrar_pontuacao(
        visitante_id=visitante["id"],
        loja_id=loja_id,
        pontos=loja["pontos_base"],
    )

    if resultado == "ok":
        return templates.TemplateResponse(
            request, "resultado_loja.html",
            {"sucesso": True, "ja_pontuou": False, "mensagem": f"Você ganhou +{loja['pontos_base']} pontos, {visitante['nome']}!"},
        )
    elif resultado == "duplicado":
        return templates.TemplateResponse(
            request, "resultado_loja.html",
            {"sucesso": False, "ja_pontuou": True, "mensagem": f"Você já pontuou em {loja['nome']} hoje."},
        )
    else:
        return templates.TemplateResponse(
            request, "resultado_loja.html",
            {"sucesso": False, "ja_pontuou": False, "mensagem": "Não conseguimos registrar seus pontos agora. Tenta de novo em instantes."},
            status_code=500,
        )