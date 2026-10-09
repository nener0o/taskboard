import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api, public
from app.config import settings
from app.graphql_schema import graphql_router
from app.migrate import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskboard")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.jwt_secret.startswith("dev-only"):
        logger.warning("Используется секрет JWT по умолчанию. Для развёртывания задайте JWT_SECRET.")
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api, prefix="/api")
app.include_router(public)
app.include_router(graphql_router, prefix="/graphql")
