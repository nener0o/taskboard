import { useEffect, useState } from "react";

import { api, errorText } from "../api/client";
import type { Attachment } from "../api/types";

export function FileBox({
  taskId,
  canUpload,
  canDelete,
}: {
  taskId: number;
  canUpload: boolean;
  canDelete: (file: Attachment) => boolean;
}) {
  const [files, setFiles] = useState<Attachment[]>([]);
  const [state, setState] = useState<"idle" | "loading" | "error" | "uploading">("loading");
  const [message, setMessage] = useState("");

  function reload() {
    setState("loading");
    api
      .get<Attachment[]>(`/api/tasks/${taskId}/files`)
      .then((response) => {
        setFiles(response.data);
        setState("idle");
        setMessage("");
      })
      .catch((error) => {
        setState("error");
        setMessage(errorText(error));
      });
  }

  useEffect(() => {
    reload();
  }, [taskId]);

  async function onPick(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    setState("uploading");
    setMessage("Отправляем файл…");
    try {
      await api.post(`/api/tasks/${taskId}/files`, body);
      setMessage("Файл загружен");
      reload();
    } catch (error) {
      setState("error");
      setMessage(errorText(error));
    }
  }

  async function remove(file: Attachment) {
    try {
      await api.delete(`/api/files/${file.id}`);
      reload();
    } catch (error) {
      setMessage(errorText(error));
    }
  }

  return (
    <section className="files">
      <h2>Вложения</h2>
      {state === "loading" ? <p className="status">Загружаем список файлов…</p> : null}
      {state === "error" ? <p className="error">{message}</p> : null}
      {state !== "loading" && files.length === 0 ? <p className="empty">Файлов пока нет.</p> : null}
      <ul className="file-list">
        {files.map((file) => (
          <li key={file.id}>
            {file.content_type.startsWith("image/") ? (
              <img src={file.download_url} alt={file.original_name} loading="lazy" width={180} height={120} />
            ) : null}
            <a href={file.download_url}>{file.original_name}</a>
            <span className="meta">{Math.ceil(file.size / 1024)} КБ</span>
            {canDelete(file) ? (
              <button type="button" className="ghost" onClick={() => void remove(file)}>
                Удалить
              </button>
            ) : null}
          </li>
        ))}
      </ul>
      {canUpload ? (
        <label className="upload">
          Прикрепить png, jpg, webp, gif, pdf или txt до 5 МБ
          <input type="file" accept=".png,.jpg,.jpeg,.webp,.gif,.pdf,.txt" onChange={(event) => void onPick(event)} />
        </label>
      ) : (
        <p className="meta">Загрузка недоступна для этой роли или чужой задачи.</p>
      )}
      {state === "uploading" ? <p className="status">{message}</p> : null}
    </section>
  );
}
