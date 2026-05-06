import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 3010,
    proxy: {
      "/api": { target: "http://165.245.132.93:8190", changeOrigin: true },
      "/media": { target: "http://165.245.132.93:8190", changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});