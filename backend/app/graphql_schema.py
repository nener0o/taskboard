import strawberry
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter

from app.database import get_db
from app.models import User
from app.schemas import TaskIn
from app.security import decode_access_token
from app.services import TaskService, UserService


@strawberry.type
class GTask:
    id: int
    title: str
    description: str
    status: str
    user_id: int


@strawberry.type
class GUser:
    id: int
    name: str
    email: str
    tasks: list[GTask]


def _task(row) -> GTask:
    return GTask(
        id=row.id,
        title=row.title,
        description=row.description,
        status=row.status.value,
        user_id=row.owner_id,
    )


def _user_with_tasks(user: User, service: TaskService) -> GUser:
    rows, _total = service.search(
        None,
        search=None,
        status=None,
        priority=None,
        owner_id=user.id,
        mine=False,
        sort="created_at",
        order="desc",
        page=1,
        page_size=50,
    )
    return GUser(id=user.id, name=user.name, email=user.email, tasks=[_task(row) for row in rows])


@strawberry.type
class Query:
    @strawberry.field
    def users(self, info: strawberry.Info) -> list[GUser]:
        db: Session = info.context["db"]
        service = TaskService(db)
        people = UserService(db).directory()
        return [_user_with_tasks(person, service) for person in people]

    @strawberry.field
    def user(self, info: strawberry.Info, id: int) -> GUser | None:
        db: Session = info.context["db"]
        person = db.get(User, id)
        if not person:
            return None
        return _user_with_tasks(person, TaskService(db))

    @strawberry.field
    def tasks(self, info: strawberry.Info) -> list[GTask]:
        rows, _total = TaskService(info.context["db"]).search(
            None, search=None, status=None, priority=None, owner_id=None, mine=False, sort="created_at", order="desc", page=1, page_size=50
        )
        return [_task(row) for row in rows]

    @strawberry.field
    def task(self, info: strawberry.Info, id: int) -> GTask | None:
        try:
            row = TaskService(info.context["db"]).get_visible(id, None)
        except Exception:
            return None
        return _task(row)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_task(self, info: strawberry.Info, title: str, description: str = "", user_id: int | None = None) -> GTask:
        actor: User | None = info.context["user"]
        if actor is None:
            raise PermissionError("Требуется access token")
        if user_id is not None and user_id != actor.id and actor.role.value != "admin":
            raise PermissionError("Нельзя создавать задачу от чужого имени")
        row = TaskService(info.context["db"]).create(
            actor,
            TaskIn(title=title, description=description, is_public=True),
        )
        return _task(row)


schema = strawberry.Schema(query=Query, mutation=Mutation)


def get_context(request: Request, db: Session = Depends(get_db)) -> dict:
    user = None
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        try:
            payload = decode_access_token(header.split(" ", 1)[1])
            user = db.get(User, int(payload["sub"]))
        except Exception:
            user = None
    return {"db": db, "user": user, "request": request}


graphql_router = GraphQLRouter(schema, context_getter=get_context)
