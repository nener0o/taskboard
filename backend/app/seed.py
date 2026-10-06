from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Role, Task, TaskPriority, TaskStatus, User
from app.security import hash_password

DEMO_USERS = [
    ("Анна", "admin@example.com", "Admin12345", Role.ADMIN),
    ("Игорь", "manager@example.com", "Manager12345", Role.MANAGER),
    ("Ольга", "user@example.com", "User12345", Role.USER),
]


def seed(db: Session) -> None:
    by_email: dict[str, User] = {}
    for name, email, password, role in DEMO_USERS:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            by_email[email] = existing
            continue
        user = User(name=name, email=email, password_hash=hash_password(password), role=role)
        db.add(user)
        db.flush()
        by_email[email] = user

    total = int(db.scalar(select(func.count()).select_from(Task)) or 0)
    if total == 0:
        owner = by_email["user@example.com"]
        manager = by_email["manager@example.com"]
        db.add_all(
            [
                Task(
                    title="Собрать требования к доске",
                    description="Описать роли guest, user, manager и admin и сценарии канбан-доски.",
                    status=TaskStatus.DONE,
                    priority=TaskPriority.HIGH,
                    is_public=True,
                    owner_id=manager.id,
                ),
                Task(
                    title="Подготовить публичный каталог",
                    description="Список задач с поиском, фильтром по статусу и приоритету, сортировкой и страницами.",
                    status=TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.MEDIUM,
                    is_public=True,
                    owner_id=owner.id,
                    assignee_id=manager.id,
                ),
                Task(
                    title="Проверить загрузку вложений",
                    description="К задаче можно прикрепить изображение, pdf или txt не больше 5 МБ.",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.LOW,
                    is_public=True,
                    owner_id=owner.id,
                ),
                Task(
                    title="Личная черновая задача",
                    description="Эту задачу видит только владелец, менеджер и администратор.",
                    status=TaskStatus.REVIEW,
                    priority=TaskPriority.HIGH,
                    is_public=False,
                    owner_id=owner.id,
                ),
            ]
        )
    db.commit()
