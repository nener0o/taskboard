from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.permissions import has_permission
from app.security import decode_access_token
from app.services import AuthService, StorageService, TaskService, UserService, WeatherService

bearer = HTTPBearer(auto_error=False)
_weather = WeatherService()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


def get_storage_service(db: Session = Depends(get_db)) -> StorageService:
    return StorageService(db)


def get_weather_service() -> WeatherService:
    return _weather


def _user_from_token(db: Session, credentials: HTTPAuthorizationCredentials | None) -> User | None:
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь не найден")
    return user


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User | None:
    if credentials is None:
        return None
    return _user_from_token(db, credentials)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Требуется вход")
    return _user_from_token(db, credentials)


def require_permission(permission: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user.role, permission):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
        return user

    return checker


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
AuthDep = Annotated[AuthService, Depends(get_auth_service)]
UserDep = Annotated[UserService, Depends(get_user_service)]
TaskDep = Annotated[TaskService, Depends(get_task_service)]
StorageDep = Annotated[StorageService, Depends(get_storage_service)]
WeatherDep = Annotated[WeatherService, Depends(get_weather_service)]
