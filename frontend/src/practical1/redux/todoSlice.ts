import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import { initialTasks, type DemoTask } from "./model";

const todoSlice = createSlice({
  name: "todos",
  initialState: { tasks: initialTasks as DemoTask[] },
  reducers: {
    added(state, action: PayloadAction<string>) {
      const title = action.payload.trim();
      if (!title) return;
      state.tasks.push({ id: Date.now(), title, done: false });
    },
    toggled(state, action: PayloadAction<number>) {
      const task = state.tasks.find((item) => item.id === action.payload);
      if (task) task.done = !task.done;
    },
    removed(state, action: PayloadAction<number>) {
      state.tasks = state.tasks.filter((item) => item.id !== action.payload);
    },
  },
});

export const { added, toggled, removed } = todoSlice.actions;
export default todoSlice.reducer;
