from fastapi import FastAPI
from app.routes import visitante

app = FastAPI(title="Ecossistema de Dados Exagerado")

app.include_router(visitante.router)