const GEIST = '/node_modules/geist/dist/fonts';

const FACES: [family: string, url: string, weight?: string][] = [
  ['MangoGrotesque', '/assets/fonts/MangoGrotesque-ExtBdIta.woff2'],
  ['GeistDisplay', `${GEIST}/geist-sans/Geist-ExtraBoldItalic.woff2`],
  ['Geist', `${GEIST}/geist-sans/Geist-Medium.woff2`, '500'],
  ['Geist Mono', `${GEIST}/geist-mono/GeistMono-Regular.woff2`, '400'],
  ['Geist Mono', `${GEIST}/geist-mono/GeistMono-Medium.woff2`, '500'],
  ['Geist Mono', `${GEIST}/geist-mono/GeistMono-Bold.woff2`, '700'],
  ['DSEG7', '/node_modules/dseg/fonts/DSEG7-Classic/DSEG7Classic-BoldItalic.woff2'],
];

export async function loadFonts() {
  const faces = FACES.map(([family, url, weight]) => new FontFace(family, `url(${url})`, weight ? { weight } : {}));
  await Promise.all(faces.map((face) => face.load()));
  for (const face of faces) document.fonts.add(face);
}

/** Canvas font strings. The display faces are already the brand's extra-bold italic cuts. */
export const font = {
  display: (px: number) => `${px}px "MangoGrotesque"`,
  displaySm: (px: number) => `${px}px "GeistDisplay"`,
  sans: (px: number) => `500 ${px}px "Geist"`,
  mono: (px: number, weight: 400 | 500 | 700 = 500) => `${weight} ${px}px "Geist Mono"`,
  seg: (px: number) => `${px}px "DSEG7"`,
};
