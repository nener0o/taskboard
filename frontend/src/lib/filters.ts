export type Filters = {
  search: string;
  status: string;
  priority: string;
  sort: string;
  order: "asc" | "desc";
  page: number;
};

export const EMPTY_FILTERS: Filters = {
  search: "",
  status: "",
  priority: "",
  sort: "created_at",
  order: "desc",
  page: 1,
};

export function parseFilters(params: URLSearchParams): Filters {
  const page = Number(params.get("page") || "1");
  const order = params.get("order") === "asc" ? "asc" : "desc";
  const sort = params.get("sort") || "created_at";
  return {
    search: params.get("search") || "",
    status: params.get("status") || "",
    priority: params.get("priority") || "",
    sort: ["created_at", "updated_at", "title", "priority", "status"].includes(sort) ? sort : "created_at",
    order,
    page: Number.isFinite(page) && page > 0 ? Math.floor(page) : 1,
  };
}

export function filtersToSearchParams(filters: Filters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.search.trim()) params.set("search", filters.search.trim());
  if (filters.status) params.set("status", filters.status);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.sort !== "created_at") params.set("sort", filters.sort);
  if (filters.order !== "desc") params.set("order", filters.order);
  if (filters.page > 1) params.set("page", String(filters.page));
  return params;
}

export function toRequestParams(filters: Filters, mine = false): Record<string, string | number | boolean> {
  return {
    ...(filters.search.trim() ? { search: filters.search.trim() } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.priority ? { priority: filters.priority } : {}),
    sort: filters.sort,
    order: filters.order,
    page: filters.page,
    page_size: 6,
    ...(mine ? { mine: true } : {}),
  };
}

export function validateCredentials(email: string, password: string): string | null {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) return "Укажите корректный email";
  if (password.length < 8 || password.length > 72) return "Пароль должен быть от 8 до 72 символов";
  if (!/\p{L}/u.test(password) || !/\d/.test(password)) return "Пароль должен содержать букву и цифру";
  return null;
}

export function validateTask(title: string, description: string): string | null {
  if (title.trim().length < 3) return "Название короче 3 символов";
  if (title.trim().length > 200) return "Название длиннее 200 символов";
  if (description.length > 5000) return "Описание длиннее 5000 символов";
  return null;
}
