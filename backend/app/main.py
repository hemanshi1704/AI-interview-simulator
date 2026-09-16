from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import get_settings
from app.routers import auth, resume, interview

settings = get_settings()

# Creates tables if they don't exist. For production, use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(interview.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
