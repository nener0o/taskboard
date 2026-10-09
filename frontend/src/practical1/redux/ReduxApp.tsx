import { useState } from "react";
import { Provider, useDispatch, useSelector } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";

import { Seo } from "../../components/Seo";
import todoReducer, { added, removed, toggled } from "./todoSlice";
import type { DemoTask } from "./model";

const store = configureStore({ reducer: { todos: todoReducer } });
type RootState = ReturnType<typeof store.getState>;
type AppDispatch = typeof store.dispatch;

function Board() {
  const tasks = useSelector((state: RootState) => state.todos.tasks);
  const dispatch = useDispatch<AppDispatch>();
  const [title, setTitle] = useState("");
  const open = tasks.filter((task: DemoTask) => !task.done).length;
  return (
    <section>
      <Seo title="Redux Toolkit — TaskBoard" description="Мини-доска на Redux Toolkit" path="/demo/redux" index={false} />
      <h1>Мини-доска на Redux Toolkit</h1>
      <p className="meta">Открытых задач: {open}</p>
      <form
        className="inline"
        onSubmit={(event) => {
          event.preventDefault();
          dispatch(added(title));
          setTitle("");
        }}
      >
        <input aria-label="Новая задача" value={title} onChange={(event) => setTitle(event.target.value)} />
        <button className="button" type="submit">Добавить</button>
      </form>
      <ul className="plain">
        {tasks.map((task: DemoTask) => (
          <li key={task.id}>
            <label>
              <input type="checkbox" checked={task.done} onChange={() => dispatch(toggled(task.id))} />
              <span className={task.done ? "done" : ""}>{task.title}</span>
            </label>
            <button type="button" className="ghost" onClick={() => dispatch(removed(task.id))}>Удалить</button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function ReduxApp() {
  return (
    <Provider store={store}>
      <Board />
    </Provider>
  );
}
