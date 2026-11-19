from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.database.enum import MemberRole, MemberStatus


class OrganizationRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    name: str = Field(min_length=1, max_length=200, description="Название организации")
    description: str | None = Field(default=None, max_length=2000, description="Описание организации")


class OrganizationResponse(OrganizationRequest):
    id: UUID = Field(..., description="Уникальный UUID организации")

    model_config = ConfigDict(from_attributes=True)

class MemberResponse(BaseModel):
    user_id: UUID = Field(..., description="Уникальный UUID пользователя")
    organization_id: UUID = Field(..., description="Уникальный UUID организации")
    role: MemberRole = Field(..., description="Роль работника организации")
    status: MemberStatus = Field(..., description="Статус работника")

    model_config = ConfigDict(from_attributes=True)

class OrganizationMemberResponse(BaseModel):
    organization_id: UUID = Field(..., description="Уникальный UUID организации")
    name: str = Field(min_length=1, max_length=200, description="Название организации")
    role: MemberRole = Field(..., description="Роль работника организации")
    status: MemberStatus = Field(..., description="Статус работника")
    joined_at: datetime = Field(..., description="Время присоединения пользователя к организации")

    model_config = ConfigDict(from_attributes=True)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, description="Новое название организации")
    description: str | None = Field(default=None, description="Новое описание организации")
