from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Почта пользователя")
    password: str = Field(..., description="Пароль пользователя")
    full_name: str = Field(..., description="Полное имя")

class RegisterResponse(BaseModel):
    id: UUID = Field(..., description="Уникальный UUID пользователя")
    email: EmailStr = Field(..., description="Почта пользователя")
    full_name: str = Field(..., description="Полное имя")
    created_at: datetime = Field(..., description="Время создания аккаунта")

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Почта пользователя")
    password: str = Field(..., description="Пароль пользователя")