from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Users, RefreshTokens
from src.modules.auth.schema import RegisterRequest


class AuthRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, params: RegisterRequest, hash_password: str) -> Users:
        result = await self.session.execute(
            insert(Users)
            .values(
                email=params.email,
                fullname=params.fullname,
                password=hash_password,
            )
            .returning(Users)
        )

        return result.scalar_one()

    async def get_user_by_email(self, email: str) -> Users | None:
        result = await self.session.execute(
            select(Users).where(Users.email == email)
        )

        return result.scalar_one_or_none()

    async def get_user_by_uuid(self, user_id: UUID) -> Users | None:
        result = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )

        return result.scalar_one_or_none()

    async def change_password(self, hash_password: str, user_id: UUID) -> Users:
        result = await self.session.execute(
            update(Users).where(Users.id == user_id, Users.password == hash_password)
            .returning(Users)
        )

        return result.scalar_one()

    async def update_data(self, data: dict, user_id: UUID) -> Users:
        result = await self.session.execute(
            update(Users).where(Users.id == user_id)
            .values(**data)
            .returning(Users)
        )

        return result.scalar_one()

    async def add_refresh_token(self, token_hash: str, user_id: UUID, expires_at: datetime) -> None:
        await self.session.execute(
            insert(RefreshTokens).values(
                id=uuid4(),
                token_hash=token_hash,
                user_id=user_id,
                expires_at=expires_at,
                revoked=False,
            )
        )

    async def update_token(self, user_id: UUID, old_token_hash: str, new_token_hash: str, expires_at: datetime) -> UUID | None:
        result = await self.session.execute(
            update(RefreshTokens)
            .where(
                RefreshTokens.user_id == user_id,
                RefreshTokens.token_hash == old_token_hash,
                RefreshTokens.revoked.is_(False),
                RefreshTokens.expires_at > func.now(),
            )
            .values(
                token_hash=new_token_hash,
                expires_at=expires_at,
            )
            .returning(RefreshTokens.id)
        )

        return result.scalar_one_or_none()

    async def logout(self, refresh_token_hash: str) -> None:
        await self.session.execute(
            update(RefreshTokens)
            .where(
                RefreshTokens.token_hash == refresh_token_hash,
                RefreshTokens.revoked.is_(False),
            )
            .values(revoked=True)
        )