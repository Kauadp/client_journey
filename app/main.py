from fastapi import FastAPI
from app.routes import entrada_juquita, visitante, loja, vip_lounge, admin, usuario_pontuacao, auth, acao_guerrilha, boas_vindas, estacionamento, cenografia, saida_juquita
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Ecossistema de Dados Exagerado")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("session_create_key"))

app.include_router(visitante.router)
app.include_router(loja.router)
app.include_router(entrada_juquita.router)
app.include_router(vip_lounge.router)
app.include_router(admin.router)
app.include_router(usuario_pontuacao.router)
app.include_router(auth.router)
app.include_router(acao_guerrilha.router)
app.include_router(boas_vindas.router)
app.include_router(estacionamento.router)
app.include_router(cenografia.router)
app.include_router(saida_juquita.router)