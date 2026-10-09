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
