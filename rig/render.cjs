// Render the ALPHA head rig to PNG frames / stills with headless Chromium.
//   node render.cjs --curve out/line08_curve.json --view 34 --mode white --out out/line08_34_white
//   node render.cjs --stills out/jaw_states                    (closed / small / mid / big, 3 views)
const { chromium } = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path");
const A = Object.fromEntries(process.argv.slice(2).join(" ").split("--").filter(Boolean).map(s => { const [k, ...v] = s.trim().split(" "); return [k, v.join(" ") || true]; }));
const ROOT = __dirname, W = +(A.w || 1280), H = +(A.h || 548);
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json" };
const srv = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split("?")[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(r);
});
(async () => {
  await new Promise(ok => srv.listen(0, ok));
  const port = srv.address().port;
  const browser = await chromium.launch({ executablePath: process.env.CHROME || undefined, args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on("console", m => { if (m.type() === "error") console.error("page:", m.text()); });
  const open = async (view, mode) => {
    await page.goto(`http://127.0.0.1:${port}/head.html?w=${W}&h=${H}&view=${view}&mode=${mode}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  };
  if (A.stills) {
    fs.mkdirSync(A.stills, { recursive: true });
    for (const mode of ["white", "paint"]) for (const view of ["front", "34", "side"]) {
      await open(view, mode);
      for (const [name, deg] of [["0_closed", 0], ["1_small", 3.4], ["2_mid", 6.2], ["3_big", 9]]) {
        await page.evaluate(d => { window.load({ fps: 24, max_deg: 9, frames: [d] }); window.setFrame(0, d); }, deg);
        await page.screenshot({ path: path.join(A.stills, `${mode}_${view}_${name}.png`) });
      }
    }
  } else {
    const curve = JSON.parse(fs.readFileSync(A.curve, "utf8"));
    const steps = A.yaw ? JSON.parse(A.yaw) : [[1.75, 4], [3.05, 8], [4.8, 12]];
    fs.mkdirSync(A.out, { recursive: true });
    await open(A.view || "34", A.mode || "white");
    await page.evaluate(([c, s]) => window.load(c, s), [curve, steps]);
    for (let i = 0; i < curve.frames.length; i++) {
      await page.evaluate(i => window.setFrame(i), i);
      await page.screenshot({ path: path.join(A.out, `f${String(i).padStart(4, "0")}.png`) });
    }
    console.log("frames:", curve.frames.length);
  }
  await browser.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
