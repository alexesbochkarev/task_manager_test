from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


app = FastAPI(
    title="Task Manager Service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.parsed_cors_allow_methods,
    allow_headers=settings.parsed_cors_allow_headers,
)


@app.get("/health", tags=["Health"])
async def healthcheck():
    return {"status": "ok"}
