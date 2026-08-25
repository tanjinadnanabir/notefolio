from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import Base, engine
from app.models import Folder, Note, User

app = FastAPI(
    title="NoteFolio API",
    description="A free and open-source note-taking API",
    version="0.1.0",
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Welcome to NoteFolio API",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }