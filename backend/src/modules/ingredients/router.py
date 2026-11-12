from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.modules.ingredients.deps import get_ingredient_service
from src.modules.ingredients.schema import IngredientResponse
from src.modules.ingredients.service import IngredientService

router = APIRouter()


@router.post(
    "/{org_id/ingredients",
    summary="Создать ингредиент",
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredients(
        org_id: UUID,
):
    return


@router.get(
    "/{org_id/ingredients",
    response_model=list[IngredientResponse],
    summary="Получить список ингредиентов",
    status_code=status.HTTP_200_OK
)
async def get_ingredients(
        org_id: UUID,
        service: IngredientService = Depends(get_ingredient_service),
):
    return await service.get_organization_ingredients(org_id)


@router.get(
    "/{org_id/ingredients/{id}",
    response_model=IngredientResponse,
    summary="Получить ингредиент"
)
async def get_ingredient(
        org_id: UUID,
        id: UUID
):
    return


@router.patch(
    "/{org_id/ingredients/{id}",
    response_model=IngredientResponse,
    summary="Изменить характеристики ингредиента"
)
async def change_ingredient(
        org_id: UUID,
        id: UUID,
):
    return


@router.delete(
    "/{org_id/ingredients/{id}",
    summary="Архивировать ингредиент"
)
async def delete_ingredient(
        org_id: UUID,
        id: UUID,
):
    return