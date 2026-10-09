import { defineConfig } from 'vite';
import { speechPlugin } from './src/speech-server.js';
export default defineConfig({
  plugins: [speechPlugin()],
  build: { rolldownOptions: { input: { review: "index.html", motion: "motion.html", studio: "studio.html", motionSource: "motion-source.html" } } },
  server: { host: '127.0.0.1', port: Number(process.env.PORT || 3000), strictPort: true },
});
