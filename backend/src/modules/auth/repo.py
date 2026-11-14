from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Users
from src.modules.auth.schema import RegisterRequest


class AuthRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, params: RegisterRequest, hash_password: str) -> Users:
        result = await self.session.execute(
            insert(Users)
            .values(
                email=params.email,
                full_name=params.full_name,
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