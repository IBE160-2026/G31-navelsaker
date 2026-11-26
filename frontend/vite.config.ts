import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// AD-11: /api sendes videre til backend, så nettleseren ser ett opphav og det trengs ingen CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
