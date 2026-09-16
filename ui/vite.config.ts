import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // fastcae's dev server holds 5183 on this machine; fastcad takes the next one.
    port: 5184,
    strictPort: true,
    // The API is a separate process. Proxying rather than calling it cross-origin keeps the
    // browser on one origin, which matters for the binary mesh fetch.
    proxy: { "/api": { target: "http://127.0.0.1:8022", changeOrigin: true } },
  },
});
