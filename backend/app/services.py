import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Attachment, RefreshToken, Role, Task, TaskStatus, User
from app.permissions import has_permission, permissions_for
from app.repositories import FileRepository, TaskRepository, TokenRepository, UserRepository, touch
from app.schemas import FileOut, TaskIn, TaskOut, TaskUpdate, WeatherOut
from app.security import (
    create_access_token,
    hash_password,
    hash_token,
    new_refresh_token,
    sign_download,
    verify_download,
    verify_password,
)

ALLOWED_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}

WEATHER_SUMMARY = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Туман с изморозью",
    51: "Морось",
    61: "Дождь",
    71: "Снег",
    80: "Ливень",
    95: "Гроза",
}


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def task_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        is_public=task.is_public,
        owner_id=task.owner_id,
        assignee_id=task.assignee_id,
        owner_name=task.owner.name if task.owner else "",
        assignee_name=task.assignee.name if task.assignee else None,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = TokenRepository(db)

    def register(self, name: str, email: str, password: str) -> User:
        if self.users.by_email(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким email уже есть")
        user = User(name=name.strip(), email=email.lower(), password_hash=hash_password(password), role=Role.USER)
        self.users.add(user)
        self.db.commit()
        return user

    def login(self, email: str, password: str) -> dict:
        user = self.users.by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Учётная запись отключена")
        return self._issue(user)

    def refresh(self, raw_token: str) -> dict:
        row = self.tokens.by_hash(hash_token(raw_token))
        if row is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Сессия не найдена")
        if row.revoked:
            self.tokens.revoke_all(row.user_id)
            self.db.commit()
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Сессия отозвана. Войдите снова")
        if ensure_utc(row.expires_at) <= datetime.now(timezone.utc):
            row.revoked = True
            self.db.commit()
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Срок сессии истёк")
        user = row.user
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Учётная запись отключена")
        row.revoked = True
        payload = self._issue(user)
        row.replaced_by_id = self.tokens.by_hash(hash_token(payload["refresh_token"])).id
        self.db.commit()
        return payload

    def logout(self, raw_token: str) -> None:
        row = self.tokens.by_hash(hash_token(raw_token))
        if row and not row.revoked:
            row.revoked = True
            self.db.commit()

    def _issue(self, user: User) -> dict:
        raw, digest = new_refresh_token()
        self.tokens.add(
            RefreshToken(
                user_id=user.id,
                token_hash=digest,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        self.db.commit()
        return {
            "access_token": create_access_token(user.id, user.role.value),
            "refresh_token": raw,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def to_out(self, user: User) -> dict:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "permissions": sorted(permissions_for(user.role)),
        }

    def list_users(self, actor: User) -> list[User]:
        if not has_permission(actor.role, "user:read"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
        return self.users.list_users()

    def directory(self) -> list[User]:
        return self.users.directory()

    def change_role(self, actor: User, user_id: int, role: Role) -> User:
        if not has_permission(actor.role, "user:manage_roles"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Менять роли может только администратор")
        if actor.id == user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Нельзя изменить собственную роль")
        user = self.users.by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
        if user.role == Role.ADMIN and role != Role.ADMIN and self.users.count_admins() <= 1:
            raise HTTPException(status.HTTP_409_CONFLICT, "Нельзя снять роль с последнего администратора")
        user.role = role
        self.db.commit()
        return user


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.tasks = TaskRepository(db)
        self.users = UserRepository(db)

    def create(self, actor: User, data: TaskIn) -> Task:
        if not has_permission(actor.role, "task:create"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для создания")
        self._ensure_assignee(data.assignee_id)
        task = Task(
            title=data.title.strip(),
            description=data.description.strip(),
            status=data.status,
            priority=data.priority,
            is_public=data.is_public,
            owner_id=actor.id,
            assignee_id=data.assignee_id,
        )
        self.tasks.add(task)
        self.db.commit()
        return self.tasks.get(task.id)

    def update(self, actor: User, task_id: int, data: TaskUpdate) -> Task:
        task = self._get_for_write(actor, task_id)
        changes = data.model_dump(exclude_unset=True)
        if "assignee_id" in changes:
            self._ensure_assignee(changes["assignee_id"])
        moderating = False
        if "is_public" in changes and task.owner_id != actor.id and actor.role not in {Role.MANAGER, Role.ADMIN}:
            moderating = True
        if "status" in changes and changes["status"] == TaskStatus.ARCHIVED and task.owner_id != actor.id:
            moderating = True
        if moderating and not has_permission(actor.role, "task:moderate"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для модерации")
        for key, value in changes.items():
            if isinstance(value, str):
                value = value.strip()
            setattr(task, key, value)
        touch(task, datetime.now(timezone.utc))
        self.db.commit()
        return self.tasks.get(task.id)

    def delete(self, actor: User, task_id: int) -> None:
        task = self.tasks.get(task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Задача не найдена")
        owns = task.owner_id == actor.id
        if owns and has_permission(actor.role, "task:delete_own"):
            pass
        elif has_permission(actor.role, "task:delete_any"):
            pass
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Удаление этой задачи запрещено")
        self.tasks.delete(task)
        self.db.commit()

    def get_visible(self, task_id: int, viewer: User | None) -> Task:
        task = self.tasks.get(task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Задача не найдена")
        if self._can_view(viewer, task):
            return task
        if task.status == TaskStatus.ARCHIVED and task.is_public:
            raise HTTPException(status.HTTP_410_GONE, "Задача снята с публикации")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для просмотра")

    def search(self, viewer: User | None, **filters) -> tuple[list[Task], int]:
        return self.tasks.search(viewer=viewer, **filters)

    def _get_for_write(self, actor: User, task_id: int) -> Task:
        task = self.tasks.get(task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Задача не найдена")
        if not self._can_view(actor, task):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
        owns = task.owner_id == actor.id or task.assignee_id == actor.id
        if owns and has_permission(actor.role, "task:update_own"):
            return task
        if has_permission(actor.role, "task:update_any"):
            return task
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Редактирование запрещено")

    def _can_view(self, viewer: User | None, task: Task) -> bool:
        if viewer and viewer.role in {Role.MANAGER, Role.ADMIN}:
            return True
        if viewer and (task.owner_id == viewer.id or task.assignee_id == viewer.id):
            return True
        return bool(task.is_public and task.status != TaskStatus.ARCHIVED)

    def _ensure_assignee(self, assignee_id: int | None) -> None:
        if assignee_id is None:
            return
        user = self.users.by_id(assignee_id)
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Исполнитель не найден")


class StorageService:
    def __init__(self, db: Session):
        self.db = db
        self.files = FileRepository(db)
        self.tasks = TaskService(db)

    def upload(self, actor: User, task_id: int, filename: str, content_type: str, data: bytes) -> Attachment:
        if not has_permission(actor.role, "file:upload"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для загрузки")
        task = self.tasks.get_visible(task_id, actor)
        self._can_attach(actor, task)
        safe_name, mime = self._validate(filename, content_type, data)
        key = self._put(safe_name, data, mime)
        row = Attachment(
            task_id=task.id,
            original_name=safe_name,
            content_type=mime,
            size=len(data),
            storage_key=key,
            uploaded_by=actor.id,
        )
        self.files.add(row)
        self.db.commit()
        return row

    def list_files(self, viewer: User | None, task_id: int) -> list[Attachment]:
        self.tasks.get_visible(task_id, viewer)
        return self.files.list_for_task(task_id)

    def delete(self, actor: User, file_id: int) -> None:
        row = self.files.get(file_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Файл не найден")
        self.tasks.get_visible(row.task_id, actor)
        owns = row.uploaded_by == actor.id
        if owns and has_permission(actor.role, "file:delete_own"):
            pass
        elif has_permission(actor.role, "file:delete_any"):
            pass
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для удаления файла")
        self._remove(row.storage_key)
        self.files.delete(row)
        self.db.commit()

    def open(self, file_id: int, token: str) -> tuple[Path | None, bytes | None, Attachment]:
        verify_download(token, file_id)
        row = self.files.get(file_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Файл не найден")
        if settings.s3_enabled:
            return None, self._read_s3(row.storage_key), row
        path = Path(settings.storage_dir) / row.storage_key
        if not path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Файл отсутствует в хранилище")
        return path, None, row

    def to_out(self, row: Attachment) -> FileOut:
        expires = int(time.time()) + 300
        token = sign_download(row.id, expires)
        if settings.s3_enabled:
            url = self._presign_s3(row.storage_key)
        else:
            url = f"/api/files/{row.id}/content?token={token}"
        return FileOut(
            id=row.id,
            task_id=row.task_id,
            original_name=row.original_name,
            content_type=row.content_type,
            size=row.size,
            uploaded_by=row.uploaded_by,
            created_at=row.created_at,
            download_url=url,
        )

    def _can_attach(self, actor: User, task: Task) -> None:
        if actor.role in {Role.MANAGER, Role.ADMIN}:
            return
        if task.owner_id == actor.id or task.assignee_id == actor.id:
            return
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Файл можно прикрепить только к своей задаче")

    def _validate(self, filename: str, content_type: str, data: bytes) -> tuple[str, str]:
        name = Path(filename).name.strip()
        if not name or len(name) > 200:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Некорректное имя файла")
        ext = Path(name).suffix.lower()
        expected = ALLOWED_TYPES.get(ext)
        if not expected:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Допустимы png, jpg, webp, gif, pdf и txt")
        mime = content_type.split(";")[0].strip().lower() or expected
        if mime != expected:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Тип файла не совпадает с расширением")
        if not data:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пустой файл")
        if len(data) > settings.max_upload_bytes:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Файл больше 5 МБ")
        return name, mime

    def _put(self, filename: str, data: bytes, content_type: str) -> str:
        key = f"{uuid.uuid4().hex}_{filename}"
        if settings.s3_enabled:
            client = self._s3()
            client.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)
            return key
        folder = Path(settings.storage_dir)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / key).write_bytes(data)
        return key

    def _remove(self, key: str) -> None:
        if settings.s3_enabled:
            self._s3().delete_object(Bucket=settings.s3_bucket, Key=key)
            return
        path = Path(settings.storage_dir) / key
        if path.exists():
            path.unlink()

    def _presign_s3(self, key: str) -> str:
        return self._s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=300,
        )

    def _read_s3(self, key: str) -> bytes:
        obj = self._s3().get_object(Bucket=settings.s3_bucket, Key=key)
        return obj["Body"].read()

    def _s3(self):
        import boto3

        return boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )


class WeatherService:
    """Адаптер Open-Meteo: таймаут, одна повторная попытка, кэш и ограничение частоты."""

    def __init__(self, fetcher=None, clock=None):
        self._fetcher = fetcher or self._http_get
        self._clock = clock or time.monotonic
        self._cache: WeatherOut | None = None
        self._cache_until = 0.0
        self._last_call = 0.0

    def current(self) -> WeatherOut:
        now = self._clock()
        if self._cache and now < self._cache_until:
            return self._cache
        if now - self._last_call < 1 and self._cache:
            return self._cache
        if now - self._last_call < 1 and not self._cache:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Слишком частые запросы к внешнему API")
        self._last_call = now
        try:
            payload = self._fetch_with_retry()
        except httpx.HTTPError:
            if self._cache:
                stale = self._cache.model_copy(update={"stale": True, "summary": self._cache.summary + " (кэш)"})
                return stale
            return WeatherOut(
                available=False,
                location=settings.weather_location,
                summary="Сервис погоды временно недоступен",
            )
        code = int(payload.get("weather_code") or 0)
        result = WeatherOut(
            available=True,
            location=settings.weather_location,
            temperature_c=float(payload["temperature_c"]),
            weather_code=code,
            summary=WEATHER_SUMMARY.get(code, "Без описания"),
        )
        self._cache = result
        self._cache_until = now + 600
        return result

    def _fetch_with_retry(self) -> dict:
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                return self._fetcher()
            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt == 1:
                    raise
            except httpx.HTTPError:
                raise
        raise last_error or httpx.HTTPError("weather")

    def _http_get(self) -> dict:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": settings.weather_lat,
            "longitude": settings.weather_lon,
            "current": "temperature_2m,weather_code",
        }
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            current = response.json().get("current") or {}
        if "temperature_2m" not in current:
            raise httpx.HTTPError("пустой ответ Open-Meteo")
        return {"temperature_c": current["temperature_2m"], "weather_code": current.get("weather_code", 0)}
