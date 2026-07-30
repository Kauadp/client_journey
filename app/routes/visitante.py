from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import db
from app.services.public_code import gerar_public_code_unico

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/form/entrada", response_class=HTMLResponse)
def form_entrada(request: Request):
    return templates.TemplateResponse(request, "entrada.html", {})


@router.post("/form/entrada", response_class=HTMLResponse)
def submit_entrada(
    request: Request,
    nome: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(...),
):
    telefone_normalizado = "".join(filter(str.isdigit, telefone))

    usuario = db.buscar_por_telefone(telefone_normalizado)

    if usuario is None:
        id_public = gerar_public_code_unico(db.id_public_existe)
        usuario = db.inserir_usuario(
            nome=nome,
            numero_cel=telefone_normalizado,
            email=email,
            id_public=id_public,
        )

        if usuario is None:
            return templates.TemplateResponse(
                request,
                "erro.html",
                {"mensagem": "Não conseguimos concluir seu cadastro. Tenta de novo em instantes."},
                status_code=500,
            )

    return templates.TemplateResponse(
        request,
        "confirmacao.html",
        {"id_public": usuario["id_public"], "nome": usuario["nome"]},
    )