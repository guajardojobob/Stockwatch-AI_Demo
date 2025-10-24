import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/recommend': 'http://localhost:8000',
      '/ingest': 'http://localhost:8000',
      '/healthz': 'http://localhost:8000'
    }
  },
  build: {
    outDir: '../backend/static',
    emptyOutDir: true
  }
})
