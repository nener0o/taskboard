import { createContext, useContext, useMemo, useState } from "react";

import { initialTasks, type DemoTask } from "./model";

type TodoValue = {
  tasks: DemoTask[];
  add: (title: string) => void;
  toggle: (id: number) => void;
  remove: (id: number) => void;
};

const TodoContext = createContext<TodoValue | null>(null);

export function TodoProvider({ children }: { children: React.ReactNode }) {
  const [tasks, setTasks] = useState<DemoTask[]>(initialTasks);
  const value = useMemo<TodoValue>(
    () => ({
      tasks,
      add(title: string) {
        const text = title.trim();
        if (!text) return;
        setTasks((current) => [...current, { id: Date.now(), title: text, done: false }]);
      },
      toggle(id: number) {
        setTasks((current) => current.map((task) => (task.id === id ? { ...task, done: !task.done } : task)));
      },
      remove(id: number) {
        setTasks((current) => current.filter((task) => task.id !== id));
      },
    }),
    [tasks],
  );
  return <TodoContext.Provider value={value}>{children}</TodoContext.Provider>;
}

export function useTodo(): TodoValue {
  const value = useContext(TodoContext);
  if (!value) throw new Error("useTodo вне провайдера");
  return value;
}
