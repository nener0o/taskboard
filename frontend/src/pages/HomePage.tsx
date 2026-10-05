import { Link } from "react-router-dom";

import { Seo } from "../components/Seo";

export function HomePage() {
  return (
    <article className="home">
      <Seo
        title="TaskBoard — доска задач команды"
        description="Публичный каталог задач, роли доступа и вложения. Доска задач на FastAPI и React."
        path="/"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "WebSite",
          name: "TaskBoard",
          description: "Доска задач команды с ролями guest, user, manager и admin.",
          url: typeof window === "undefined" ? "http://localhost:5173/" : window.location.origin,
        }}
      />
      <p className="kicker">Доска задач команды</p>
      <h1>Доска задач, в которой права доступа видны сразу</h1>
      <p className="lead">
        TaskBoard ведёт задачи команды: гость читает публичный каталог, пользователь работает со своими карточками,
        менеджер модерирует, администратор назначает роли.
      </p>
      <p>
        <Link className="button" to="/tasks">
          Открыть каталог
        </Link>
      </p>
      <section>
        <h2>Как устроен доступ</h2>
        <ul className="roles">
          <li>
            <h3>Гость</h3>
            <p>Видит только публичные задачи и не может ничего менять.</p>
          </li>
          <li>
            <h3>Пользователь</h3>
            <p>Создаёт и редактирует свои задачи, прикрепляет файлы. Удаление ему закрыто.</p>
          </li>
          <li>
            <h3>Менеджер</h3>
            <p>Видит все карточки, правит чужие и удаляет только свои.</p>
          </li>
          <li>
            <h3>Администратор</h3>
            <p>Удаляет любые задачи и меняет роли остальных.</p>
          </li>
        </ul>
      </section>
      <section>
        <h2>Демонстрационные входы</h2>
        <ul>
          <li>admin@example.com / Admin12345</li>
          <li>manager@example.com / Manager12345</li>
          <li>user@example.com / User12345</li>
        </ul>
      </section>
    </article>
  );
}
