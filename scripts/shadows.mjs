#!/usr/bin/env node
// Generates compound shadows after massimo-v4 (packages/ui/src/shadows.ts) into theme/theme.shadows.css.
// Every cast is a contact layer plus N key layers; every recess is N inset layers. No layer is written by hand.
// Usage: node scripts/shadows.mjs
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const E = {
  ratio: 2, blur: 2, spread: 0.25, lean: 0, contactY: 1 / 16, contactBlur: 1 / 8,
  light: { contact: 0.24, budget: 0.22, decay: 0.72, insetBudget: 0.16, insetDecay: 0.6 },
  dark: { contact: 0.6, budget: 0.44, decay: 0.5, insetBudget: 0.4, insetDecay: 0.5 },
};
const SHADE = { light: "27 28 32", dark: "0 0 0" };

// Tailwind v4 names, Massimo levels.
const CASTS = [
  ["shadow-xs", "chip", 0.25, 3],
  ["shadow-sm", "raised", 0.5, 4],
  ["shadow-md", "popup", 1, 5],
  ["shadow-lg", "overlay", 1.5, 5],
  ["shadow-xl", "modal", 2, 5],
];
const INSETS = [
  ["inset-shadow-xs", "pressed", 0.25, 3],
  ["inset-shadow-sm", "recessed", 0.5, 3],
];

const series = (B, l, n) => Array.from({ length: n }, (_, i) => (B * (1 - l) * l ** i) / (1 - l ** n));
const round = (n, d = 4) => Number(n.toFixed(d));

function castLayers(s, keys) {
  const light = series(E.light.budget, E.light.decay, keys);
  const dark = series(E.dark.budget, E.dark.decay, keys);
  const contact = { role: "contact", inset: false, x: 0, y: E.contactY, blur: E.contactBlur, spread: 0, a: { light: E.light.contact / (1 + s), dark: E.dark.contact / (1 + s) } };
  return [contact, ...Array.from({ length: keys }, (_, i) => {
    const y = 2 * s * E.ratio ** (i + 1 - keys);
    return { role: i === keys - 1 ? "far" : "key", inset: false, x: E.lean * y, y, blur: E.blur * y, spread: -E.spread * y, a: { light: light[i], dark: dark[i] } };
  })];
}

function insetLayers(s, keys) {
  const light = series(E.light.insetBudget, E.light.insetDecay, keys);
  const dark = series(E.dark.insetBudget, E.dark.insetDecay, keys);
  return Array.from({ length: keys }, (_, i) => {
    const y = s * E.ratio ** (i + 1 - keys);
    return { role: i === 0 ? "contact" : "key", inset: true, x: 0, y, blur: E.blur * y, spread: 0, a: { light: light[i], dark: dark[i] } };
  });
}

const len = (k) => (Math.abs(k) < 1e-9 ? "0" : `calc(var(--q) * ${round(k)})`);
const color = (a) => `light-dark(rgb(${SHADE.light} / ${round(a.light, 3)}), rgb(${SHADE.dark} / ${round(a.dark, 3)}))`;
const layerCss = (l) => `${l.inset ? "inset " : ""}${len(l.x)} ${len(l.y)} ${len(l.blur)} ${len(l.spread)} ${color(l.a)}`;
const shadowCss = (layers) => layers.map(layerCss).join(",\n    ");

const levels = [
  ...CASTS.map(([name, massimo, s, keys]) => ({ name, massimo, s, keys, kind: "cast", layers: castLayers(s, keys) })),
  ...INSETS.map(([name, massimo, s, keys]) => ({ name, massimo, s, keys, kind: "inset", layers: insetLayers(s, keys) })),
];

const css = `:root, .scope {
${levels.map((l) => `  --${l.name}:\n    ${shadowCss(l.layers)};`).join("\n")}
}
`;
writeFileSync(join(root, "theme/theme.shadows.css"), css);

const composite = (layers, scheme) => 1 - layers.reduce((p, l) => p * (1 - l.a[scheme]), 1);
const q16 = 0.75 * 16 - 6.75;
const manifest = {
  file: "theme.shadows.css",
  generated: "scripts/shadows.mjs",
  description: "Compound shadows after massimo-v4: every cast is a contact layer plus N key layers, every recess N inset layers, generated from a few constants. Lengths are multiples of --q, declared on :root and .scope, so a scope with a smaller font size casts a smaller shadow.",
  source: "massimo-v4 packages/ui/src/shadows.ts",
  depends: ["theme.geometry.css (--q)"],
  method: {
    contact: "Where the part meets its ground: y = q/16, blur = q/8, no spread, alpha = C / (1 + s), so it fades as the part rises.",
    key: "The key light's penumbra: the far layer drops 2s·q and each nearer one ratio times less; blur = blur × y; spread = −spread × y, tucking the halo under the part; x = lean × y.",
    alpha: "The key layers share a budget B, falling by decay λ per layer: α_k = B(1 − λ)λ^(k−1) / (1 − λ^N), so Σα = B at every level and layer count.",
    inset: "A recess turns the series inward: y = s·q · ratio^(k − N), blur = blur × y, no spread, budget B_in falling by λ_in; the nearest layer is the darkest.",
    level: "s scales lengths, never alpha: a higher part casts a wider halo, not a darker one.",
    schemes: "Both schemes share the lengths; dark has a stronger contact and budget and a faster decay, so its occlusion is denser and its halo shorter. Colours are light-dark() pairs of a near-black (light) and black (dark).",
  },
  constants: { ...E, shade: SHADE },
  naming: "Tailwind v4 names (shadow-xs … shadow-xl, inset-shadow-xs, inset-shadow-sm) for Massimo's levels (chip, raised, popup, overlay, modal; pressed, recessed).",
  notDone: ["Massimo's tinted far layer (its shadow-tint property): it needs relative colour syntax and a per-part redeclaration of the tokens."],
  levels: levels.map((l) => ({
    token: `--${l.name}`,
    massimo: l.massimo,
    kind: l.kind,
    s: l.s,
    layers: l.layers.length,
    compositeAlpha: { light: round(composite(l.layers, "light"), 3), dark: round(composite(l.layers, "dark"), 3) },
    at16: l.layers.map((x) => ({ role: x.role, y: round(x.y * q16, 2), blur: round(x.blur * q16, 2), spread: round(x.spread * q16, 2), alpha: { light: round(x.a.light, 3), dark: round(x.a.dark, 3) } })),
  })),
};
writeFileSync(join(root, "theme/theme.shadows.manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log(levels.map((l) => `--${l.name} (${l.massimo}): ${l.layers.length} layers`).join("\n"));
