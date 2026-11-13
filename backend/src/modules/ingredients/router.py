from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.modules.ingredients.deps import get_ingredient_service
from src.modules.ingredients.schema import IngredientResponse, UpdateIngredientRequest, IngredientRequest
from src.modules.ingredients.service import IngredientService

router = APIRouter()


@router.post(
    path="/{org_id}/ingredients",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать ингредиент",
)
async def create_ingredients(
        org_id: UUID,
        params: IngredientRequest,
        service: IngredientService = Depends(get_ingredient_service),
):
    return await service.create_ingredient(org_id, params)


@router.get(
    path="/{org_id}/ingredients",
    response_model=list[IngredientResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список ингредиентов"
)
async def get_ingredients(
        org_id: UUID,
        service: IngredientService = Depends(get_ingredient_service),
):
    return await service.get_organization_ingredients(org_id)


@router.get(
    path="/{org_id}/ingredients/{id}",
    response_model=IngredientResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить ингредиент"
)
async def get_ingredient(
        org_id: UUID,
        id: UUID,
        service: IngredientService = Depends(get_ingredient_service),
):
    return await service.get_ingredient_by_uuid(org_id, id)


@router.patch(
    path="/{org_id}/ingredients/{id}",
    response_model=IngredientResponse,
    summary="Изменить характеристики ингредиента"
)
async def change_ingredient(
        org_id: UUID,
        id: UUID,
        params: UpdateIngredientRequest,
        service: IngredientService = Depends(get_ingredient_service),
):
    return await service.change_ingredient_params(org_id, id, params)


@router.delete(
    path="/{org_id}/ingredients/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Архивировать ингредиент"
)
async def delete_ingredient(
        org_id: UUID,
        id: UUID,
        service: IngredientService = Depends(get_ingredient_service),
):
    return await service.delete_ingredient(org_id, id)