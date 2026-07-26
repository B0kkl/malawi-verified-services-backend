from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.database.base  # noqa: F401
from app.api.v1.router import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://127.0.0.1:5502",
        "http://localhost:5502",
        "https://malawi-verified-services-frontend.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }