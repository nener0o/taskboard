import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import type { User } from "../api/types";
import { AuthContext } from "./AuthContext";
import { RequireAuth } from "./guards";

function renderAt(user: User | null, roles?: User["role"][]) {
  return render(
    <MemoryRouter initialEntries={["/secret"]}>
      <AuthContext.Provider value={{ user, ready: true, login: vi.fn(), logout: vi.fn() }}>
        <Routes>
          <Route path="/secret" element={<RequireAuth roles={roles}><p>секрет</p></RequireAuth>} />
          <Route path="/login" element={<p>страница входа</p>} />
          <Route path="/forbidden" element={<p>страница запрета</p>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>,
  );
}

const sample = (role: User["role"]): User => ({
  id: 1,
  name: "Тест",
  email: "t@example.com",
  role,
  is_active: true,
  permissions: [],
});

describe("защита маршрутов", () => {
  it("отправляет гостя на вход", () => {
    renderAt(null);
    expect(screen.getByText("страница входа")).toBeInTheDocument();
  });

  it("закрывает админский маршрут пользователю", () => {
    renderAt(sample("user"), ["admin"]);
    expect(screen.getByText("страница запрета")).toBeInTheDocument();
  });

  it("пускает администратора", () => {
    renderAt(sample("admin"), ["admin"]);
    expect(screen.getByText("секрет")).toBeInTheDocument();
  });
});
