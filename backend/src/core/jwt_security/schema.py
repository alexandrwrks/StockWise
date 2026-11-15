from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

class ResponseTokensSchema(BaseModel):
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
    role: MemberRole
    organization_id: UUID
