import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/templates': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/simulations': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/scenarios': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  }
})
