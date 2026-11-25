#!/usr/bin/env node
// Generates the material paint tokens after massimo-v4 (packages/ui/src/materials.ts) into theme/theme.materials.css:
// shade and lit at an alpha (the paint roles), and the glass faces. The relief classes that use them are written by
// scripts/utilities.mjs.
// Usage: node scripts/materials.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const SHADE = { light: "27 28 32", dark: "0 0 0" };
const LIT = "255 255 255";
// Paint roles: the dark scheme takes black at 3x the shade alpha and white at 1/4 the lit alpha, unless a role names its own.
const ROLES = {
  "face-top": { base: "lit", alpha: 0.4, dark: 0.03 },
  "face-bottom": { base: "shade", alpha: 0.015, dark: 0.055 },
  "face-top-solid": { base: "lit", alpha: 0.065, dark: 0.07 },
  "face-bottom-solid": { base: "shade", alpha: 0.03, dark: 0.015 },
  "bevel-top": { base: "lit", alpha: 0.5 },
  "bevel-top-solid": { base: "lit", alpha: 0.22 },
  "bevel-bottom": { base: "shade", alpha: 0.05 },
  "bevel-ring": { base: "shade", alpha: 0.06 },
  "recess-ring": { base: "shade", alpha: 0.05 },
  "recess-lip": { base: "lit", alpha: 0.45 },
  "etch-top": { base: "shade", alpha: 0.08, dark: 0.3 },
  "etch-ledge": { base: "lit", alpha: 1, dark: 0.14 },
  "rim-frosted-top": { base: "lit", alpha: 0.8, dark: 0.3 },
  "rim-frosted-bottom": { base: "lit", alpha: 0.35, dark: 0.08 },
  "rim-frosted-ring": { base: "lit", alpha: 0.4, dark: 0.13 },
  "rim-frosted-glow": { base: "lit", alpha: 0.3, dark: 0.07 },
  "rim-frosted-outer": { base: "shade", alpha: 0.08, dark: 0.4 },
  "specular-frosted": { base: "lit", alpha: 0.3, dark: 0.06 },
  "rim-clear-top": { base: "lit", alpha: 0.95, dark: 0.38 },
  "rim-clear-bottom": { base: "lit", alpha: 0.45, dark: 0.12 },
  "rim-clear-ring": { base: "lit", alpha: 0.5, dark: 0.14 },
  "rim-clear-glow": { base: "lit", alpha: 0.4, dark: 0.08 },
  "rim-clear-outer": { base: "shade", alpha: 0.1, dark: 0.45 },
  "specular-clear": { base: "lit", alpha: 0.4, dark: 0.1 },
};
// How much of its fill a glass face lays over what is behind it (Massimo: frosted 56%, clear 18%).
const GLASS_FACE = { frosted: 0.56, clear: 0.18 };

const r3 = (n) => Math.round(Math.min(1, n) * 1000) / 1000;
const paint = (role) => {
  const light = role.base === "shade" ? `rgb(${SHADE.light} / ${r3(role.alpha)})` : `rgb(${LIT} / ${r3(role.alpha)})`;
  const dark = role.base === "shade" ? `rgb(${SHADE.dark} / ${r3(role.dark ?? role.alpha * 3)})` : `rgb(${LIT} / ${r3(role.dark ?? role.alpha / 4)})`;
  return `light-dark(${light}, ${dark})`;
};

// The glass face is the neutral fill at an alpha: step 1 in light (the page), step 3 in dark (one layer lighter than
// the page, as Massimo's glass sits lighter than its host). Read from the palette, since no color-mix() is allowed.
const neutralCss = readFileSync(join(root, "theme/colors-semantic/neutral.css"), "utf8");
const family = neutralCss.match(/colors-raw\/([\w-]+)\.css/)[1];
const raw = readFileSync(join(root, `theme/colors-raw/${family}.css`), "utf8");
const step = (n, scheme) => raw.match(new RegExp(`--colors-${family}-${n}-${scheme}:\\s*oklch\\(([^)]+)\\)`))[1].trim();
const face = (alpha) => `light-dark(oklch(${step(1, "light")} / ${alpha}), oklch(${step(3, "dark")} / ${alpha}))`;

const css = `:root {
${Object.entries(ROLES).map(([n, role]) => `  --paint-${n}: ${paint(role)};`).join("\n")}

  --glass-face-frosted: ${face(GLASS_FACE.frosted)};
  --glass-face-clear: ${face(GLASS_FACE.clear)};
}
`;
writeFileSync(join(root, "theme/theme.materials.css"), css);

const manifest = {
  file: "theme.materials.css",
  generated: "scripts/materials.mjs",
  description: "Material paint after massimo-v4: the paint roles (shade and lit at an alpha) and the glass faces that the relief classes in nowind.css read. A material never changes a length or a fill of the surface ladder: it adds light (face shading, bevel, cast, inner shadow), a 1px line in place of fills, or transmission on what floats.",
  source: "massimo-v4 packages/ui/src/materials.ts",
  paint: {
    rule: "Light scheme: shade is rgb(27 28 32), lit is white, each at the role's alpha. Dark scheme: black at 3× the shade alpha and white at ¼ the lit alpha, unless the role names its own dark alpha.",
    roles: Object.entries(ROLES).map(([n, role]) => ({ token: `--paint-${n}`, base: role.base, alpha: role.alpha, darkAlpha: role.dark ?? (role.base === "shade" ? r3(role.alpha * 3) : r3(role.alpha / 4)) })),
  },
  glass: {
    tokens: ["--glass-face-frosted", "--glass-face-clear"],
    rule: `The neutral fill (${family}) at ${GLASS_FACE.frosted * 100}% (frosted) or ${GLASS_FACE.clear * 100}% (clear): step 1 in light, step 3 in dark, so the glass sits lighter than the page.`,
    notDone: ["Massimo's glass band (a contrast and brightness filter per scheme that presses the backdrop into a readable band) and its lens and frost texture are not ported."],
  },
  materials: {
    flat: "No paint: the default. Overlays still cast.",
    physical: "Lit: face shading, a bevel (lit top, shaded bottom, half-pixel ring) and the raised cast; pressed sinks to a recess; fields and wells are recessed; cards cast at the popup level.",
    frosted: "Lit, and raised parts, cards and overlays are frosted glass: a 56% face over an 8px blur, a specular sheen, a lit rim and the cast.",
    glass: "Lit, and raised parts, cards and overlays are clear glass after Apple's Liquid Glass: an 18% face over a 0.5px blur, no gloss band, and the light catching the rim as two thin crescents on opposite corners. Add lens for refraction.",
    outline: "No fills but state: every part draws one 1px line in the muted text color; overlays stay opaque.",
  },
  usage: "Set a material on a region with material-physical, material-frosted, material-glass or material-outline (material-flat resets it). Parts say what they are with relief-raised (buttons), relief-raised-solid (primary buttons), relief-recessed (tracks, wells), relief-field (inputs), relief-etched, relief-ground (cards) and relief-overlay (popovers, dialogs). The nearest material wins: the classes are @scope rules that stop at a nested material.",
};
writeFileSync(join(root, "theme/theme.materials.manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log(`theme.materials.css: ${Object.keys(ROLES).length} paint roles, glass faces from ${family}`);
