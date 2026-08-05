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


@router.post("/admin/lojas/nova", response_class=HTMLResponse, dependencies=[Depends(verificar_admin)])
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

@router.get("/admin/brindes/nova", response_class=HTMLResponse, dependencies=[Depends(verificar_admin)])
def form_novo_brinde(request: Request):
    return templates.TemplateResponse(request, "admin_novo_brinde.html", {})


@router.post("/admin/brindes/nova", response_class=HTMLResponse, dependencies=[Depends(verificar_admin)])
def submit_novo_brinde(
    request: Request,
    nome: str = Form(...),
    custo_pontos: int = Form(...),
    estoque: int = Form(...),
):
    brinde = db.inserir_brinde(nome=nome, custo_pontos=custo_pontos, estoque=estoque)

    if brinde is None:
        return templates.TemplateResponse(
            request, "admin_resultado_brinde.html",
            {"sucesso": False, "mensagem": "Erro ao cadastrar o brinde. Tenta de novo."},
            status_code=500,
        )

    return templates.TemplateResponse(
        request, "admin_resultado_brinde.html",
        {"sucesso": True, "brinde": brinde},
    )

@router.get("/admin/resgate", response_class=HTMLResponse, dependencies=[Depends(verificar_admin)])
def form_resgate(request: Request):
    brindes = db.buscar_brindes_disponiveis()
    return templates.TemplateResponse(request, "admin_resgate.html", {"brindes": brindes})


@router.post("/admin/resgate", response_class=HTMLResponse, dependencies=[Depends(verificar_admin)])
def submit_resgate(request: Request, id_public: str = Form(...), brinde_id: int = Form(...)):
    visitante = db.buscar_por_id_public(id_public.strip().upper())
    if visitante is None:
        return templates.TemplateResponse(
            request, "admin_resultado_resgate.html",
            {"sucesso": False, "mensagem": "Código não encontrado."},
        )

    brinde = db.buscar_brinde(brinde_id)
    if brinde is None:
        return templates.TemplateResponse(
            request, "admin_resultado_resgate.html",
            {"sucesso": False, "mensagem": "Brinde não encontrado."},
        )

    resultado = db.resgatar_brinde(
    visitante_id=visitante["id"],
    brinde_id=brinde_id,
    custo_pontos=brinde["custo_pontos"],
    tipo=brinde["tipo"],
)

    mensagens = {
        "ok": f"✅ {visitante['nome']} resgatou: {brinde['nome']}!",
        "saldo_insuficiente": f"{visitante['nome']} não tem pontos suficientes.",
        "sem_estoque": f"{brinde['nome']} está sem estoque.",
        "formularios_incompletos": f"{visitante['nome']} ainda não respondeu todos os formulários.",
        "ja_resgatou_padrao": f"{visitante['nome']} já resgatou o brinde dele.",
        "duplicado": f"{visitante['nome']} já resgatou esse item antes.",
        "erro": "Erro ao processar o resgate. Tenta de novo.",
    }

    return templates.TemplateResponse(
        request, "admin_resultado_resgate.html",
        {"sucesso": resultado == "ok", "mensagem": mensagens[resultado]},
    )