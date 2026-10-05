import { Link } from "react-router-dom";

import { Seo } from "../components/Seo";

export function ForbiddenPage() {
  return (
    <section>
      <Seo title="Доступ запрещён — TaskBoard" description="Недостаточно прав" path="/forbidden" index={false} />
      <h1>Недостаточно прав</h1>
      <p>Этот раздел закрыт для текущей роли.</p>
      <Link to="/">На главную</Link>
    </section>
  );
}

export function NotFoundPage() {
  return (
    <section>
      <Seo title="Страница не найдена — TaskBoard" description="Такого адреса нет" path="/404" index={false} />
      <h1>Страница не найдена</h1>
      <p>Проверьте адрес или откройте каталог задач.</p>
      <Link to="/tasks">К каталогу</Link>
    </section>
  );
}
