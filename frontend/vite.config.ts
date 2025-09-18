import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  server: {
    host: "0.0.0.0", // allow access from outside the container
    port: 5173,
    strictPort: true,
    hmr: {
      host: "localhost", // or your machine IP if accessing from another device
    },
  },
  plugins: [react(), tailwindcss()],
});
