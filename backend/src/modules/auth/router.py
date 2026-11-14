from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.modules.auth.deps import get_auth_service
from src.modules.auth.schema import RegisterRequest, RegisterResponse, LoginRequest
from src.modules.auth.service import AuthService

router = APIRouter()

@router.post(
    path="/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(
    params: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register(params)

@router.post(
    path="/login",
    response_model=RegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя"
)
async def login(
    params: LoginRequest,
    service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    return await service.login(params)

@router.post("/refresh")
async def refresh(

):
    return

@router.post("/logout")
async def logout(

):
    return

@router.get(
    path="/me",
    response_model=RegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о пользователе"
)
async def get_me(
    user_id: UUID,
    service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    return await service.me(user_id)

@router.patch("/me")
async def change_my_data(

):
    return

@router.post("/change-password")
async def change_password(

):
    return