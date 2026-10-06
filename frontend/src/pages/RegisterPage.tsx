import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api, errorText } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { Seo } from "../components/Seo";
import { validateCredentials } from "../lib/filters";

export function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (name.trim().length < 2) {
      setError("Имя короче 2 символов");
      return;
    }
    const problem = validateCredentials(email, password);
    if (problem) {
      setError(problem);
      return;
    }
    setPending(true);
    try {
      await api.post("/api/auth/register", { name: name.trim(), email: email.trim(), password });
      await login(email.trim(), password);
      navigate("/app");
    } catch (err) {
      setError(errorText(err));
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="narrow">
      <Seo title="Регистрация — TaskBoard" description="Создание учётной записи пользователя" path="/register" index={false} />
      <h1>Регистрация</h1>
      <form className="stack" onSubmit={(event) => void onSubmit(event)}>
        <label>
          Имя
          <input value={name} onChange={(event) => setName(event.target.value)} />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          Пароль
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error ? <p className="error" role="alert">{error}</p> : null}
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Создаём…" : "Создать аккаунт"}
        </button>
      </form>
      <p>
        Уже есть вход? <Link to="/login">Войти</Link>
      </p>
    </section>
  );
}
