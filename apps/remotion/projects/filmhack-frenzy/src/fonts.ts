import { loadFont } from '@remotion/fonts';
import { staticFile } from 'remotion';

// Downloaded by `npm run assets`; the display face is filmhack.ai's own extra-bold italic cut.
await Promise.all([
  loadFont({ family: 'MangoGrotesque', url: staticFile('fonts/MangoGrotesque-ExtBdIta.woff2') }),
  loadFont({ family: 'Geist Mono', url: staticFile('fonts/GeistMono-Medium.woff2'), weight: '500' }),
  loadFont({ family: 'Geist Mono', url: staticFile('fonts/GeistMono-Bold.woff2'), weight: '700' }),
  loadFont({ family: 'DSEG7', url: staticFile('fonts/DSEG7Classic-BoldItalic.woff2') }),
]);
