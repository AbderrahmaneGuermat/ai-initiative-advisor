import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server proxies /api to the backend, so browser requests stay
// same-origin and there is no CORS configuration for a developer to get wrong.
//
// The proxy target is written as 127.0.0.1 rather than localhost because the
// backend listens on IPv4. On the Windows 11 machine used to develop this,
// localhost resolved to the IPv6 loopback, which would not have reached it.
// That was observed on one machine, not verified as general behaviour.
//
// Port 5173 and the target address are fixed for this MVP. See
// docs/decisions.md, D-015.
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
