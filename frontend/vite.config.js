import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react()
  ],
  // base: './',
  resolve: {
    alias: [
      { find: '~', replacement: '/src' },
    ]
  },
  server: {
    proxy: {
      // Proxy AI API to avoid CORS in development
      '/ai': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/ai/, ''),
      },
    },
  }
})
