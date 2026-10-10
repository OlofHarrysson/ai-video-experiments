import { readdir, rm } from 'node:fs/promises';
import path from 'node:path';

// Only the exact capture stem and its numbered parts belong to this capture.
export async function clearCaptureFiles(file) {
  const directory = path.dirname(file);
  const name = path.basename(file);
  const stem = name.replace(/\.png$/i, '');
  let names;
  try { names = await readdir(directory); }
  catch (error) { if (error.code === 'ENOENT') return; throw error; }
  for (const candidate of names) {
    const suffix = candidate.startsWith(`${stem}--part-`) ? candidate.slice(stem.length + 7) : '';
    if (candidate === name || /^\d{2,}\.png$/.test(suffix)) await rm(path.join(directory, candidate), { force: true });
  }
}
