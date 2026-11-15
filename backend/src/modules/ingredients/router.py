from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.database.enum import MemberRole
from src.modules.ingredients.deps import get_ingredient_service
from src.modules.ingredients.schema import (
    IngredientRequest,
    IngredientResponse,
    UpdateIngredientRequest,
)
from src.modules.ingredients.service import IngredientService
from src.modules.organizations.deps import get_current_member, require_roles
from src.modules.organizations.schema import MemberResponse

router = APIRouter()


@router.post(
    path="/{org_id}/ingredients",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать ингредиент",
)
async def create_ingredients(
    params: IngredientRequest,
    member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
    service: IngredientService = Depends(get_ingredient_service),
) -> IngredientResponse:
    return await service.create_ingredient(member.organization_id, params)


@router.get(
    path="/{org_id}/ingredients",
    response_model=list[IngredientResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список ингредиентов",
)
async def get_ingredients(
    member: MemberResponse = Depends(get_current_member),
    service: IngredientService = Depends(get_ingredient_service),
) -> list[IngredientResponse]:
    return await service.get_organization_ingredients(member.organization_id)


@router.get(
    path="/{org_id}/ingredients/{ingredient_id}",
    response_model=IngredientResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить ингредиент",
)
async def get_ingredient(
    ingredient_id: UUID,
    member: MemberResponse = Depends(get_current_member),
    service: IngredientService = Depends(get_ingredient_service),
) -> IngredientResponse:
    return await service.get_ingredient_by_uuid(member.organization_id, ingredient_id)


@router.patch(
    path="/{org_id}/ingredients/{ingredient_id}",
    response_model=IngredientResponse,
    summary="Изменить характеристики ингредиента",
)
async def change_ingredient(
    ingredient_id: UUID,
    params: UpdateIngredientRequest,
    member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
    service: IngredientService = Depends(get_ingredient_service),
) -> IngredientResponse:
    return await service.change_ingredient_params(member.organization_id, ingredient_id, params)


@router.delete(
    path="/{org_id}/ingredients/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Архивировать ингредиент",
)
async def delete_ingredient(
    ingredient_id: UUID,
    member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
    service: IngredientService = Depends(get_ingredient_service),
) -> None:
    return await service.delete_ingredient(member.organization_id, ingredient_id)
