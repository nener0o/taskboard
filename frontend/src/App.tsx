import { Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { ForbiddenPage, NotFoundPage } from "./pages/StatusPages";

export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  );
}
