from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine
from app.database.base import Base

# ✅ IMPORT YOUR ROUTER
from app.api.project_routes import router as project_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoResearch Pro")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTER ROUTER
app.include_router(project_router)

@app.get("/")
def root():
    return {"status": "AutoResearch Pro backend running"}
