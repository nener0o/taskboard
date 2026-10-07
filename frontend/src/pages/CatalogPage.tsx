import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api, errorText } from "../api/client";
import type { TaskPage } from "../api/types";
import { FilterBar } from "../components/FilterBar";
import { Seo } from "../components/Seo";
import { Pager, TaskCards } from "../components/TaskCards";
import { filtersToSearchParams, parseFilters, toRequestParams } from "../lib/filters";

export function CatalogPage({
  mine = false,
  title = "Каталог задач",
  path = "/tasks",
  showHeading = true,
}: {
  mine?: boolean;
  title?: string;
  path?: string;
  showHeading?: boolean;
}) {
  const [params, setParams] = useSearchParams();
  const query = params.toString();
  const filters = useMemo(() => parseFilters(params), [query, params]);
  const [data, setData] = useState<TaskPage | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setState("loading");
    api
      .get<TaskPage>("/api/tasks", { params: toRequestParams(filters, mine) })
      .then((response) => {
        setData(response.data);
        setState("ready");
      })
      .catch((error) => {
        setState("error");
        setMessage(errorText(error));
      });
  }, [query, mine, filters]);

  return (
    <section>
      <Seo
        title={`${title} — TaskBoard`}
        description="Поиск, фильтры по статусу и приоритету, сортировка и постраничный список задач."
        path={path}
        index={!mine}
      />
      {showHeading ? (mine ? <h2>{title}</h2> : <h1>{title}</h1>) : null}
      <FilterBar value={filters} onChange={(next) => setParams(filtersToSearchParams(next))} />
      {state === "loading" ? <p className="status">Загружаем задачи…</p> : null}
      {state === "error" ? <p className="error">{message}</p> : null}
      {state === "ready" && data ? (
        <>
          <TaskCards items={data.items} hrefFor={(task) => (mine ? `/app/tasks/${task.id}` : `/tasks/${task.id}`)} />
          <Pager page={data.page} pages={data.pages} onPage={(page) => setParams(filtersToSearchParams({ ...filters, page }))} />
        </>
      ) : null}
    </section>
  );
}
