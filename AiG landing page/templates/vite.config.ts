import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Django serves the build under /static/; Vercel serves from site root (VERCEL=1 at build time).
const isVercel = Boolean(process.env.VERCEL)

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: isVercel ? '/' : '/static/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        // use stable filenames (no hashing) so Django templates can reference them
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name][extname]'
      }
    }
  },
})
