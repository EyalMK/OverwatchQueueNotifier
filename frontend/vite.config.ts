import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "./",
  plugins: [react()],
  optimizeDeps: {
    exclude: ["electron", "electron-is-dev"],
  },
  server: {
    port: 5174,
    strictPort: true,
  },
  build: {
    sourcemap: true,
  },
});
