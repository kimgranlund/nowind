#!/usr/bin/env node
// Serves the repository for local previews with caching turned off, so an edited stylesheet (and every file it
// @imports) is fetched fresh on each reload.
// Usage: node scripts/serve.mjs [port]   (default 8765)
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join, normalize, extname, sep } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const port = Number(process.argv[2] ?? process.env.PORT ?? 8765);

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8",
};

const NO_CACHE = { "Cache-Control": "no-store, max-age=0", Pragma: "no-cache", Expires: "0" };

createServer(async (req, res) => {
  const pathname = (req.url ?? "/").split(/[?#]/)[0] || "/";
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8", ...NO_CACHE }).end("Bad request");
    return;
  }
  let path = normalize(join(root, decoded));
  if (path !== root && !path.startsWith(root + sep)) {
    res.writeHead(403, NO_CACHE).end("Forbidden");
    return;
  }
  try {
    if ((await stat(path)).isDirectory()) path = join(path, "index.html");
    const body = await readFile(path);
    res.writeHead(200, { "Content-Type": TYPES[extname(path)] ?? "application/octet-stream", "X-Nowind-Root": encodeURIComponent(root), ...NO_CACHE });
    res.end(req.method === "HEAD" ? undefined : body);
    console.log(`200 ${pathname}`);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8", ...NO_CACHE }).end("Not found");
    console.log(`404 ${pathname}`);
  }
}).listen(port, "127.0.0.1", () => console.log(`Nowind dev server: http://localhost:${port}/ (no caching)`));
