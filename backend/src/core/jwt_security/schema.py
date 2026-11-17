from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenType(StrEnum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class MemberRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EMPLOYEE = "employee"


class TokenData(BaseModel):
    user_id: UUID
    token_type: TokenType
    exp: datetime
    iat: datetime
