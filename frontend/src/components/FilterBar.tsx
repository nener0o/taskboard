import type { Filters } from "../lib/filters";
import { PRIORITY_LABEL, STATUS_LABEL } from "../lib/labels";

export function FilterBar({ value, onChange }: { value: Filters; onChange: (next: Filters) => void }) {
  function patch(partial: Partial<Filters>) {
    onChange({ ...value, page: 1, ...partial });
  }

  return (
    <form className="filters" role="search" onSubmit={(event) => event.preventDefault()}>
      <label>
        Поиск
        <input
          value={value.search}
          onChange={(event) => patch({ search: event.target.value })}
          placeholder="Название или описание"
          aria-label="Поиск по задачам"
        />
      </label>
      <label>
        Статус
        <select value={value.status} onChange={(event) => patch({ status: event.target.value })} aria-label="Фильтр по статусу">
          <option value="">Все</option>
          {Object.entries(STATUS_LABEL).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Приоритет
        <select
          value={value.priority}
          onChange={(event) => patch({ priority: event.target.value })}
          aria-label="Фильтр по приоритету"
        >
          <option value="">Все</option>
          {Object.entries(PRIORITY_LABEL).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Сортировка
        <select value={`${value.sort}:${value.order}`} onChange={(event) => {
          const [sort, order] = event.target.value.split(":");
          patch({ sort, order: order as Filters["order"] });
        }} aria-label="Сортировка">
          <option value="created_at:desc">Сначала новые</option>
          <option value="created_at:asc">Сначала старые</option>
          <option value="title:asc">По названию</option>
          <option value="priority:desc">По приоритету</option>
          <option value="updated_at:desc">По обновлению</option>
        </select>
      </label>
    </form>
  );
}
