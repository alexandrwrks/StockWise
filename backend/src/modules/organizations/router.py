from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.database.enum import MemberRole
from src.modules.auth.deps import get_current_user
from src.modules.auth.schema import UserDataResponse
from src.modules.organizations.deps import get_organization_service, get_current_member, require_roles
from src.modules.organizations.schema import OrganizationRequest, OrganizationMemberResponse, MemberResponse, \
    OrganizationResponse, OrganizationUpdate
from src.modules.organizations.service import OrganizationService

router = APIRouter()

@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    summary="Создать организацию"
)
async def create_organization(
        params: OrganizationRequest = Depends(),
        user: UserDataResponse = Depends(get_current_user),
        service: OrganizationService = Depends(get_organization_service),
):
    return await service.create_organization(params, user.id)

@router.get(
    path="/",
    response_model=list[OrganizationMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Список организаций пользователя",
)
async def get_organizations(
        user: UserDataResponse = Depends(get_current_user),
        service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationMemberResponse]:
    return await service.get_user_active_organizations(user.id)

@router.get(
    path="/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение организации по уникальному UUID организации"
)
async def get_organization(
        member: MemberResponse = Depends(get_current_member),
        service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await service.get_organization(member.organization_id)

@router.patch(
    path="/{org_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationResponse,
    summary="Изменение характеристик организации"
)
async def update_organization(
        params: OrganizationUpdate = Depends(),
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER)),
        service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await service.update_organization(params, member.organization_id)

@router.get(
    path="/{org_id}/members",
    response_model=list[MemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение списка сотрудников",
)
async def get_organization_members(
        member: MemberResponse = Depends(
            require_roles(MemberRole.OWNER, MemberRole.ADMIN)
        ),
        service: OrganizationService = Depends(get_organization_service),
) -> list[MemberResponse]:
    return await service.get_members(member.organization_id)

@router.post(
    path="/{org_id}/invitations",
    summary="Приглашение сотрудника по email"
)
async def create_invitation(
        org_id: UUID,
):
    return

@router.post(
    path="/invitations/{token}/accept",
    summary="Принять приглашение"
)
async def accept_invitation(
        token: str
):
    return

@router.patch(
    path="/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Изменить роль сотрудника"
)
async def update_member_role(
        user_id: UUID,
        new_role: MemberRole,
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER)),
        service: OrganizationService = Depends(get_organization_service),
) -> None:
    return await service.update_member_role(user_id, new_role, member)

@router.delete(
    path="/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сотрудника из организации"
)
async def delete_member(
        user_id: UUID,
        member: MemberResponse = Depends(require_roles(MemberRole.OWNER)),
        service: OrganizationService = Depends(get_organization_service),
) -> None:
    return await service.delete_member(user_id, member)