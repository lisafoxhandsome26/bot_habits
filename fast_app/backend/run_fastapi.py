from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.environments import env
from config.async_database import close_session
from .routers import router
from .auth.auth_routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Перезапуск backend fastapi")
    yield
    await close_session()


def get_application(lifespan) -> FastAPI:
    app = FastAPI(title=env.PROJECT_NAME, lifespan=lifespan)
    app.include_router(router)
    app.include_router(auth_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=env.CORS_ALLOWED_ORIGINS, # env....
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    return app
