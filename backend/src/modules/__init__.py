from fastapi import APIRouter

from .auth.router import router as auth_router

routers = APIRouter()

routers.include_router(auth_router, prefix="/auth", tags=["auth"])