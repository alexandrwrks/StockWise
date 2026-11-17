from fastapi import APIRouter, Depends, status

from src.core.jwt_security.schema import TokensResponse
from src.modules.auth.deps import get_current_user, AuthServiceDep
from src.modules.auth.schema import RegisterRequest, RegisterResponse, LoginRequest, UserDataResponse, \
    PasswordUpdateRequest, UpdateRequest

router = APIRouter()

@router.post(
    path="/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(
    params: RegisterRequest,
    service: AuthServiceDep
):
    return await service.register(params)

@router.post(
    path="/login",
    response_model=TokensResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя"
)
async def login(
    params: LoginRequest,
    service: AuthServiceDep,
) -> TokensResponse:
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
    response_model=UserDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о пользователе"
)
async def get_me(
    user: UserDataResponse = Depends(get_current_user),
    # service: AuthService = Depends(get_auth_service)
) -> UserDataResponse:
    return user

@router.patch(
    path="/me",
    response_model=UserDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменение данных пользователя"
)
async def change_my_data(
    params: UpdateRequest,
    service: AuthServiceDep,
    user: UserDataResponse = Depends(get_current_user),
):
    return await service.update_data(params, user.id)

@router.post(
    path="/change-password",
    response_model=UserDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Смена пароля пользователя"
)
async def change_password(
    params: PasswordUpdateRequest,
    service: AuthServiceDep,
    user: UserDataResponse = Depends(get_current_user),
):
    return await service.change_password(params.new_password, user.id)