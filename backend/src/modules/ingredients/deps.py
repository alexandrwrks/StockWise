from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import get_async_session
from src.modules.ingredients.service import IngredientService


async def get_ingredient_service(
    session: AsyncSession = Depends(get_async_session),
) -> IngredientService:
    return IngredientService(session)
