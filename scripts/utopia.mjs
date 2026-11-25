#!/usr/bin/env node
// Generates the fluid type and space scales (Utopia method) into theme/.
// Usage: node scripts/utopia.mjs [--min-vw 360 --max-vw 1240 --min-base 14 --max-base 18 --min-ratio 1.2 --max-ratio 1.25]
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const defaults = { minVw: 360, maxVw: 1240, minBase: 14, maxBase: 18, minRatio: 1.2, maxRatio: 1.25, rem: 16 };
const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? undefined : Number(args[i + 1]);
};
const cfg = {
  ...defaults,
  ...Object.fromEntries(
    [["minVw", "min-vw"], ["maxVw", "max-vw"], ["minBase", "min-base"], ["maxBase", "max-base"], ["minRatio", "min-ratio"], ["maxRatio", "max-ratio"]]
      .map(([k, f]) => [k, flag(f)])
      .filter(([, v]) => v !== undefined && !Number.isNaN(v)),
  ),
};

const TEXT_STEPS = [["xs", -2], ["sm", -1], ["base", 0], ["lg", 1], ["xl", 2], ["2xl", 3], ["3xl", 4], ["4xl", 5], ["5xl", 6], ["6xl", 7]];
const LINE_HEIGHTS = { xs: 1.5, sm: 1.5, base: 1.5, lg: 1.4, xl: 1.35, "2xl": 1.3, "3xl": 1.2, "4xl": 1.1, "5xl": 1.05, "6xl": 1 };
const KICKERS = [["sm", "xs"], ["md", "sm"], ["lg", "base"]];
const KICKER_FACTOR = 0.92;
const TEXT_FLOOR = 9;
const SPACE_STEPS = [["3xs", 0.25], ["2xs", 0.5], ["xs", 0.75], ["sm", 1], ["md", 1.5], ["lg", 2], ["xl", 3], ["2xl", 4], ["3xl", 6], ["4xl", 8]];

const round = (n, d = 4) => Number(n.toFixed(d));
const rem = (px) => `${round(px / cfg.rem)}rem`;

function fluid(minPx, maxPx) {
  const slope = (maxPx - minPx) / (cfg.maxVw - cfg.minVw);
  const intercept = minPx - slope * cfg.minVw;
  const lo = Math.min(minPx, maxPx);
  const hi = Math.max(minPx, maxPx);
  const sign = slope < 0 ? "-" : "+";
  const css = `clamp(${rem(lo)}, ${rem(intercept)} ${sign} ${round(Math.abs(slope) * 100)} * var(--vw), ${rem(hi)})`;
  return { css, min: round(minPx, 2), max: round(maxPx, 2) };
}

// Below base the steps are fixed fractions of base (Tailwind's 14/16 and 12/16), not Utopia ratios: one ratio step
// down (base / 1.2) is too big a drop for supporting text set beside body text.
const SMALL = { sm: 0.875, xs: 0.75 };
const text = TEXT_STEPS.map(([name, step]) => {
  const f = SMALL[name];
  const v = f ? fluid(cfg.minBase * f, cfg.maxBase * f) : fluid(cfg.minBase * cfg.minRatio ** step, cfg.maxBase * cfg.maxRatio ** step);
  return { name, step, ...v, lineHeight: LINE_HEIGHTS[name], tierFactor: f ?? Number((((cfg.minRatio + cfg.maxRatio) / 2) ** step).toFixed(3)) };
});
const byName = Object.fromEntries(text.map((t) => [t.name, t]));
const kicker = KICKERS.map(([name, beside]) => {
  const b = byName[beside];
  return { name, beside, min: round(Math.max(b.min * KICKER_FACTOR, TEXT_FLOOR), 2), max: round(Math.max(b.max * KICKER_FACTOR, TEXT_FLOOR), 2) };
});
const space = SPACE_STEPS.map(([name, factor]) => ({ name, factor, ...fluid(cfg.minBase * factor, cfg.maxBase * factor) }));

const header = "";

const typeCss = `${header}:root {
  --font-body: "Inter", "Segoe UI", system-ui, sans-serif;
  --font-heading: "Inter Tight", "Inter", "Segoe UI", system-ui, sans-serif;
  --font-display: "Inter Tight", "Inter", "Segoe UI", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  --tracking-tight: -0.01em;
  --tracking-normal: 0em;
  --tracking-wide: 0.025em;
  --tracking-widest: 0.16em;

  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

${text.map((t) => `  --text-${t.name}--line-height: ${t.lineHeight};`).join("\n")}

  --kicker-font: var(--font-mono);
  --kicker-weight: var(--font-weight-medium);
  --kicker-tracking: var(--tracking-widest);
  --kicker-transform: uppercase;
  --vw: 1vw;
}

@supports (width: calc(1rem / 1px * 1px)) {
  :root {
    --vw: calc(1vw * (1rem / ${cfg.rem}px));
  }
}

:root, .scope, .tier-product, .tier-content, .tier-brand {
${text.map((t) => `  --text-${t.name}: calc(${t.css} + var(--tier-text, 0px) * ${t.tierFactor});`).join("\n")}

${kicker.map((k) => `  --kicker-${k.name}: max(calc(var(--text-${k.beside}) * ${KICKER_FACTOR}), ${TEXT_FLOOR}px);`).join("\n")}
}
`;

// Space is a multiple of --F, as all of Affine's spacing is. At the root --F is --text-base, the same fluid clamp the
// Utopia space scale would use, so root values match it exactly; inside a .scope, space follows that scope's font size.
const spaceCss = `${header}:root, .scope, .tier-product, .tier-content, .tier-brand {
${space.map((s) => `  --space-${s.name}: calc(${s.factor} * var(--F));`).join("\n")}
}
`;

const viewport = { minVw: cfg.minVw, maxVw: cfg.maxVw, unit: "px", rem: cfg.rem };
const regenerate = "node scripts/utopia.mjs --min-vw 360 --max-vw 1240 --min-base 14 --max-base 18 --min-ratio 1.2 --max-ratio 1.25";

const typeManifest = {
  file: "theme.typography.css",
  generated: "scripts/utopia.mjs",
  description: "Nowind type: a fluid Utopia scale with Tailwind/Prewind names. Each size is a clamp() from its size at the minimum viewport to its size at the maximum, so it grows with the viewport without media queries.",
  method: "Utopia (utopia.fyi): size(step) = base × ratio^step at each end, interpolated linearly in vw between minVw and maxVw, for base and the steps above it. Below base the steps are fixed fractions, sm 0.875 × base and xs 0.75 × base (Tailwind's 14/16 and 12/16), since a full ratio step down was too big a drop for supporting text.",
  regenerate,
  config: { ...viewport, minBase: cfg.minBase, maxBase: cfg.maxBase, minRatio: cfg.minRatio, maxRatio: cfg.maxRatio },
  naming: {
    sizes: "Tailwind v4 / Prewind: --text-xs … --text-6xl. base is step 0.",
    lineHeights: "Tailwind v4 pattern: --text-{size}--line-height, unitless.",
    faces: "Prewind: --font-body, --font-heading; Tailwind: --font-mono.",
    weights: "Tailwind v4: --font-weight-{name}.",
    tracking: "Tailwind v4 names; values differ: tight is -0.01em (Tailwind -0.025em), widest 0.16em (Tailwind 0.1em).",
  },
  sizes: text.map((t) => ({ token: `--text-${t.name}`, step: t.step, minPx: t.min, maxPx: t.max, lineHeight: t.lineHeight, value: t.css })),
  kicker: {
    rule: `A kicker is ${KICKER_FACTOR} × the size it sits beside, never under ${TEXT_FLOOR}px, so uppercase mono reads at that size's weight.`,
    sizes: kicker.map((k) => ({ token: `--kicker-${k.name}`, beside: `--text-${k.beside}`, minPx: k.min, maxPx: k.max })),
    style: ["--kicker-font: var(--font-mono)", "--kicker-weight: var(--font-weight-medium)", "--kicker-tracking: var(--tracking-widest)", "--kicker-transform: uppercase"],
    use: "Set together: font-family, font-weight, letter-spacing, text-transform, font-size --kicker-{size}, color --fg-weak.",
  },
  faces: [
    { token: "--font-body", use: "Body face: Inter, loaded from Google Fonts by theme.css (variable, 400–700, with optical sizes and italics)." },
    { token: "--font-heading", use: "Headings and display: Inter Tight, 500–800, loaded by theme.css." },
    { token: "--font-display", use: "Display figures and numerals (prices, metrics): Inter Tight, the face that carries 800. Pair with font-extrabold and tracking-tight." },
    { token: "--font-mono", use: "Kicker, code and figures: IBM Plex Mono 400 and 500, loaded by theme.css." },
  ],
  weights: ["--font-weight-normal: 400", "--font-weight-medium: 500", "--font-weight-semibold: 600", "--font-weight-bold: 700", "--font-weight-extrabold: 800 (Inter Tight only: Inter loads 400–700)"],
  tracking: ["--tracking-tight: -0.01em", "--tracking-normal: 0em", "--tracking-wide: 0.025em", "--tracking-widest: 0.16em"],
  leading: ["--leading-none: 1", "--leading-tight: 1.25", "--leading-snug: 1.375", "--leading-normal: 1.5", "--leading-relaxed: 1.625"],
  notes: [
    "Sizes are viewport-fluid. Inside a tier each step grows by the tier's text step (--tier-text: 2px content, 4px brand) times the scale's mean ratio to that step's power, so the whole scale grows with the tier's body size. A .scope with its own font-size does not resize them.",
    "The vw part is --vw: 1vw scaled by the root size over 16px (calc(1vw * (1rem / 16px)), CSS typed arithmetic), so the whole clamp scales with the root font size: a 12px root gives exactly 0.75 of every size at 16px, at any width. Browsers without typed arithmetic keep plain 1vw, where the vw part does not follow the root or zoom; keep maxBase / minBase under about 2.5 (WCAG 1.4.4).",
  ],
};

const spaceManifest = {
  file: "theme.space.css",
  generated: "scripts/utopia.mjs",
  description: "Nowind space: a Utopia-style space scale with Prewind names, written as multiples of --F so it follows the font size like Affine's spacing. At the root --F is the fluid body size, so the values match a Utopia space scale exactly; inside a .scope they follow that scope's font size.",
  method: "space(step) = multiplier × --F. At the root --F = --text-base = Utopia's base (minBase at minVw to maxBase at maxVw), so space(step) = base × multiplier, interpolated linearly in vw.",
  depends: ["theme.geometry.css (--F)", "theme.typography.css (--text-base, which --F follows at the root)"],
  regenerate,
  config: { ...viewport, minBase: cfg.minBase, maxBase: cfg.maxBase },
  sizes: space.map((s) => ({ token: `--space-${s.name}`, multiplier: s.factor, minPx: s.min, maxPx: s.max, value: `calc(${s.factor} * var(--F))` })),
  notes: ["minPx and maxPx are the root values at minVw and maxVw. Inside a .scope the value is multiplier × that scope's font size."],
};

writeFileSync(join(root, "theme/theme.typography.css"), typeCss);
writeFileSync(join(root, "theme/theme.space.css"), spaceCss);
writeFileSync(join(root, "theme/theme.typography.manifest.json"), JSON.stringify(typeManifest, null, 2) + "\n");
writeFileSync(join(root, "theme/theme.space.manifest.json"), JSON.stringify(spaceManifest, null, 2) + "\n");

console.table(text.map((t) => ({ token: `--text-${t.name}`, min: t.min, max: t.max })));
console.table(kicker.map((k) => ({ token: `--kicker-${k.name}`, min: k.min, max: k.max })));
console.table(space.map((s) => ({ token: `--space-${s.name}`, min: s.min, max: s.max })));
