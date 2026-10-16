import { Color } from "three";
import { PALETTE } from "../palette";

// Shared by the sky dome and the ground fog, so the floor dissolves into exactly the sky colour
// at the horizon.
export const skyUniforms = () => ({
  uZenith: { value: new Color(PALETTE.zenith) },
  uHorizon: { value: new Color(PALETTE.horizon) },
  uGlow: { value: new Color(PALETTE.horizonGlow) },
  uDawn: { value: new Color(PALETTE.dawn) },
  uGlowStrength: { value: 1 },
  uDawnStrength: { value: 1 },
});

export const skyColorGlsl = /* glsl */ `
uniform vec3 uZenith;
uniform vec3 uHorizon;
uniform vec3 uGlow;
uniform vec3 uDawn;
uniform float uGlowStrength;
uniform float uDawnStrength;

vec3 skyColor(vec3 d) {
  float elev = d.y;
  float up = smoothstep(0.0, 0.5, max(elev, 0.0));
  vec3 col = mix(uHorizon, uZenith, pow(up, 0.7));
  // Haze band hugging the horizon all around.
  float band = exp(-abs(elev) * 22.0);
  col += uGlow * band * 0.5 * uGlowStrength;
  // A faint dawn low over the horizon ahead (−Z), where the race is heading.
  float ahead = pow(max(0.0, -d.z), 10.0);
  float low = exp(-max(elev, 0.0) * 38.0) * smoothstep(-0.02, 0.0, elev);
  col += uDawn * ahead * low * 0.55 * uDawnStrength;
  return col;
}
`;
