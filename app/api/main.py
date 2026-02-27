from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.db import startup_event
from app.api.v1.routes.events import router

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


@app.get("/", response_model=dict)
async def root() -> dict:
    """
    Root endpoint for the API.

    Returns:
        Welcome message with API version
    """
    return {"message": "Welcome to RusClimbing API", "version": "1.0.0"}


@app.get("/health", response_model=dict)
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
