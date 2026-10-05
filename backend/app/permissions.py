from app.models import Role

# Разрешения. Гость не хранится в БД: у него есть только чтение публичных задач.
PERMISSIONS: dict[str, str] = {
    "task:read_public": "Просмотр публичных задач",
    "task:read_own": "Просмотр своих задач",
    "task:read_all": "Просмотр всех задач",
    "task:create": "Создание задач",
    "task:update_own": "Редактирование своих задач",
    "task:update_any": "Редактирование любых задач",
    "task:delete_own": "Удаление своих задач",
    "task:delete_any": "Удаление любых задач",
    "task:moderate": "Модерация и архивация чужих задач",
    "file:upload": "Загрузка файлов",
    "file:delete_own": "Удаление своих файлов",
    "file:delete_any": "Удаление любых файлов",
    "user:read": "Просмотр списка пользователей",
    "user:manage_roles": "Назначение ролей",
}

ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.USER: {
        "task:read_public",
        "task:read_own",
        "task:create",
        "task:update_own",
        "file:upload",
        "file:delete_own",
    },
    Role.MANAGER: {
        "task:read_public",
        "task:read_own",
        "task:read_all",
        "task:create",
        "task:update_own",
        "task:update_any",
        "task:delete_own",
        "task:moderate",
        "file:upload",
        "file:delete_own",
        "file:delete_any",
        "user:read",
    },
    Role.ADMIN: set(PERMISSIONS),
}


def permissions_for(role: Role) -> set[str]:
    return set(ROLE_PERMISSIONS[role])


def has_permission(role: Role, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS[role]
