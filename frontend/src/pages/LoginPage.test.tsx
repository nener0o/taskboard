import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelmetProvider } from "react-helmet-async";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../auth/AuthContext";
import { LoginPage } from "./LoginPage";

vi.mock("../api/client", () => ({
  api: {
    get: vi.fn().mockRejectedValue(new Error("нет сессии")),
    post: vi.fn(),
  },
  tokenStore: {
    getAccess: () => null,
    getRefresh: () => null,
    set: vi.fn(),
    clear: vi.fn(),
  },
  refreshAccess: vi.fn(),
  errorText: () => "ошибка сервера",
}));

describe("форма входа", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("показывает ошибку и не отправляет пустую форму", async () => {
    render(
      <HelmetProvider>
        <MemoryRouter>
          <AuthProvider>
            <LoginPage />
          </AuthProvider>
        </MemoryRouter>
      </HelmetProvider>,
    );
    await userEvent.click(screen.getByRole("button", { name: "Войти" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/email/i);
  });
});
