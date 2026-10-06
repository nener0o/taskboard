import { Link, NavLink } from "react-router-dom";

import { ROLE_LABEL } from "../lib/labels";
import { can } from "../lib/roles";
import { useAuth } from "../auth/AuthContext";

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand" aria-label="TaskBoard, на главную">
          <span className="mark" aria-hidden="true" />
          TaskBoard
        </Link>
        <nav className="nav" aria-label="Основное меню">
          <NavLink to="/tasks">Каталог</NavLink>
          <NavLink to="/compare">REST и GraphQL</NavLink>
          <NavLink to="/demo/context">Context</NavLink>
          <NavLink to="/demo/redux">Redux</NavLink>
          {user ? <NavLink to="/app">Доска</NavLink> : null}
          {user && can(user.role, "user:read") ? <NavLink to="/admin">Роли</NavLink> : null}
        </nav>
        <div className="session">
          {user ? (
            <>
              <span className="who">
                {user.name}
                <small>{ROLE_LABEL[user.role]}</small>
              </span>
              <button type="button" className="ghost" onClick={() => void logout()}>
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Войти</Link>
              <Link to="/register" className="button">
                Регистрация
              </Link>
            </>
          )}
        </div>
      </header>
      <main className="page">{children}</main>
    </div>
  );
}
