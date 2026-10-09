import { describe, expect, it } from "vitest";

import { filtersToSearchParams, parseFilters, validateCredentials, validateTask } from "./filters";

describe("фильтры в адресе", () => {
  it("читает и записывает параметры", () => {
    const filters = parseFilters(new URLSearchParams("search=доска&status=todo&priority=high&sort=title&order=asc&page=2"));
    expect(filters).toMatchObject({ search: "доска", status: "todo", priority: "high", sort: "title", order: "asc", page: 2 });
    const back = filtersToSearchParams(filters);
    expect(back.get("search")).toBe("доска");
    expect(back.get("page")).toBe("2");
  });

  it("подставляет значения по умолчанию", () => {
    const filters = parseFilters(new URLSearchParams("sort=nope&page=-3"));
    expect(filters.sort).toBe("created_at");
    expect(filters.page).toBe(1);
    expect(filtersToSearchParams(filters).toString()).toBe("");
  });
});

describe("валидация", () => {
  it("отклоняет пустой вход и короткий пароль", () => {
    expect(validateCredentials("", "")).toMatch(/email/);
    expect(validateCredentials("a@b.c", "short")).toMatch(/Пароль/);
    expect(validateCredentials("user@taskboard.local", "User12345")).toBeNull();
  });

  it("проверяет название задачи", () => {
    expect(validateTask("ab", "")).toMatch(/3/);
    expect(validateTask("Нормальное", "")).toBeNull();
  });
});
