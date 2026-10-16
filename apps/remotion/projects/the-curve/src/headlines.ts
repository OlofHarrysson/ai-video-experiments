import { PALETTE } from "./palette";

// Fragments of the news cycle. Generic on purpose: no company names, no figures to fact-check.
export const TAG_TEXTS = ["NEW MODEL"];

/** Chart annotations drawn like the time ticks. */
export const MARKERS = ["YOU"];

export type Headline = { text: string; bg: string; fg: string };

const RED = "#e8202a";
const WHITE = "#f4f4f4";
const INK = "#0a0a0f";
const BLUE = "#1f4fff";

export const HEADLINES: Headline[] = [
  { text: "NEW MODEL", bg: RED, fg: WHITE },
  { text: "BILLIONS", bg: PALETTE.gold, fg: INK },
  { text: "NEW DATA CENTER", bg: BLUE, fg: WHITE },
  { text: "BREAKTHROUGH", bg: WHITE, fg: INK },
  { text: "RECORD", bg: RED, fg: WHITE },
  { text: "OUT NOW", bg: WHITE, fg: INK },
  { text: "NEW LAB", bg: INK, fg: WHITE },
  { text: "IS THIS AGI?", bg: WHITE, fg: INK },
  { text: "GIGAWATTS", bg: BLUE, fg: WHITE },
  { text: "EVERYTHING CHANGES", bg: RED, fg: WHITE },
  { text: "UPDATE AVAILABLE", bg: INK, fg: WHITE },
  { text: "BIGGER", bg: WHITE, fg: INK },
  { text: "FASTER", bg: RED, fg: WHITE },
  { text: "ALL IN", bg: PALETTE.gold, fg: INK },
];
