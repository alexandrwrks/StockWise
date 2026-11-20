from uuid import UUID

from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.enum import MemberStatus, MemberRole
from src.database.models import Organizations, OrganizationMembers
from src.modules.organizations.schema import OrganizationRequest, OrganizationUpdate


class OrganizationRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_organization(self, data: dict, user_id: UUID) -> Organizations:
        result = await self.session.execute(
            insert(Organizations)
            .values(**data)
            .returning(Organizations)
        )

        await self.session.flush()

        organization = result.scalar_one()

        await self.session.execute(
            insert(OrganizationMembers)
            .values(
                organization_id=organization.id,
                user_id=user_id,
                role=MemberRole.OWNER,
            )
        )

        return organization

    async def get_organization(self, org_uuid: UUID) -> Organizations | None:
        result = await self.session.execute(
            select(Organizations).where(Organizations.id == org_uuid)
        )

        return result.scalar_one_or_none()

    async def get_organization_member_by_uuids(self, org_id: UUID, user_id: UUID) -> OrganizationMembers | None:
        result = await self.session.execute(
            select(OrganizationMembers)
            .where(
                OrganizationMembers.user_id == user_id,
                OrganizationMembers.organization_id == org_id,
                OrganizationMembers.status == MemberStatus.ACTIVE,
            )
        )

        return result.scalar_one_or_none()

    async def get_user_active_organizations(self, user_id: UUID) -> Sequence[RowMapping]:
        result = await self.session.execute(
            select(
                Organizations.id.label("organization_id"),
                Organizations.name.label("name"),
                OrganizationMembers.role,
                OrganizationMembers.status,
                OrganizationMembers.created_at.label("joined_at"),
            )
            .join(
                OrganizationMembers,
                OrganizationMembers.organization_id == Organizations.id,
            )
            .where(
                OrganizationMembers.user_id == user_id,
                OrganizationMembers.status == MemberStatus.ACTIVE,
            )
            .order_by(
                OrganizationMembers.created_at.desc(),
                Organizations.id
            )
        )

        return result.mappings().all()

    async def get_members(self, org_id: UUID) -> list[OrganizationMembers]:
        result = await self.session.execute(
            select(OrganizationMembers).where(OrganizationMembers.organization_id == org_id)
        )

        return list(result.scalars().all())

    async def get_member(self, user_id: UUID, org_id: UUID) -> OrganizationMembers | None:
        result = await self.session.execute(
            select(OrganizationMembers).where(
                OrganizationMembers.user_id == user_id, OrganizationMembers.organization_id == org_id
            )
        )

        return result.scalar_one_or_none()

    async def update_member_role(self, user_id: UUID, org_id: UUID, new_role: MemberRole) -> None:
        await self.session.execute(
            update(OrganizationMembers).where(
                OrganizationMembers.user_id == user_id, OrganizationMembers.organization_id == org_id
            )
            .values(role=new_role)
        )

    async def delete_member(self, user_id: UUID, org_id: UUID) -> None:
        await self.session.execute(
            update(OrganizationMembers).where(
                OrganizationMembers.user_id == user_id, OrganizationMembers.organization_id == org_id
            )
            .values(status=MemberStatus.BLOCKED)
        )

    async def update_organization(self, data: dict, org_id: UUID) -> Organizations:
        result = await self.session.execute(
            update(Organizations)
            .where(Organizations.id == org_id)
            .values(data)
            .returning(Organizations)
        )

        return result.scalar_one()
