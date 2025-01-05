from fastapi import FastAPI
from app.core.config import settings
from app.db import hooks
from app.routers import root_router, user_router, parameter_router, preference_router, tank_router

app = FastAPI()

app.include_router(root_router)
app.include_router(user_router)
app.include_router(parameter_router)
app.include_router(preference_router)
app.include_router(tank_router)
