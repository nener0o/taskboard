import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { RequireAuth } from "./auth/guards";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ForbiddenPage, NotFoundPage } from "./pages/StatusPages";

const AdminPage = lazy(() => import("./pages/AdminPage").then((module) => ({ default: module.AdminPage })));

export function App() {
  return (
    <Layout>
      <Suspense fallback={<p className="status">Загружаем раздел…</p>}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />
          <Route path="/admin" element={<RequireAuth roles={["manager", "admin"]}><AdminPage /></RequireAuth>} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}
