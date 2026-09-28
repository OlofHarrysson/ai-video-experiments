import { bundle } from "@remotion/bundler";
import {
  openBrowser,
  selectComposition,
  renderStill,
} from "@remotion/renderer";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
const out = resolve(
  "../../../deforum/projects/shape-injection/references/assets",
);
await mkdir(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: resolve("src/injection.tsx") });
const browser = await openBrowser("chrome");
try {
  for (const kind of ["circle", "sphere", "ring", "triangle"]) {
    await mkdir(resolve(out, kind), { recursive: true });
    const composition = await selectComposition({
      serveUrl,
      id: `Inject-${kind}`,
      puppeteerInstance: browser,
    });
    for (let frame = 0; frame < 16; frame++)
      await renderStill({
        serveUrl,
        composition,
        frame,
        output: resolve(out, kind, `${frame.toString().padStart(3, "0")}.png`),
        imageFormat: "png",
        puppeteerInstance: browser,
      });
  }
  await writeFile(
    resolve(out, "guide.json"),
    JSON.stringify(
      {
        width: 1024,
        height: 576,
        fps: 4,
        frames: 16,
        positions: Array.from({ length: 16 }, (_, i) => ({
          i,
          x: 280 + (460 * i) / 15,
          y: 205 - 45 * Math.sin((Math.PI * i) / 15),
          radius: 74,
        })),
      },
      null,
      2,
    ),
  );
} finally {
  await browser.close({ silent: true });
}
