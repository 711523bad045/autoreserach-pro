from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine
from app.database.base import Base

#  IMPORT YOUR ROUTER
from app.api.project_routes import router as project_router
from fastapi.staticfiles import StaticFiles

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoResearch Pro")

import os

os.makedirs("generated_diagrams", exist_ok=True)

app.mount(
    "/generated_diagrams",
    StaticFiles(directory="generated_diagrams"),
    name="generated_diagrams",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",  # Local development
    "https://*.vercel.app",   # Your deployed frontend
      ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  REGISTER ROUTER
app.include_router(project_router)

@app.get("/")
def root():
    return {"status": "AutoResearch Pro backend running"}
