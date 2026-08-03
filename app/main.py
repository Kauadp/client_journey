from fastapi import FastAPI
from app.routes import visitante, loja, hub_juquita, vip_lounge, admin

app = FastAPI(title="Ecossistema de Dados Exagerado")

app.include_router(visitante.router)
app.include_router(loja.router)
app.include_router(hub_juquita.router)
app.include_router(vip_lounge.router)
app.include_router(admin.router)