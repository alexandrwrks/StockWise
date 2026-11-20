from fastapi import APIRouter

from .auth.router import router as auth_router
from .ingredients.router import router as ingredients_router
from .organizations.router import router as organization_router
from .purchases.router import router as purchase_router

routers = APIRouter()

routers.include_router(organization_router, prefix="/organizations", tags=["organizations"])
routers.include_router(ingredients_router, tags=["ingredients"])
routers.include_router(auth_router, prefix="/auth", tags=["auth"])
routers.include_router(purchase_router, prefix="/purchase", tags=["purchase"])