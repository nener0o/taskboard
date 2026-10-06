import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { errorText } from "../api/client";
import { Seo } from "../components/Seo";
import { validateCredentials } from "../lib/filters";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const from = (location.state as { from?: string } | null)?.from || "/app";

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const problem = validateCredentials(email, password);
    if (problem) {
      setError(problem);
      return;
    }
    setPending(true);
    try {
      await login(email.trim(), password);
      navigate(from);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="narrow">
      <Seo title="Вход — TaskBoard" description="Вход в доску задач" path="/login" index={false} />
      <h1>Вход</h1>
      <form className="stack" onSubmit={(event) => void onSubmit(event)}>
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" />
        </label>
        <label>
          Пароль
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
        </label>
        {error ? <p className="error" role="alert">{error}</p> : null}
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Входим…" : "Войти"}
        </button>
      </form>
      <p>
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </p>
    </section>
  );
}
