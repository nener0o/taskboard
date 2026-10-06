import { Navigate, useLocation } from "react-router-dom";

import type { Role } from "../api/types";
import { useAuth } from "./AuthContext";

export function RequireAuth({ roles, children }: { roles?: Role[]; children: React.ReactNode }) {
  const { user, ready } = useAuth();
  const location = useLocation();
  if (!ready) return <p className="status">Проверяем сессию…</p>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/forbidden" replace />;
  return children;
}
