// Download the recorded instruments the score plays, from Versilian Studios'
// VSCO 2 Community Edition (CC0), into samples/ (ignored by Git), and record
// each file's SHA-256 in samples/manifest.json.
//   npm run samples
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "samples");
const REPO = "https://raw.githubusercontent.com/sgossner/VSCO-2-CE/master";

// The instruments, their files and the notes they sound: src/audio/samples.json.
const LAYOUT = JSON.parse(
  await readFile(join(ROOT, "src/audio/samples.json"), "utf8"),
);
export const SAMPLES = Object.fromEntries(
  Object.entries(LAYOUT).map(([instrument, { source, notes }]) => [
    instrument,
    notes.split(" ").map((note) => source.replace("{note}", note)),
  ]),
);

const manifest = {
  source: "https://github.com/sgossner/VSCO-2-CE",
  license: "CC0-1.0",
  files: {},
};
for (const [instrument, paths] of Object.entries(SAMPLES)) {
  await mkdir(join(OUT, instrument), { recursive: true });
  for (const path of paths) {
    const file = join(OUT, instrument, path.split("/").pop());
    if (!existsSync(file)) {
      const res = await fetch(
        `${REPO}/${path.split("/").map(encodeURIComponent).join("/")}`,
      );
      if (!res.ok) throw new Error(`${res.status} for ${path}`);
      await writeFile(file, Buffer.from(await res.arrayBuffer()));
    }
    const bytes = await readFile(file);
    manifest.files[`${instrument}/${path.split("/").pop()}`] = {
      source: path,
      bytes: bytes.length,
      sha256: createHash("sha256").update(bytes).digest("hex"),
    };
  }
  console.log(`${instrument}: ${paths.length} files`);
}
await writeFile(
  join(OUT, "manifest.json"),
  JSON.stringify(manifest, null, 2) + "\n",
);
