import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { RequireAuth } from "./auth/guards";
import { Layout } from "./components/Layout";
import { BoardPage } from "./pages/BoardPage";
import { CatalogPage } from "./pages/CatalogPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ForbiddenPage, NotFoundPage } from "./pages/StatusPages";
import { TaskFormPage } from "./pages/TaskFormPage";
import { TaskPage } from "./pages/TaskPage";

const AdminPage = lazy(() => import("./pages/AdminPage").then((module) => ({ default: module.AdminPage })));

export function App() {
  return (
    <Layout>
      <Suspense fallback={<p className="status">Загружаем раздел…</p>}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/tasks" element={<CatalogPage />} />
          <Route path="/tasks/:id" element={<TaskPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />
          <Route path="/app" element={<RequireAuth><BoardPage /></RequireAuth>} />
          <Route path="/app/tasks/new" element={<RequireAuth><TaskFormPage /></RequireAuth>} />
          <Route path="/app/tasks/:id" element={<RequireAuth><TaskFormPage /></RequireAuth>} />
          <Route path="/admin" element={<RequireAuth roles={["manager", "admin"]}><AdminPage /></RequireAuth>} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}
