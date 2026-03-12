import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      'frappe-gantt/dist/frappe-gantt.css': path.resolve(__dirname, 'node_modules/frappe-gantt/dist/frappe-gantt.css'),
    },
  },
  server: {
    host: true,
    port: 5173,
    // No explicit hmr.host — Vite auto-detects from window.location.hostname.
    // Works for both localhost and remote VPS access without any config change.
    proxy: {
      '/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://web:8000',
        ws: true,
      },
      '/admin': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
    },
    watch: {
      usePolling: true,
      interval: 500,
    },
  },
});
