from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ingredients.repo import IngredientRepo
from src.modules.ingredients.schema import IngredientResponse


class IngredientService:
    def __init__(self, session: AsyncSession):
        self.repo = IngredientRepo(session)
        self.db = session

    async def get_organization_ingredients(self, org_id: UUID) -> list[IngredientResponse]:
        ingredients = await self.repo.get_organization_ingredients(org_id)

        return [
            IngredientResponse.model_validate(ingredient)
            for ingredient in ingredients
        ]