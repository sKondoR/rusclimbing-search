from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.permissions import PermissionCheck
from app.api.db import startup_event
from app.api.v1.routes.events import router
from app.schemas.event import BaseResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    openapi_tags=[
        {
            "name": "events",
            "description": "запрос всех событий",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get(
    "/",
    response_model=BaseResponse,
    summary="Root endpoint",
    operation_id="root",
    description="Root endpoint for the API. Returns a welcome message with API version.",
    dependencies=[Depends(PermissionCheck())],
)
async def root() -> dict:
    """
    Root endpoint for the API.

    Returns:
        Welcome message with API version
    """
    return {"message": "Welcome to RusClimbing API", "version": "1.0.0"}


@app.get(
    "/health",
    response_model=BaseResponse,
    summary="Health check",
    operation_id="health_check",
    description="Health check endpoint. Returns API health status.",
    dependencies=[Depends(PermissionCheck())],
)
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        API health status
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def startup() -> None:
    """
    Startup event handler.

    Initializes database connection on application startup.
    """
    await startup_event()
