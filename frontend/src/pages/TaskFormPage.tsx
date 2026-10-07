import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { api, errorText } from "../api/client";
import type { Task } from "../api/types";
import { FileBox } from "../components/FileBox";
import { Seo } from "../components/Seo";
import { validateTask } from "../lib/filters";
import { PRIORITY_LABEL, STATUS_LABEL } from "../lib/labels";
import { can, canDeleteTask } from "../lib/roles";

type Person = { id: number; name: string };

export function TaskFormPage() {
  const { id } = useParams();
  const editing = Boolean(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("todo");
  const [priority, setPriority] = useState("medium");
  const [isPublic, setIsPublic] = useState(false);
  const [assigneeId, setAssigneeId] = useState("");
  const [people, setPeople] = useState<Person[]>([]);
  const [ownerId, setOwnerId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const [loading, setLoading] = useState(editing);

  useEffect(() => {
    api
      .get<Person[]>("/api/users/directory")
      .then((response) => setPeople(response.data))
      .catch(() => setPeople([]));
  }, []);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api
      .get<Task>(`/api/tasks/${id}`)
      .then((response) => {
        const task = response.data;
        setTitle(task.title);
        setDescription(task.description);
        setStatus(task.status);
        setPriority(task.priority);
        setIsPublic(task.is_public);
        setAssigneeId(task.assignee_id ? String(task.assignee_id) : "");
        setOwnerId(task.owner_id);
        setLoading(false);
      })
      .catch((err) => {
        setError(errorText(err));
        setLoading(false);
      });
  }, [id]);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const problem = validateTask(title, description);
    if (problem) {
      setError(problem);
      return;
    }
    const payload = {
      title: title.trim(),
      description: description.trim(),
      status,
      priority,
      is_public: isPublic,
      assignee_id: assigneeId ? Number(assigneeId) : null,
    };
    setPending(true);
    try {
      const response = editing
        ? await api.patch<Task>(`/api/tasks/${id}`, payload)
        : await api.post<Task>("/api/tasks", payload);
      navigate(`/tasks/${response.data.id}`);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setPending(false);
    }
  }

  async function remove() {
    if (!id) return;
    setPending(true);
    try {
      await api.delete(`/api/tasks/${id}`);
      navigate("/app");
    } catch (err) {
      setError(errorText(err));
      setPending(false);
    }
  }

  const allowDelete = Boolean(user && ownerId && canDeleteTask(user.role, ownerId, user.id));

  return (
    <section className="narrow">
      <Seo title={editing ? "Редактирование задачи" : "Новая задача"} description="Форма задачи TaskBoard" path={editing ? `/app/tasks/${id}` : "/app/tasks/new"} index={false} />
      <h1>{editing ? "Редактирование" : "Новая задача"}</h1>
      {loading ? <p className="status">Загружаем карточку…</p> : null}
      <form className="stack" onSubmit={(event) => void onSubmit(event)}>
        <label>
          Название
          <input value={title} onChange={(event) => setTitle(event.target.value)} />
        </label>
        <label>
          Описание
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={5} />
        </label>
        <label>
          Статус
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            {Object.entries(STATUS_LABEL).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </label>
        <label>
          Приоритет
          <select value={priority} onChange={(event) => setPriority(event.target.value)}>
            {Object.entries(PRIORITY_LABEL).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </label>
        <label>
          Исполнитель
          <select value={assigneeId} onChange={(event) => setAssigneeId(event.target.value)}>
            <option value="">Не назначен</option>
            {people.map((person) => (
              <option key={person.id} value={person.id}>{person.name}</option>
            ))}
          </select>
        </label>
        <label className="check">
          <input type="checkbox" checked={isPublic} onChange={(event) => setIsPublic(event.target.checked)} />
          Показывать в публичном каталоге
        </label>
        {error ? <p className="error" role="alert">{error}</p> : null}
        <button className="button" type="submit" disabled={pending || loading}>
          {pending ? "Сохраняем…" : "Сохранить"}
        </button>
      </form>
      {editing && allowDelete ? (
        <button type="button" className="danger" onClick={() => void remove()} disabled={pending}>
          Удалить задачу
        </button>
      ) : null}
      {editing && user && !allowDelete ? <p className="meta">Удаление скрыто: у роли {user.role} нет такого права.</p> : null}
      {editing && id && user ? (
        <FileBox
          taskId={Number(id)}
          canUpload={can(user.role, "file:upload")}
          canDelete={(file) => can(user.role, "file:delete_any") || (file.uploaded_by === user.id && can(user.role, "file:delete_own"))}
        />
      ) : null}
    </section>
  );
}
