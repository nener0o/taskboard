import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { WeatherCard } from "../components/WeatherCard";
import { CatalogPage } from "./CatalogPage";

export function BoardPage() {
  const { user } = useAuth();
  return (
    <section>
      <div className="split">
        <div>
          <p className="kicker">Личная доска</p>
          <h1>{user?.role === "user" ? "Мои задачи" : "Все задачи"}</h1>
          <p>
            <Link className="button" to="/app/tasks/new">
              Новая задача
            </Link>
          </p>
        </div>
        <WeatherCard />
      </div>
      <CatalogPage
        mine={user?.role === "user"}
        title={user?.role === "user" ? "Мои задачи" : "Все задачи команды"}
        path="/app"
        showHeading={false}
      />
    </section>
  );
}
