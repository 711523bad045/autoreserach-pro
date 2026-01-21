from fastapi import FastAPI

from app.database.base import Base
from app.database.session import engine
from app.database import models

from app.api.project_routes import router as project_router

app = FastAPI(title="AutoResearch Pro")

Base.metadata.create_all(bind=engine)

app.include_router(project_router)


@app.get("/")
def root():
    return {"status": "AutoResearch Pro backend running"}
