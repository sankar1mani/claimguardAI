import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,  // Required for Docker
    watch: {
      usePolling: true  // Required for Docker file watching
    },
    hmr: {
      clientPort: 5173  // Ensure HMR works through Docker port mapping
    }
  }
})
