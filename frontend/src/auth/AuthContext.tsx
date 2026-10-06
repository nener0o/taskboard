import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api, refreshAccess, tokenStore } from "../api/client";
import type { User } from "../api/types";

type AuthValue = {
  user: User | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        if (!tokenStore.getAccess() && tokenStore.getRefresh()) await refreshAccess();
        if (tokenStore.getAccess()) {
          const { data } = await api.get<User>("/api/auth/me");
          if (alive) setUser(data);
        }
      } catch {
        tokenStore.clear();
        if (alive) setUser(null);
      } finally {
        if (alive) setReady(true);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const value = useMemo<AuthValue>(
    () => ({
      user,
      ready,
      async login(email: string, password: string) {
        const { data } = await api.post("/api/auth/login", { email, password });
        tokenStore.set(data.access_token, data.refresh_token);
        const me = await api.get<User>("/api/auth/me");
        setUser(me.data);
      },
      async logout() {
        const refresh = tokenStore.getRefresh();
        try {
          if (refresh) await api.post("/api/auth/logout", { refresh_token: refresh });
        } finally {
          tokenStore.clear();
          setUser(null);
        }
      },
    }),
    [user, ready],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth используется вне AuthProvider");
  return value;
}
