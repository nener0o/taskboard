import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/graphql": "http://127.0.0.1:8000",
      "/robots.txt": "http://127.0.0.1:8000",
      "/sitemap.xml": "http://127.0.0.1:8000",
      "/pages": "http://127.0.0.1:8000",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
  },
});
