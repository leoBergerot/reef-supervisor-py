from typing import Union
from fastapi import FastAPI
from app.db.init_db import init_db
from app.core.config import settings
from app.db import hooks

app = FastAPI()

@app.on_event("startup")
def on_startup():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    init_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
