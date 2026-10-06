from datetime import datetime

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Attachment, RefreshToken, Role, Task, TaskPriority, TaskStatus, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(func.lower(User.email) == email.lower()))

    def by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def list_users(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)))

    def count_admins(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(User).where(User.role == Role.ADMIN)) or 0)

    def directory(self) -> list[User]:
        return list(self.db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.name)))


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        return token

    def by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    def revoke_all(self, user_id: int) -> None:
        rows = self.db.scalars(select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)))
        for row in rows:
            row.revoked = True


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        return task

    def get(self, task_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id).options(selectinload(Task.owner), selectinload(Task.assignee))
        return self.db.scalar(stmt)

    def delete(self, task: Task) -> None:
        self.db.delete(task)

    def public_for_sitemap(self) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.is_public.is_(True), Task.status != TaskStatus.ARCHIVED)
            .order_by(Task.updated_at.desc())
        )
        return list(self.db.scalars(stmt))

    def search(
        self,
        *,
        viewer: User | None,
        search: str | None,
        status: TaskStatus | None,
        priority: TaskPriority | None,
        owner_id: int | None,
        mine: bool,
        sort: str,
        order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Task], int]:
        stmt = select(Task).options(selectinload(Task.owner), selectinload(Task.assignee))
        stmt = self._visibility(stmt, viewer, mine)
        if search:
            needle = f"%{search.strip().casefold()}%"
            stmt = stmt.where(Task.search_text.like(needle))
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        if owner_id:
            stmt = stmt.where(Task.owner_id == owner_id)

        total = int(self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0)
        columns = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "priority": Task.priority,
            "status": Task.status,
        }
        column = columns[sort]
        stmt = stmt.order_by(column.desc() if order == "desc" else column.asc(), Task.id.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt)), total

    def _visibility(self, stmt: Select[tuple[Task]], viewer: User | None, mine: bool) -> Select[tuple[Task]]:
        if viewer is None:
            return stmt.where(Task.is_public.is_(True), Task.status != TaskStatus.ARCHIVED)
        if viewer.role == Role.USER:
            own = or_(Task.owner_id == viewer.id, Task.assignee_id == viewer.id)
            visible = or_(own, and_(Task.is_public.is_(True), Task.status != TaskStatus.ARCHIVED))
            stmt = stmt.where(visible)
            if mine:
                stmt = stmt.where(own)
            return stmt
        if mine:
            stmt = stmt.where(or_(Task.owner_id == viewer.id, Task.assignee_id == viewer.id))
        return stmt


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, row: Attachment) -> Attachment:
        self.db.add(row)
        self.db.flush()
        return row

    def get(self, file_id: int) -> Attachment | None:
        return self.db.scalar(
            select(Attachment).where(Attachment.id == file_id).options(selectinload(Attachment.task))
        )

    def list_for_task(self, task_id: int) -> list[Attachment]:
        return list(self.db.scalars(select(Attachment).where(Attachment.task_id == task_id).order_by(Attachment.id)))

    def delete(self, row: Attachment) -> None:
        self.db.delete(row)


def touch(task: Task, now: datetime) -> None:
    task.updated_at = now
