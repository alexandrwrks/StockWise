from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.enum import MemberRole
from src.modules.organizations.repo import OrganizationRepo
from src.modules.organizations.schema import OrganizationRequest, OrganizationResponse, OrganizationMemberResponse, \
    MemberResponse, OrganizationUpdate


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.repo = OrganizationRepo(session)
        self.db = session

    async def create_organization(self, params: OrganizationRequest) -> OrganizationResponse:
        organization = await self.repo.create_organization(params)

        return OrganizationResponse.model_validate(organization)

    async def get_organization(self, org_uuid: UUID) -> OrganizationResponse:
        organization = await self.repo.get_organization(org_uuid)
        if organization is None:
            raise HTTPException(status_code=404, detail="Organization not found")

        return OrganizationResponse.model_validate(organization)

    async def get_user_active_organizations(self, user_id: UUID):
        organizations = await self.repo.get_user_active_organizations(user_id)

        return [
            OrganizationMemberResponse.model_validate(organization)
            for organization in organizations
        ]

    async def get_members(self, org_id: UUID) -> list[MemberResponse]:
        members = await self.repo.get_members(org_id)

        return [
            MemberResponse.model_validate(member)
            for member in members
        ]

    async def update_member_role(self, user_id: UUID, new_role: MemberRole, member: MemberResponse) -> None:
        exists_member = await self.repo.get_member(user_id)
        if exists_member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        if new_role == MemberRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Нельзя просто так назначить другого сотрудника владельцем"
            )

        try:
            await self.repo.update_member_role(user_id, new_role)

            await self.db.commit()

        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка обновления статуса"
            )

    async def delete_member(self, user_id: UUID, member: MemberResponse) -> None:
        exists_member = await self.repo.get_member(user_id)
        if exists_member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден")

        try:
            await self.repo.delete_member(user_id)

            await self.db.commit()

        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка удаления сотрудника из компании"
            )

    async def update_organization(self, params: OrganizationUpdate, org_id: UUID) -> OrganizationResponse:
        try:
            data = params.model_dump(exclude_unset=True)
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не переданы никакие данные"
                )

            updated_organization = await self.repo.update_organization(data, org_id)

            await self.db.commit()

            return OrganizationResponse.model_validate(updated_organization)

        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка обновления компании"
            )