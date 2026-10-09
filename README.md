# TaskBoard

Доска задач команды на Python, FastAPI, TypeScript и React. Отчёт по работе лежит в [ОТЧЁТ.md](ОТЧЁТ.md).

## Демонстрационные входы

| Роль | Email | Пароль |
| --- | --- | --- |
| Администратор | admin@example.com | Admin12345 |
| Менеджер | manager@example.com | Manager12345 |
| Пользователь | user@example.com | User12345 |

## Запуск без Docker

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

В другом терминале:

```bash
cd frontend
npm install
npm run dev
```

Сайт: http://localhost:5173  
Swagger: http://localhost:8000/docs  
GraphQL: http://localhost:8000/graphql

База по умолчанию — файл SQLite `backend/taskboard.db`. При первом запуске создаются демо-пользователи и задачи.

## Запуск в Docker

```bash
docker compose up --build
```

Сайт открывается на http://localhost:8080. Поднимаются PostgreSQL, MinIO, backend, frontend и Nginx.

## Проверки

```bash
cd backend && pytest
cd frontend && npm test && npm run build
node practicals/02-event-loop/demo.mjs
python practicals/03-sql-nosql/run_demo.py
```

## Что где лежит

| Работа | Где смотреть |
| --- | --- |
| Лаб. 1. Роли и права | `backend/app/permissions.py`, `frontend/src/lib/roles.ts` |
| Лаб. 2. Access и refresh | `backend/app/security.py`, `backend/app/services.py`, `frontend/src/api/client.ts` |
| Лаб. 3. Фильтры и файлы | `frontend/src/components/FilterBar.tsx`, `backend/app/services.py` (`StorageService`) |
| Лаб. 4. SEO и внешний API | `frontend/src/components/Seo.tsx`, `backend/app/pages.py`, погода Open-Meteo |
| Лаб. 5. Тесты | `backend/tests`, `frontend/src/**/*.test.ts` |
| Лаб. 6. Docker и CI | `docker-compose.yml`, `Dockerfile`, `.github/workflows/ci.yml` |
| Практ. 1. Context и Redux | `frontend/src/practical1`, маршруты `/demo/context` и `/demo/redux` |
| Практ. 2. Event loop | `practicals/02-event-loop/demo.mjs` |
| Практ. 3. SQL и NoSQL | `practicals/03-sql-nosql` |
| Практ. 4. REST и GraphQL | `/docs`, `/graphql`, страница `/compare` |
| Практ. 5–8. Дизайн | разделы в `ОТЧЁТ.md` |
