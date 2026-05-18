import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

process.env.GOMAXPROCS = process.env.GOMAXPROCS || "1";

export default defineConfig({
  base: "/ui/",
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8088",
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
