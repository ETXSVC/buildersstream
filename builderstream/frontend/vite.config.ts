import { defineConfig, Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

function buildTimePlugin(): Plugin {
  const buildTime = new Date().toISOString();
  return {
    name: 'build-time',
    transformIndexHtml: (html) => html.replace('__VITE_BUILD_TIMESTAMP__', buildTime),
  };
}

export default defineConfig({
  plugins: [react(), buildTimePlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      'frappe-gantt/dist/frappe-gantt.css': path.resolve(__dirname, 'node_modules/frappe-gantt/dist/frappe-gantt.css'),
    },
  },
  preview: {
    host: true,
    port: 4173,
    proxy: {
      '/api':   { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ws':    { target: 'ws://127.0.0.1:8000', ws: true },
      '/admin': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  server: {
    host: true,
    port: 5173,
    hmr: {
      clientPort: 5173,
    },
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
      '/media': {
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
