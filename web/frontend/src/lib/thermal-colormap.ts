import * as THREE from "three";

/**
 * Same 7-stop ramp as the --thermal-1..7 CSS tokens (globals.css), so the
 * marketing 3D visual, the legend, and chart colors all agree. `t` is 0
 * (coldest) to 1 (hottest).
 */
const STOPS: { h: number; s: number; l: number }[] = [
  { h: 217, s: 0.91, l: 0.5 },
  { h: 189, s: 0.85, l: 0.48 },
  { h: 158, s: 0.64, l: 0.42 },
  { h: 84, s: 0.6, l: 0.45 },
  { h: 45, s: 0.93, l: 0.47 },
  { h: 25, s: 0.9, l: 0.5 },
  { h: 0, s: 0.72, l: 0.51 },
];

export function thermalColorAt(t: number): THREE.Color {
  const clamped = THREE.MathUtils.clamp(t, 0, 1);
  const scaled = clamped * (STOPS.length - 1);
  const i = Math.min(Math.floor(scaled), STOPS.length - 2);
  const localT = scaled - i;
  const a = STOPS[i];
  const b = STOPS[i + 1];
  const h = THREE.MathUtils.lerp(a.h, b.h, localT) / 360;
  const s = THREE.MathUtils.lerp(a.s, b.s, localT);
  const l = THREE.MathUtils.lerp(a.l, b.l, localT);
  return new THREE.Color().setHSL(h, s, l);
}

export function thermalCssGradient(): string {
  return `linear-gradient(to top, ${STOPS.map((s) => `hsl(${s.h} ${s.s * 100}% ${s.l * 100}%)`).join(", ")})`;
}
