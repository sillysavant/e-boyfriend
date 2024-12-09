import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/chat": {
        target: "http://localhost:8000", // Your FastAPI backend port
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/chat/, "/chat"),
      },
    },
  },
});
