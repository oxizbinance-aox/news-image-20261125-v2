// main.ts — entrypoint for make.fun competition news-image-20261125.
// Node 22 stdlib only. Verifies the committed entry.png (PNG, 1024x1024,
// at most 1 MiB) by parsing its IHDR chunk, then copies it to output/.
// The image itself is drawn deterministically by draw_news25_v2.py;
// this program does no drawing and needs no network.
import * as fs from "node:fs";
import * as path from "node:path";

const ROOT: string = path.dirname(new URL(import.meta.url).pathname);
const SRC: string = path.join(ROOT, "entry.png");
const OUT_DIR: string = path.join(ROOT, "output");
const OUT: string = path.join(OUT_DIR, "entry.png");

const buf: Buffer = fs.readFileSync(SRC);
if (buf.length > 1048576) {
  throw new Error(`entry.png is ${buf.length} bytes, over the 1 MiB limit`);
}
const PNG_SIG: Buffer = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error("entry.png is not a PNG file");
}
if (buf.toString("ascii", 12, 16) !== "IHDR") {
  throw new Error("entry.png has no IHDR chunk where one is expected");
}
const width: number = buf.readUInt32BE(16);
const height: number = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, not 1024x1024`);
}
fs.mkdirSync(OUT_DIR, { recursive: true });
fs.copyFileSync(SRC, OUT);
console.log(`entry.png OK: ${width}x${height}, ${buf.length} bytes -> output/entry.png`);
