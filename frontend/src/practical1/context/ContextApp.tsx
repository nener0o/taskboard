import { useState } from "react";

import { Seo } from "../../components/Seo";
import { TodoProvider, useTodo } from "./TodoContext";

function Board() {
  const { tasks, add, toggle, remove } = useTodo();
  const [title, setTitle] = useState("");
  const open = tasks.filter((task) => !task.done).length;
  return (
    <section>
      <Seo title="Context API — TaskBoard" description="Мини-доска на React Context" path="/demo/context" index={false} />
      <h1>Мини-доска на Context API</h1>
      <p className="meta">Открытых задач: {open}</p>
      <form
        className="inline"
        onSubmit={(event) => {
          event.preventDefault();
          add(title);
          setTitle("");
        }}
      >
        <input aria-label="Новая задача" value={title} onChange={(event) => setTitle(event.target.value)} />
        <button className="button" type="submit">Добавить</button>
      </form>
      <ul className="plain">
        {tasks.map((task) => (
          <li key={task.id}>
            <label>
              <input type="checkbox" checked={task.done} onChange={() => toggle(task.id)} />
              <span className={task.done ? "done" : ""}>{task.title}</span>
            </label>
            <button type="button" className="ghost" onClick={() => remove(task.id)}>Удалить</button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function ContextApp() {
  return (
    <TodoProvider>
      <Board />
    </TodoProvider>
  );
}
