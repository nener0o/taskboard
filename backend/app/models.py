import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _enum(kind: type[enum.Enum]) -> Enum:
    return Enum(kind, native_enum=False, length=32, values_callable=lambda items: [item.value for item in items])


class Role(str, enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    ARCHIVED = "archived"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(_enum(Role), default=Role.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner", foreign_keys="Task.owner_id")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    replaced_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    search_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[TaskStatus] = mapped_column(_enum(TaskStatus), default=TaskStatus.TODO, index=True)
    priority: Mapped[TaskPriority] = mapped_column(_enum(TaskPriority), default=TaskPriority.MEDIUM, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    owner: Mapped[User] = relationship(foreign_keys=[owner_id], back_populates="tasks")
    assignee: Mapped[User | None] = relationship(foreign_keys=[assignee_id])
    files: Mapped[list["Attachment"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    size: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    task: Mapped[Task] = relationship(back_populates="files")


@event.listens_for(Task, "before_insert")
@event.listens_for(Task, "before_update")
def fill_task_search(_mapper, _connection, target: Task) -> None:
    target.search_text = f"{target.title or ''}\n{target.description or ''}".casefold()
