import type { Page, Locator } from 'playwright';
export function writeEvidence(page: Page, options: {
  basePath: string;
  observation?: object & { missing: string[] };
  identity: { target: string; state: string; viewport: string };
  sourceRoot?: string;
  details?: unknown;
  issues?: { type: string; message: string }[];
  screenshot?: boolean;
  crop?: string | Locator;
  parts?: boolean | { height?: number; overlap?: number; overview?: boolean };
}): Promise<{ status: string; png: string | null; parts?: CapturePart[]; artifacts: { png: string | null; parts?: CapturePart[] }; missing: string[]; errors: string[] }>;

export type CapturePart = { part: number; png: string; x: number; y: number; width: number; height: number };
