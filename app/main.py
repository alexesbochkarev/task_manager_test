from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.config import settings
from app.db.session import engine


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

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def healthcheck():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "unavailable",
                "message": str(exc),
            },
        ) from exc

    return {
        "status": "ok",
        "database": "available",
    }
