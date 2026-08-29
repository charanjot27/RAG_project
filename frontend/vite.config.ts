import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, calls to /api are proxied to the FastAPI backend on :8000 (no CORS
// headaches). In production, set VITE_API_URL to your deployed API URL instead.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
