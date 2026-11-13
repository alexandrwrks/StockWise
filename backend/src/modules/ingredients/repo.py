from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Ingredients
from src.modules.ingredients.schema import UpdateIngredientRequest


class IngredientRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_organization_ingredients(self, org_id: UUID) -> list[Ingredients]:
        result = await self.session.execute(
            select(Ingredients)
            .where(Ingredients.organization_id == org_id)
        )

        return list(result.scalars().all())

    async def get_ingredient_by_uuid(self, org_uuid: UUID, ingredient_uuid: UUID) -> Ingredients | None:
        result = await self.session.execute(
            select(Ingredients)
            .where(
                Ingredients.organization_id == org_uuid,
                Ingredients.id == ingredient_uuid,
            )
        )

        return result.scalar_one_or_none()

    async def change_ingredient_params(self, ingredient: Ingredients, params: UpdateIngredientRequest) -> Ingredients:
        new_data = params.model_dump(exclude_unset=True, exclude_none=True)

        for field, value in new_data.items():
            setattr(ingredient, field, value)

        await self.session.flush()

        return ingredient

    async def delete_ingredient(self, org_uuid: UUID, ingredient_uuid: UUID) -> None:
        await self.session.execute(
            update(Ingredients)
            .where(Ingredients.organization_id == org_uuid, Ingredients.id == ingredient_uuid)
            .values(is_active=False)
        )