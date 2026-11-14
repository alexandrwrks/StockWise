from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    created_at: datetime