from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.environments import env
from fastapi import FastAPI

from .routers import router
from database.core import close_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Перезапуск backend fastapi")
    yield
    await close_session()


def get_application(lifespan) -> FastAPI:
    app = FastAPI(title=env.PROJECT_NAME, lifespan=lifespan)
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=env.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    return app
