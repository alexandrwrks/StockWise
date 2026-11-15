from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import get_async_session
from src.database.enum import MemberStatus, MemberRole
from src.modules.auth.deps import get_current_user
from src.modules.auth.schema import UserDataResponse
from src.modules.organizations.repo import OrganizationRepo
from src.modules.organizations.schema import MemberResponse
from src.modules.organizations.service import OrganizationService


async def get_organization_service(
        session: AsyncSession = Depends(get_async_session),
):
    return OrganizationService(session)

async def get_organization_repo(session: AsyncSession = Depends(get_async_session)):
    return OrganizationRepo(session)

async def get_current_member(
        org_id: UUID,
        user: UserDataResponse = Depends(get_current_user),
        repo: OrganizationRepo = Depends(get_organization_repo)
) -> MemberResponse:
    try:
        organization = await repo.get_organization(org_id)
        if organization is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Организация не найдена")

        member = await repo.get_organization_member_by_uuids(org_id, user.id)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка получения данных работника")

    if member is None or member.status != MemberStatus.ACTIVE :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member not found or member is not active")

    return MemberResponse.model_validate(member)

def require_roles(*allowed_roles: MemberRole):
    async def check_roles(
            member: MemberResponse = Depends(get_current_member),
    ) -> MemberResponse:
        if member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав"
            )

        return member

    return check_roles
