import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  base: "/isaac/",
  plugins: [react()],
  server: {
    proxy: {
      "/isaac/api/": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/isaac\/api\//, "/api/"),
      },
      "/isaac/uploads/": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/isaac\/uploads\//, "/uploads/"),
      },
    },
    watch: {
      usePolling: true,
      interval: 100,
    },
  },
});
