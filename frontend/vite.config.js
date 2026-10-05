import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite configuration: enables the React plugin (JSX + Fast Refresh)
// and runs the dev server on port 5173 by default.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
