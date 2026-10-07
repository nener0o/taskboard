import axios from "axios";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { api, errorText } from "../api/client";
import type { Attachment, Task } from "../api/types";
import { FileBox } from "../components/FileBox";
import { Seo } from "../components/Seo";
import { PRIORITY_LABEL, STATUS_LABEL } from "../lib/labels";
import { can, canDeleteTask, canEditTask } from "../lib/roles";

export function TaskPage() {
  const params = useParams();
  const taskId = Number(params.id);
  const { user } = useAuth();
  const [task, setTask] = useState<Task | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [message, setMessage] = useState("");
  const [code, setCode] = useState<number | null>(null);

  useEffect(() => {
    setState("loading");
    api
      .get<Task>(`/api/tasks/${taskId}`)
      .then((response) => {
        setTask(response.data);
        setState("ready");
      })
      .catch((error) => {
        setCode(axios.isAxiosError(error) ? error.response?.status ?? null : null);
        setMessage(errorText(error));
        setState("error");
      });
  }, [taskId]);

  if (state === "loading") return <p className="status">Загружаем задачу…</p>;
  if (state === "error" || !task) {
    const heading = code === 410 ? "Материал снят с публикации" : code === 403 ? "Недостаточно прав" : "Задача не найдена";
    return (
      <section>
        <Seo title={`${heading} — TaskBoard`} description={message} path={`/tasks/${taskId}`} index={false} />
        <h1>{heading}</h1>
        <p className="error">{message}</p>
        <Link to="/tasks">Вернуться в каталог</Link>
      </section>
    );
  }

  const editable = user ? canEditTask(user.role, task.owner_id, task.assignee_id, user.id) : false;
  const removable = user ? canDeleteTask(user.role, task.owner_id, user.id) : false;
  const upload = Boolean(user && can(user.role, "file:upload") && (can(user.role, "task:update_any") || task.owner_id === user.id || task.assignee_id === user.id));

  return (
    <article>
      <Seo
        title={`${task.title} — TaskBoard`}
        description={(task.description || task.title).slice(0, 180)}
        path={`/tasks/${task.id}`}
        index={task.is_public && task.status !== "archived"}
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "Article",
          headline: task.title,
          description: task.description,
          author: { "@type": "Person", name: task.owner_name },
          dateModified: task.updated_at,
        }}
      />
      <p className="kicker">{task.is_public ? "Публичная задача" : "Внутренняя задача"}</p>
      <h1>{task.title}</h1>
      <p className="chips">
        <span className={`chip status-${task.status}`}>{STATUS_LABEL[task.status]}</span>
        <span className={`chip priority-${task.priority}`}>{PRIORITY_LABEL[task.priority]}</span>
      </p>
      <h2>Описание</h2>
      <p>{task.description || "Без описания"}</p>
      <h3>Участники</h3>
      <p>
        Автор: {task.owner_name}. Исполнитель: {task.assignee_name || "не назначен"}.
      </p>
      <p className="actions">
        {editable ? <Link className="button" to={`/app/tasks/${task.id}`}>Редактировать</Link> : null}
        {user && !removable ? <button type="button" disabled title="Удаление недоступно для вашей роли">Удалить</button> : null}
      </p>
      <FileBox
        taskId={task.id}
        canUpload={upload}
        canDelete={(file: Attachment) => {
          if (!user) return false;
          if (can(user.role, "file:delete_any")) return true;
          return file.uploaded_by === user.id && can(user.role, "file:delete_own");
        }}
      />
    </article>
  );
}
