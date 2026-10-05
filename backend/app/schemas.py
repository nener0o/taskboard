from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import Role, TaskPriority, TaskStatus


def _password_ok(value: str) -> str:
    if len(value) < 8 or len(value) > 72:
        raise ValueError("Пароль должен быть от 8 до 72 символов")
    if not any(ch.isalpha() for ch in value) or not any(ch.isdigit() for ch in value):
        raise ValueError("Пароль должен содержать букву и цифру")
    return value


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_rules(cls, value: str) -> str:
        return _password_ok(value)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=10)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    is_active: bool
    permissions: list[str] = []

    model_config = {"from_attributes": True}


class UserDirectoryItem(BaseModel):
    id: int
    name: str


class RoleUpdate(BaseModel):
    role: Role


class TaskIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=5000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    is_public: bool = False
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    is_public: bool | None = None
    assignee_id: int | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    is_public: bool
    owner_id: int
    assignee_id: int | None
    owner_name: str
    assignee_name: str | None
    created_at: datetime
    updated_at: datetime


class PageOut(BaseModel):
    items: list[TaskOut]
    total: int
    page: int
    page_size: int
    pages: int


class FileOut(BaseModel):
    id: int
    task_id: int
    original_name: str
    content_type: str
    size: int
    uploaded_by: int
    created_at: datetime
    download_url: str


class WeatherOut(BaseModel):
    available: bool
    location: str
    temperature_c: float | None = None
    weather_code: int | None = None
    summary: str
    source: str = "open-meteo"
    stale: bool = False


class MessageOut(BaseModel):
    detail: str
