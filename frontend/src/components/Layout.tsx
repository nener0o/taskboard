import { Link } from "react-router-dom";

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand" aria-label="TaskBoard, на главную">
          <span className="mark" aria-hidden="true" />
          TaskBoard
        </Link>
      </header>
      <main className="page">{children}</main>
    </div>
  );
}
