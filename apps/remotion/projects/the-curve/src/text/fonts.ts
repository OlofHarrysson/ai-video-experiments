import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

// Mono for the chart's own marks (ticks, launch tags), a condensed news face for headlines,
// and a quiet grotesk for the closing line.
export const mono = loadMono("normal", { weights: ["500", "700"], subsets: ["latin"] });
export const anton = loadAnton("normal", { weights: ["400"], subsets: ["latin"] });
export const inter = loadInter("normal", { weights: ["300", "500"], subsets: ["latin"] });

export const fontsReady = () =>
  Promise.all([mono.waitUntilDone(), anton.waitUntilDone(), inter.waitUntilDone()]).then(() => undefined);
