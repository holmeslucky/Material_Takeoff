import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:7001',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    // Disable sourcemaps for production security
    sourcemap: false,
    // Set base path for assets to work with FastAPI static serving
    assetsDir: 'assets'
  },
  // Set base URL for production deployment
  base: '/',
  define: {
    // Make environment variables available - use import.meta.env for Vite
    __API_BASE_URL__: JSON.stringify('http://localhost:7000')
  }
})