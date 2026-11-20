from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.database.enum import MemberRole
from src.modules.organizations.deps import require_roles
from src.modules.organizations.schema import MemberResponse
from src.modules.purchases.deps import get_purchase_service
from src.modules.purchases.schema import PurchaseResponse, PurchaseRequest, PurchaseUpdate, FullPurchaseResponse
from src.modules.purchases.service import PurchaseService

router = APIRouter()

@router.post(
    path="/{org_id}/purchases",
    response_model=FullPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать закупку"
)
async def purchases(
        params: list[PurchaseRequest],
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
        service: PurchaseService = Depends(get_purchase_service)
) -> FullPurchaseResponse:
    return await service.create(params, member)

@router.get(
    path="/{org_id}/purchases",
    response_model=list[PurchaseResponse],
    status_code=status.HTTP_200_OK,
    description="Показ всех закупок"
)
async def get_purchases(
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
        service: PurchaseService = Depends(get_purchase_service)
) -> list[PurchaseResponse]:
    return await service.get_purchases(member.organization_id)

@router.get(
    path="/{org_id}/purchases/{purchase_id}",
    response_model=FullPurchaseResponse,
    status_code=status.HTTP_200_OK,
    description="Детали о закупке"
)
async def get_purchase(
        purchase_id: UUID,
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
        service: PurchaseService = Depends(get_purchase_service)
) -> FullPurchaseResponse:
    return await service.get_purchase(purchase_id, member.organization_id)

@router.patch(
    path="/{org_id}/purchases/{purchase_id}",
    response_model=FullPurchaseResponse,
    status_code=status.HTTP_200_OK,
    description="Изменить закупку"
)
async def update_purchase(
        purchase_id: UUID,
        params: PurchaseUpdate,
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
        service: PurchaseService = Depends(get_purchase_service)
) -> FullPurchaseResponse:
    return await service.update(params, purchase_id, member.organization_id)

@router.post(
    path="/{org_id}/purchases/{purchase_id}/receive",
    response_model=PurchaseResponse,
    status_code=status.HTTP_200_OK,
    description="Подтвердить поступление"
)
async def receive_purchase(
    purchase_id: UUID,
    member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
    service: PurchaseService = Depends(get_purchase_service)
) -> PurchaseResponse:
    return await service.receive(purchase_id, member.organization_id)

@router.post(
    path="/{org_id}/purchases/{purchase_id}/cancel",
    response_model=PurchaseResponse,
    status_code=status.HTTP_200_OK,
    description="Отменить неподтверждённую закупку"
)
async def cancel_purchase(
        purchase_id: UUID,
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER, MemberRole.ADMIN)),
        service: PurchaseService = Depends(get_purchase_service)
) -> PurchaseResponse:
    return await service.cancel(purchase_id, member.organization_id)