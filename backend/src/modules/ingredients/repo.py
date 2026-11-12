from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.databse.models import Ingredients


class IngredientRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_organization_ingredients(self, org_id: UUID) -> list[Ingredients]:
        result = await self.session.execute(
            select(Ingredients)
            .where(Ingredients.organization_id == org_id)
        )

        return list(result.scalars().all())