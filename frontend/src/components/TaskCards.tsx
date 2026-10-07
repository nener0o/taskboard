import { Link } from "react-router-dom";

import type { Task } from "../api/types";
import { PRIORITY_LABEL, STATUS_LABEL } from "../lib/labels";

export function TaskCards({ items, hrefFor }: { items: Task[]; hrefFor: (task: Task) => string }) {
  if (items.length === 0) {
    return <p className="empty">Ничего не найдено. Измените фильтры или создайте задачу.</p>;
  }
  return (
    <ul className="cards">
      {items.map((task) => (
        <li key={task.id} className="card">
          <div className="chips">
            <span className={`chip status-${task.status}`}>{STATUS_LABEL[task.status] || task.status}</span>
            <span className={`chip priority-${task.priority}`}>{PRIORITY_LABEL[task.priority] || task.priority}</span>
            {task.is_public ? <span className="chip">Публичная</span> : <span className="chip">Скрытая</span>}
          </div>
          <h2>
            <Link to={hrefFor(task)}>{task.title}</Link>
          </h2>
          <p>{task.description || "Без описания"}</p>
          <p className="meta">
            Автор: {task.owner_name}
            {task.assignee_name ? ` · Исполнитель: ${task.assignee_name}` : ""}
          </p>
        </li>
      ))}
    </ul>
  );
}

export function Pager({ page, pages, onPage }: { page: number; pages: number; onPage: (page: number) => void }) {
  return (
    <div className="pager">
      <button type="button" disabled={page <= 1} onClick={() => onPage(page - 1)}>
        Назад
      </button>
      <span>
        Страница {page} из {pages}
      </span>
      <button type="button" disabled={page >= pages} onClick={() => onPage(page + 1)}>
        Дальше
      </button>
    </div>
  );
}
