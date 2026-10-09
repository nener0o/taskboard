import { useState } from "react";

import { api, errorText } from "../api/client";
import { Seo } from "../components/Seo";

type Report = {
  restRequests: number;
  restBytes: number;
  gqlRequests: number;
  gqlBytes: number;
  restPreview: string;
  gqlPreview: string;
};

export function ComparePage() {
  const [report, setReport] = useState<Report | null>(null);
  const [state, setState] = useState<"idle" | "loading" | "empty" | "error" | "ready">("idle");
  const [message, setMessage] = useState("");

  async function run() {
    setState("loading");
    setMessage("");
    try {
      const list = await api.get("/api/tasks", { params: { page_size: 5 } });
      const first = list.data.items[0];
      if (!first) {
        setState("empty");
        setMessage("Публичных задач нет, сравнивать нечего.");
        return;
      }
      const one = await api.get(`/api/tasks/${first.id}`);
      const restPayload = { list: list.data, one: one.data };
      const gql = await api.post("/graphql", {
        query: "query ($id: Int!) { task(id: $id) { id title description status } tasks { id title } }",
        variables: { id: first.id },
      });
      if (gql.data.errors) throw new Error(gql.data.errors[0].message);
      setReport({
        restRequests: 2,
        restBytes: JSON.stringify(restPayload).length,
        gqlRequests: 1,
        gqlBytes: JSON.stringify(gql.data).length,
        restPreview: JSON.stringify(restPayload, null, 2).slice(0, 500),
        gqlPreview: JSON.stringify(gql.data, null, 2).slice(0, 500),
      });
      setState("ready");
    } catch (error) {
      setState("error");
      setMessage(errorText(error));
    }
  }

  return (
    <section>
      <Seo
        title="REST и GraphQL — TaskBoard"
        description="Одно и то же чтение задачи двумя запросами REST или одним запросом GraphQL."
        path="/compare"
        index={false}
      />
      <h1>REST и GraphQL</h1>
      <p>
        REST забирает список и карточку двумя запросами. GraphQL получает карточку и список одним запросом на /graphql.
      </p>
      <button className="button" type="button" onClick={() => void run()}>
        Сравнить запросы
      </button>
      {state === "loading" ? <p className="status">Считаем запросы…</p> : null}
      {state === "empty" ? <p className="empty">{message}</p> : null}
      {state === "error" ? <p className="error">Внешний или локальный API недоступен. {message}</p> : null}
      {state === "ready" && report ? (
        <div className="compare">
          <article>
            <h2>REST: {report.restRequests} запроса</h2>
            <p>{report.restBytes} символов JSON</p>
            <pre>{report.restPreview}</pre>
          </article>
          <article>
            <h2>GraphQL: {report.gqlRequests} запрос</h2>
            <p>{report.gqlBytes} символов JSON</p>
            <pre>{report.gqlPreview}</pre>
          </article>
        </div>
      ) : null}
    </section>
  );
}
