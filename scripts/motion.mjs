#!/usr/bin/env node
// Generates motion tokens after massimo-v4 (packages/ui/src/motion.ts) into theme/theme.motion.css: Apple's spring
// presets sampled into CSS linear() easings, their durations, and the ease curves for color and opacity.
// Usage: node scripts/motion.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const SPRINGS = {
  smooth: { response: 0.5, bounce: 0, use: "No overshoot: the default for anything that moves (a sliding thumb, a sheet)." },
  snappy: { response: 0.4, bounce: 0.15, use: "A small overshoot: quick, direct feedback (a toggle, a pressed key's return)." },
  bouncy: { response: 0.5, bounce: 0.3, use: "A visible overshoot: playful moments only." },
};
const CURVES = {
  standard: { value: "cubic-bezier(0.25, 0.1, 0.25, 1)", use: "Apple's standard ease, for color and opacity." },
  out: { value: "cubic-bezier(0.16, 1, 0.3, 1)", use: "Ease-out, for what enters." },
  in: { value: "cubic-bezier(0.5, 0, 0.75, 0)", use: "Ease-in, for what leaves." },
};
const SPEED = 0.8;
const FADE = "160ms";
const POINTS = 40;

// Position (0 → 1) of a unit spring at time t, SwiftUI's parameterisation: ω = 2π / response, ζ = 1 − bounce.
const at = ({ response, bounce }, t) => {
  const w = (2 * Math.PI) / response;
  const z = 1 - bounce;
  if (z >= 1) return 1 - (1 + w * t) * Math.exp(-w * t);
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
};
// The time the spring takes to stay within 0.1% of its target.
const settle = (s) => {
  let last = 0;
  for (let t = 0; t < 5; t += 0.005) if (Math.abs(1 - at(s, t)) > 0.001) last = t;
  return Math.ceil(last * 100) / 100;
};
const round = (n) => Math.round(n * 10000) / 10000;
const linear = (s) => {
  const d = settle(s);
  const stops = Array.from({ length: POINTS + 1 }, (_, i) => round(at(s, (d * i) / POINTS)));
  stops[POINTS] = 1;
  return `linear(${stops.join(", ")})`;
};

const springs = Object.entries(SPRINGS).map(([name, s]) => ({
  name, ...s, settle: settle(s), duration: `${Math.round(settle(s) * 1000 * SPEED)}ms`, easing: linear(s),
}));

const css = `:root {
${springs.map((s) => `  --ease-${s.name}: ${s.easing};`).join("\n")}
${Object.entries(CURVES).map(([n, c]) => `  --ease-${n}: ${c.value};`).join("\n")}

${springs.map((s) => `  --duration-${s.name}: ${s.duration};`).join("\n")}
  --duration-fade: ${FADE};

  --motion-duration: var(--duration-fade);
  --motion-easing: var(--ease-standard);
}
`;
writeFileSync(join(root, "theme/theme.motion.css"), css);

const manifest = {
  file: "theme.motion.css",
  generated: "scripts/motion.mjs",
  description: "Motion after massimo-v4: Apple's spring presets sampled into CSS linear() easings over the time each takes to settle, so the curve is the spring itself, plus ease curves for color and opacity. --motion-duration and --motion-easing are Affine's single state-change pair, pointed at the fade.",
  source: "massimo-v4 packages/ui/src/motion.ts; affine-ui tokens/motion",
  method: {
    spring: "x(t) = 1 − e^(−ζωt)(cos ω_d t + (ζω/ω_d) sin ω_d t), ω = 2π / response, ζ = 1 − bounce (critically damped when bounce is 0). Sampled at 41 points from 0 to the settling time.",
    settle: "The time the spring stays within 0.1% of its target.",
    duration: `Each spring runs in ${SPEED * 100}% of its settling time (Massimo: buttons and menus felt slow at 100%).`,
    fade: `Color and opacity have no distance to travel: they take ${FADE} on the standard ease.`,
  },
  springs: springs.map((s) => ({ easing: `--ease-${s.name}`, duration: `--duration-${s.name}`, response: s.response, bounce: s.bounce, settle: `${s.settle}s`, value: s.duration, use: s.use })),
  curves: Object.entries(CURVES).map(([n, c]) => ({ token: `--ease-${n}`, value: c.value, use: c.use })),
  state: [
    { token: "--duration-fade", value: FADE, use: "Color and opacity changes." },
    { token: "--motion-duration", value: "var(--duration-fade)", use: "Affine's one state-change length; what the transition classes use by default." },
    { token: "--motion-easing", value: "var(--ease-standard)", use: "Affine's one state-change easing." },
  ],
  reducedMotion: "The reset cuts every animation and transition to 0.01ms under prefers-reduced-motion: reduce.",
};
writeFileSync(join(root, "theme/theme.motion.manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log(springs.map((s) => `--ease-${s.name}: settles in ${s.settle}s, runs ${s.duration}`).join("\n"));
