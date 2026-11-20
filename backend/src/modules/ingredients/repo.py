from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update, bindparam
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Ingredients
from src.modules.ingredients.schema import IngredientRequest, UpdateIngredientRequest


class IngredientRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_organization_ingredients(self, org_id: UUID) -> list[Ingredients]:
        result = await self.session.execute(
            select(Ingredients).where(Ingredients.organization_id == org_id)
        )

        return list(result.scalars().all())

    async def get_ingredient_by_uuid(
        self, org_uuid: UUID, ingredient_uuid: UUID
    ) -> Ingredients | None:
        result = await self.session.execute(
            select(Ingredients).where(
                Ingredients.organization_id == org_uuid,
                Ingredients.id == ingredient_uuid,
            )
        )

        return result.scalar_one_or_none()

    async def change_ingredient_params(
        self, ingredient: Ingredients, params: UpdateIngredientRequest
    ) -> Ingredients:
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

    async def create_ingredient(self, org_uuid: UUID, params: IngredientRequest) -> Ingredients:
        result = await self.session.execute(
            insert(Ingredients)
            .values(
                **params.model_dump(),
                organization_id=org_uuid,
            )
            .returning(Ingredients)
        )

        return result.scalar_one()

    async def replenishment(self, ingredients: list[dict]) -> None:
        await self.session.execute(
            update(Ingredients)
            .where(Ingredients.id == bindparam("ingredient_id"))
            .values(
                current_stock=Ingredients.current_stock + bindparam("added_quantity"),
            ),
            [
                {
                    "ingredient_id": item["id"],
                    "added_quantity": item["quantity"],
                }
                for item in ingredients
            ]
        )

    async def get_existing_ids(self, organization_id: UUID, ingredient_ids: set[UUID]) -> set[UUID]:
        result = await self.session.scalars(
            select(Ingredients.id).where(
                Ingredients.organization_id == organization_id,
                Ingredients.id.in_(ingredient_ids),
            )
        )
        return set(result.all())