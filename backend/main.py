import os
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from sqlmodel import SQLModel
from database import engine
from auth_endpoints import router as auth_router
from task_endpoints import router as task_router
from chat_endpoints import router as chat_router
from logging_config import logger
import models  # noqa: F401 — ensure all models are registered before create_all

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

# T029: Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Todo API",
    description="API for managing tasks in a multi-user todo application",
    version="2.0.0",
)
app.state.limiter = limiter

# T031: 429 error handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# T041: CORS from environment
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
def on_startup():
    logger.info("Creating database tables if they don't exist...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables ready.")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/debug/env")
def debug_env():
    return {
        "OPEN_ROUTER_API_KEY_set": bool(os.getenv("OPEN_ROUTER_API_KEY")),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "NOT SET"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "NOT SET"),
        "DATABASE_URL_set": bool(os.getenv("DATABASE_URL")),
        "FRONTEND_URL": os.getenv("FRONTEND_URL", "NOT SET"),
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url} -> {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
