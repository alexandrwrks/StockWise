from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from src.core.jwt_security.schema import TokensResponse
from src.modules.auth.deps import get_current_user, AuthServiceDep, get_refresh_token
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
    service: AuthServiceDep,
    params: RegisterRequest = Depends()
):
    return await service.register(params)

@router.post(
    path="/login",
    response_model=TokensResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя"
)
async def login(
    service: AuthServiceDep,
    params: LoginRequest = Depends()
) -> TokensResponse:
    return await service.login(params)

@router.post(
    path="/refresh",
    response_model=TokensResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление пары токенов"
)
async def refresh(
    service: AuthServiceDep,
    refresh_token: str = Depends(get_refresh_token),
) -> TokensResponse:
    return await service.refresh(refresh_token)

@router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из учётной записи и отзыв refresh токена"
)
async def logout(
    service: AuthServiceDep,
    refresh_token: str = Depends(get_refresh_token),
) -> None:
    return await service.logout(refresh_token)

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
    service: AuthServiceDep,
    params: UpdateRequest = Depends(),
    user: UserDataResponse = Depends(get_current_user)
) -> UserDataResponse:
    return await service.update_data(params, user.id)

@router.post(
    path="/change-password",
    response_model=UserDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Смена пароля пользователя"
)
async def change_password(
    service: AuthServiceDep,
    params: PasswordUpdateRequest = Depends(),
    user: UserDataResponse = Depends(get_current_user)
) -> UserDataResponse:
    return await service.change_password(params.new_password, user.id)