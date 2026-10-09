export type DemoTask = {
  id: number;
  title: string;
  done: boolean;
};

export const initialTasks: DemoTask[] = [
  { id: 1, title: "Прочитать методичку", done: true },
  { id: 2, title: "Собрать доску", done: false },
];
