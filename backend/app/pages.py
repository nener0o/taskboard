import html
import json

from app.config import settings
from app.models import Task


def render_task_page(task: Task | None, status_code: int, detail: str) -> str:
    if task is None:
        titles = {403: "Доступ запрещён", 404: "Страница не найдена", 410: "Материал снят"}
        title = titles.get(status_code, "Ошибка")
        return f"""<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8"><title>{title} — TaskBoard</title>
<meta name="robots" content="noindex">
</head><body>
<main>
<h1>{title}</h1>
<p>{html.escape(str(detail))}</p>
<p><a href="{html.escape(settings.frontend_base_url)}/tasks">К каталогу</a></p>
</main>
</body></html>"""

    canonical = f"{settings.frontend_base_url.rstrip('/')}/tasks/{task.id}"
    description = (task.description or task.title)[:180]
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": task.title,
        "description": description,
        "author": {"@type": "Person", "name": task.owner.name if task.owner else "TaskBoard"},
        "datePublished": task.created_at.isoformat(),
        "dateModified": task.updated_at.isoformat(),
        "mainEntityOfPage": canonical,
    }
    return f"""<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8">
<title>{html.escape(task.title)} — TaskBoard</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(task.title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{html.escape(canonical)}">
<script type="application/ld+json">{html.escape(json.dumps(payload, ensure_ascii=False))}</script>
</head><body>
<main>
<p>Публичная задача</p>
<h1>{html.escape(task.title)}</h1>
<h2>Описание</h2>
<p>{html.escape(task.description or "Без описания")}</p>
<h3>Параметры</h3>
<ul>
<li>Статус: {html.escape(task.status.value)}</li>
<li>Приоритет: {html.escape(task.priority.value)}</li>
<li>Автор: {html.escape(task.owner.name if task.owner else "")}</li>
</ul>
</main>
</body></html>"""
