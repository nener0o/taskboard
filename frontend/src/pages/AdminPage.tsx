import { useEffect, useState } from "react";

import { useAuth } from "../auth/AuthContext";
import { api, errorText } from "../api/client";
import type { Role, User } from "../api/types";
import { Seo } from "../components/Seo";
import { ROLE_LABEL } from "../lib/labels";
import { can } from "../lib/roles";

export function AdminPage() {
  const { user } = useAuth();
  const [rows, setRows] = useState<User[]>([]);
  const [message, setMessage] = useState("");
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  function load() {
    setState("loading");
    api
      .get<User[]>("/api/users")
      .then((response) => {
        setRows(response.data);
        setState("ready");
      })
      .catch((error) => {
        setState("error");
        setMessage(errorText(error));
      });
  }

  useEffect(() => {
    load();
  }, []);

  async function changeRole(userId: number, role: Role) {
    setMessage("");
    try {
      await api.patch(`/api/users/${userId}/role`, { role });
      load();
    } catch (error) {
      setMessage(errorText(error));
    }
  }

  const manager = Boolean(user && can(user.role, "user:manage_roles"));

  return (
    <section>
      <Seo title="Роли пользователей — TaskBoard" description="Назначение ролей доступно администратору" path="/admin" index={false} />
      <h1>Роли</h1>
      {state === "loading" ? <p className="status">Загружаем пользователей…</p> : null}
      {state === "error" ? <p className="error">{message}</p> : null}
      {message && state !== "error" ? <p className="error">{message}</p> : null}
      <table className="grid">
        <thead>
          <tr>
            <th>Имя</th>
            <th>Email</th>
            <th>Роль</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>{row.name}</td>
              <td>{row.email}</td>
              <td>
                <select
                  aria-label={`Роль ${row.name}`}
                  value={row.role}
                  disabled={!manager || row.id === user?.id}
                  onChange={(event) => void changeRole(row.id, event.target.value as Role)}
                >
                  {Object.entries(ROLE_LABEL).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!manager ? <p className="meta">Менеджер видит список, но менять роли может только администратор.</p> : null}
    </section>
  );
}
