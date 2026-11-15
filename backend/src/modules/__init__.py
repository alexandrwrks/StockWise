from fastapi import APIRouter

from .auth.router import router as auth_router
from ..modules.organizations.router import router as organization_router


routers = APIRouter()


routers.include_router(organization_router, prefix="/organizations", tags=["organizations"])
routers.include_router(auth_router, prefix="/auth", tags=["auth"])