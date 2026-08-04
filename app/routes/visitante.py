from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import db
from app.services.public_code import gerar_public_code_unico
from app.services.email_service import enviar_email_passaporte

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/entrada", response_class=HTMLResponse)
def form_entrada(request: Request):
    return templates.TemplateResponse(request, "entrada.html", {})


@router.post("/entrada", response_class=HTMLResponse)
def submit_entrada(
    request: Request,
    nome: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(...),
):
    telefone_normalizado = "".join(filter(str.isdigit, telefone))

    usuario_tel = db.buscar_por_telefone(telefone_normalizado)
    usuario_email = db.buscar_por_email(email)

    if usuario_tel is None and usuario_email is None:
        id_public = gerar_public_code_unico(db.id_public_existe)
        usuario = db.inserir_usuario(
            nome=nome,
            numero_cel=telefone_normalizado,
            email=email,
            id_public=id_public,
        )
        enviar_email_passaporte(
            nome=nome,
            email=email,
            id_public=id_public
        )

        if usuario is None:
            return templates.TemplateResponse(
                request,
                "erro.html",
                {"mensagem": "Não conseguimos concluir seu cadastro. Tenta de novo em instantes."},
                status_code=500,
            )

    else:
        return templates.TemplateResponse(
            request,
            "erro.html",
            {"mensagem": "Número de celular ou Email já cadastrados. Verifique se o campo está correto e tente novamente."},
            status_code=400,
        )


    return templates.TemplateResponse(
        request,
        "confirmacao.html",
        {"id_public": usuario["id_public"], "nome": usuario["nome"]},
    )