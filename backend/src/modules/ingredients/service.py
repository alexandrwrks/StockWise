from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ingredients.repo import IngredientRepo
from src.modules.ingredients.schema import (
    IngredientRequest,
    IngredientResponse,
    UpdateIngredientRequest,
)


class IngredientService:
    def __init__(self, session: AsyncSession):
        self.repo = IngredientRepo(session)
        self.db = session

    async def get_organization_ingredients(self, org_id: UUID) -> list[IngredientResponse]:
        ingredients = await self.repo.get_organization_ingredients(org_id)

        return [IngredientResponse.model_validate(ingredient) for ingredient in ingredients]

    async def get_ingredient_by_uuid(
        self, org_uuid: UUID, ingredient_uuid: UUID
    ) -> IngredientResponse:
        ingredient = await self.repo.get_ingredient_by_uuid(org_uuid, ingredient_uuid)
        if ingredient is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        return IngredientResponse.model_validate(ingredient)

    async def change_ingredient_params(
        self, org_uuid: UUID, ingredient_uuid: UUID, params: UpdateIngredientRequest
    ) -> IngredientResponse:
        ingredient = await self.repo.get_ingredient_by_uuid(org_uuid, ingredient_uuid)
        if ingredient is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        try:
            ingredient = await self.repo.change_ingredient_params(ingredient, params)

            await self.db.commit()

        except (SQLAlchemyError, Exception) as e:
            await self.db.rollback()
            print(e)
            raise HTTPException(status_code=500, detail="Failed to change ingredient params")

        return IngredientResponse.model_validate(ingredient)

    async def delete_ingredient(self, org_uuid: UUID, ingredient_uuid: UUID) -> None:
        try:
            await self.repo.delete_ingredient(org_uuid, ingredient_uuid)

            await self.db.commit()

        except (SQLAlchemyError, Exception) as e:
            await self.db.rollback()
            print(e)
            raise HTTPException(status_code=500, detail="Failed to delete ingredient")

    async def create_ingredient(
        self, org_uuid: UUID, params: IngredientRequest
    ) -> IngredientResponse:
        try:
            ingredient = await self.repo.create_ingredient(org_uuid, params)

            await self.db.commit()

            return IngredientResponse.model_validate(ingredient)

        except (SQLAlchemyError, Exception) as e:
            await self.db.rollback()
            print(e)
            raise HTTPException(status_code=500, detail="Failed to create ingredient")
