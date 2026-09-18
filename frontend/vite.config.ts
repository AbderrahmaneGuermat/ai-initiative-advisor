import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server proxies /api to the backend, so browser requests stay
// same-origin and there is no CORS configuration for a developer to get wrong.
// 127.0.0.1 rather than localhost, because localhost can resolve to IPv6 on
// Windows while Uvicorn is listening on IPv4.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
