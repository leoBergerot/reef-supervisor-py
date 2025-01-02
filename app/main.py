from typing import Union
from fastapi import FastAPI
from app.core.config import settings
from app.db import hooks
from app.routers import root_router, user_router
app = FastAPI()

app.include_router(root_router)
app.include_router(user_router)


