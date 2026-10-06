import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import type { Tokens } from "./types";

const ACCESS = "taskboard_access";
const REFRESH = "taskboard_refresh";

export const tokenStore = {
  getAccess: () => sessionStorage.getItem(ACCESS),
  getRefresh: () => localStorage.getItem(REFRESH),
  set(access: string, refresh: string) {
    sessionStorage.setItem(ACCESS, access);
    localStorage.setItem(REFRESH, refresh);
  },
  clear() {
    sessionStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
  },
};

export const api = axios.create();

api.interceptors.request.use((config) => {
  const token = tokenStore.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshing: Promise<string | null> | null = null;

export async function refreshAccess(): Promise<string | null> {
  const refresh = tokenStore.getRefresh();
  if (!refresh) return null;
  const { data } = await axios.post<Tokens>("/api/auth/refresh", { refresh_token: refresh });
  tokenStore.set(data.access_token, data.refresh_token);
  return data.access_token;
}

export function isRefreshFailure(status: number | undefined, url: string): boolean {
  return status === 401 && url.includes("/api/auth/refresh");
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const url = original?.url ?? "";
    if (!original || error.response?.status !== 401 || original._retry || url.includes("/api/auth/")) {
      if (isRefreshFailure(error.response?.status, url)) tokenStore.clear();
      return Promise.reject(error);
    }
    original._retry = true;
    try {
      refreshing ??= refreshAccess().finally(() => {
        refreshing = null;
      });
      const access = await refreshing;
      if (!access) throw error;
      original.headers.Authorization = `Bearer ${access}`;
      return api(original);
    } catch (refreshError) {
      tokenStore.clear();
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        window.location.assign("/login");
      }
      return Promise.reject(refreshError);
    }
  },
);

export function errorText(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((item: { msg?: string }) => item.msg || "Ошибка поля").join(", ");
    }
    if (error.response?.status === 401) return "Сессия недействительна. Войдите снова.";
  }
  return "Не удалось выполнить запрос";
}
