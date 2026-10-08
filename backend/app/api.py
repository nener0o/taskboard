from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response

from app.config import settings
from app.deps import AuthDep, CurrentUser, OptionalUser, StorageDep, TaskDep, UserDep, WeatherDep, require_permission
from app.models import TaskPriority, TaskStatus, User
from app.pages import render_task_page
from app.permissions import PERMISSIONS, ROLE_PERMISSIONS
from app.repositories import TaskRepository
from app.schemas import (
    FileOut,
    LoginIn,
    MessageOut,
    PageOut,
    RefreshIn,
    RegisterIn,
    RoleUpdate,
    TaskIn,
    TaskOut,
    TaskUpdate,
    TokenOut,
    UserDirectoryItem,
    UserOut,
    WeatherOut,
)
from app.services import task_out

api = APIRouter()
Creator = Annotated[User, Depends(require_permission("task:create"))]


@api.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@api.get("/meta/permissions")
def permission_matrix() -> dict:
    return {
        "guest": ["task:read_public"],
        "permissions": PERMISSIONS,
        "roles": {role.value: sorted(items) for role, items in ROLE_PERMISSIONS.items()},
    }


@api.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, auth: AuthDep, users: UserDep) -> dict:
    return users.to_out(auth.register(data.name, data.email, data.password))


@api.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, auth: AuthDep) -> dict:
    return auth.login(data.email, data.password)


@api.post("/auth/refresh", response_model=TokenOut)
def refresh(data: RefreshIn, auth: AuthDep) -> dict:
    return auth.refresh(data.refresh_token)


@api.post("/auth/logout", response_model=MessageOut)
def logout(data: RefreshIn, auth: AuthDep) -> dict:
    auth.logout(data.refresh_token)
    return {"detail": "Сессия завершена"}


@api.get("/auth/me", response_model=UserOut)
def me(user: CurrentUser, users: UserDep) -> dict:
    return users.to_out(user)


@api.get("/users", response_model=list[UserOut])
def list_users(actor: CurrentUser, users: UserDep) -> list[dict]:
    return [users.to_out(item) for item in users.list_users(actor)]


@api.get("/users/directory", response_model=list[UserDirectoryItem])
def directory(actor: CurrentUser, users: UserDep) -> list[UserDirectoryItem]:
    del actor
    return [UserDirectoryItem(id=item.id, name=item.name) for item in users.directory()]


@api.patch("/users/{user_id}/role", response_model=UserOut)
def change_role(user_id: int, data: RoleUpdate, actor: CurrentUser, users: UserDep) -> dict:
    return users.to_out(users.change_role(actor, user_id, data.role))


@api.get("/tasks", response_model=PageOut)
def list_tasks(
    tasks: TaskDep,
    viewer: OptionalUser,
    search: str | None = Query(default=None, max_length=200),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    owner_id: int | None = None,
    mine: bool = False,
    sort: str = Query(default="created_at", pattern="^(created_at|updated_at|title|priority|status)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
) -> PageOut:
    if mine and viewer is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Фильтр «мои» доступен после входа")
    rows, total = tasks.search(
        viewer,
        search=search,
        status=status_filter,
        priority=priority,
        owner_id=owner_id,
        mine=mine,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    pages = max(1, (total + page_size - 1) // page_size) if total else 1
    return PageOut(
        items=[task_out(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@api.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskIn, tasks: TaskDep, actor: Creator) -> TaskOut:
    return task_out(tasks.create(actor, data))


@api.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, tasks: TaskDep, viewer: OptionalUser) -> TaskOut:
    return task_out(tasks.get_visible(task_id, viewer))


@api.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, tasks: TaskDep, actor: CurrentUser) -> TaskOut:
    return task_out(tasks.update(actor, task_id, data))


@api.delete("/tasks/{task_id}", response_model=MessageOut)
def delete_task(task_id: int, tasks: TaskDep, actor: CurrentUser) -> dict:
    tasks.delete(actor, task_id)
    return {"detail": "Задача удалена"}


@api.get("/tasks/{task_id}/files", response_model=list[FileOut])
def list_files(task_id: int, storage: StorageDep, viewer: OptionalUser) -> list[FileOut]:
    return [storage.to_out(row) for row in storage.list_files(viewer, task_id)]


@api.post("/tasks/{task_id}/files", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    task_id: int,
    storage: StorageDep,
    actor: CurrentUser,
    file: UploadFile = File(...),
) -> FileOut:
    data = await file.read()
    row = storage.upload(actor, task_id, file.filename or "file", file.content_type or "", data)
    return storage.to_out(row)


@api.delete("/files/{file_id}", response_model=MessageOut)
def delete_file(file_id: int, storage: StorageDep, actor: CurrentUser) -> dict:
    storage.delete(actor, file_id)
    return {"detail": "Файл удалён"}


@api.get("/files/{file_id}/content")
def download_file(file_id: int, token: str, storage: StorageDep):
    path, data, row = storage.open(file_id, token)
    disposition = f'inline; filename="{row.original_name}"'
    if path is not None:
        return FileResponse(path, media_type=row.content_type, filename=row.original_name)
    return Response(content=data, media_type=row.content_type, headers={"Content-Disposition": disposition})


@api.get("/integrations/weather", response_model=WeatherOut)
def weather(service: WeatherDep) -> WeatherOut:
    return service.current()


public = APIRouter()


@public.get("/robots.txt", response_class=PlainTextResponse)
def robots() -> str:
    base = settings.public_base_url.rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /tasks\n"
        "Disallow: /app\n"
        "Disallow: /login\n"
        "Disallow: /register\n"
        "Disallow: /admin\n"
        "Disallow: /demo\n"
        "Disallow: /compare\n"
        "Disallow: /api/\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )


@public.get("/sitemap.xml")
def sitemap(tasks: TaskDep) -> Response:
    base = settings.frontend_base_url.rstrip("/")
    urls = [f"{base}/", f"{base}/tasks"]
    for task in TaskRepository(tasks.db).public_for_sitemap():
        lastmod = task.updated_at.date().isoformat()
        urls.append(f"{base}/tasks/{task.id}|{lastmod}")
    body = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for item in urls:
        loc, _, lastmod = item.partition("|")
        body.append("<url>")
        body.append(f"<loc>{loc}</loc>")
        if lastmod:
            body.append(f"<lastmod>{lastmod}</lastmod>")
        body.append("</url>")
    body.append("</urlset>")
    return Response("\n".join(body), media_type="application/xml")


@public.get("/pages/tasks/{task_id}", response_class=HTMLResponse)
def public_task_page(task_id: int, tasks: TaskDep) -> HTMLResponse:
    try:
        task = tasks.get_visible(task_id, None)
    except HTTPException as exc:
        return HTMLResponse(render_task_page(None, exc.status_code, exc.detail), status_code=exc.status_code)
    return HTMLResponse(render_task_page(task, 200, ""))
