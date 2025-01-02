from sqlmodel import SQLModel
from app.db.session import engine

def init_db():
    SQLModel.metadata.create_all(bind=engine)