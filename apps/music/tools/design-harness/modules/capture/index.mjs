import { clearCaptureFiles } from '../core/capture-files.mjs';

const DEFAULT_HEIGHT = 1000;
const DEFAULT_OVERLAP = 200;

function partOptions(value) {
  if (value === undefined || value === false) return null;
  if (value !== true && (!value || typeof value !== 'object' || Array.isArray(value))) throw new Error('Capture parts must be true, false, or an options object');
  const { height = DEFAULT_HEIGHT, overlap = DEFAULT_OVERLAP, overview = false, ...extra } = value === true ? {} : value;
  if (Object.keys(extra).length || !Number.isInteger(height) || height <= 0 || !Number.isInteger(overlap) || overlap < 0 || overlap >= height || typeof overview !== 'boolean') {
    throw new Error('Capture parts require integer height > 0, integer overlap >= 0 and < height, and boolean overview');
  }
  return { height, overlap, overview };
}

export async function capturePage(page, file, selector, { parts } = {}) {
  await clearCaptureFiles(file);
  const settings = partOptions(parts);
  const options = { path: file, animations: 'disabled', caret: 'hide', scale: 'css' };
  if (settings) return captureParts(page, file, selector, options, settings);
  if (!selector) {
    await page.screenshot({ ...options, fullPage: true });
    return { png: file, region: null, missing: [] };
  }
  const region = typeof selector === 'string' ? page.locator(selector) : selector;
  const count = await region.count();
  if (count !== 1 || !await region.isVisible()) {
    return { png: null, region: null, missing: [`Capture selector ${selector}: expected one visible element, found ${count}`] };
  }
  await region.screenshot(options);
  return { png: file, region: await region.boundingBox(), missing: [] };
}

async function captureParts(page, file, selector, options, settings) {
  if (!/\.png$/i.test(file)) throw new Error('Capture parts require a .png output path');
  const locator = selector ? (typeof selector === 'string' ? page.locator(selector) : selector) : null;
  if (locator && (await locator.count() !== 1 || !await locator.isVisible())) {
    return { png: null, region: null, parts: [], missing: [`Capture selector ${selector}: expected one visible element`] };
  }
  const document = await page.evaluate(() => ({
    width: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth ?? 0, innerWidth),
    height: Math.max(document.documentElement.scrollHeight, document.body?.scrollHeight ?? 0, innerHeight),
    x: scrollX, y: scrollY,
  }));
  const region = locator ? await locator.boundingBox() : null;
  if (locator && !region) return { png: null, region: null, parts: [], missing: ['Capture region has no bounding box'] };
  const left = Math.max(0, Math.floor(region ? region.x + document.x : 0));
  const top = Math.max(0, Math.floor(region ? region.y + document.y : 0));
  const right = Math.min(document.width, Math.ceil(region ? region.x + document.x + region.width : document.width));
  const bottom = Math.min(document.height, Math.ceil(region ? region.y + document.y + region.height : document.height));
  if (right <= left || bottom <= top) return { png: null, region, parts: [], missing: ['Capture region is outside the document'] };
  const bounds = { x: left, y: top, width: right - left, height: bottom - top };
  const result = { png: null, region, parts: [], missing: [], captureParts: { ...settings, bounds, coordinates: 'document CSS pixels' } };
  try {
    if (settings.overview) {
      await page.screenshot({ ...options, fullPage: true, clip: bounds });
      result.png = file;
    }
    for (let y = top; y < bottom; y += settings.height - settings.overlap) {
      const clip = { x: left, y, width: bounds.width, height: Math.min(settings.height, bottom - y) };
      const part = result.parts.length + 1;
      const png = file.replace(/\.png$/i, `--part-${String(part).padStart(2, '0')}.png`);
      await page.screenshot({ ...options, path: png, fullPage: true, clip });
      result.parts.push({ part, png, ...clip });
      if (y + clip.height === bottom) break;
    }
    return result;
  } catch (error) {
    await clearCaptureFiles(file);
    throw error;
  }
}
