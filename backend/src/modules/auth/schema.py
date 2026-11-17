from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


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


class UserDataResponse(BaseModel):
    id: UUID
    email: EmailStr
    fullname: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PasswordUpdateRequest(BaseModel):
    new_password: str = Field(min_length=8, description="Новый пароль")
    password_retry: str = Field(min_length=8, description="Повтор пароля")

    @model_validator(mode="after")
    def validate_password(self) -> "PasswordUpdateRequest":
        if self.new_password != self.password_retry:
            raise ValueError("Пароли должны совпадать")

        return self

class UpdateRequest(BaseModel):
    email: EmailStr | None = Field(default=None, description="Новая почта пользователя")
    fullname: str | None = Field(default=None, description="Новое имя")