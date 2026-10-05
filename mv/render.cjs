// Render the MV: headless Chromium draws each frame from mv.js, frames are piped into ffmpeg.
//   node render.cjs preview 10 45.5 130      -> out/preview_<T>.png for given video times
//   node render.cjs video [workers]           -> out/远去的列车.mp4
// Run with NODE_PATH pointing at a global playwright install.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const OUT = path.join(ROOT, 'out');
const SONG = process.env.MV_SONG || path.join(ROOT, 'song.mp3');
fs.mkdirSync(OUT, { recursive: true });

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file://' + path.join(ROOT, 'index.html'));
  await page.evaluate(() => window.mvReady);
  return page;
}
async function grab(page, T, type = 'jpeg') {
  const data = await page.evaluate(([T, type]) => {
    window.renderFrame(T);
    return document.getElementById('c').toDataURL(type === 'png' ? 'image/png' : 'image/jpeg', 0.93);
  }, [T, type]);
  return Buffer.from(data.split(',')[1], 'base64');
}

async function preview(times) {
  const browser = await chromium.launch();
  const page = await openPage(browser);
  for (const t of times) {
    const T = parseFloat(t);
    fs.writeFileSync(path.join(OUT, `preview_${T.toFixed(2)}.png`), await grab(page, T, 'png'));
  }
  await browser.close();
}

async function renderSegment(browser, f0, f1, file, fps) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', file]);
  for (let f = f0; f < f1; f++) {
    const buf = await grab(page, f / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 240 === 0) console.log(`  ${path.basename(file)}: ${f - f0}/${f1 - f0}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await page.close();
}

async function video(workers) {
  const browser = await chromium.launch();
  const page = await openPage(browser);
  const MV = await page.evaluate(() => window.MV);
  await page.close();
  const total = Math.round(MV.TOTAL * MV.FPS);
  const per = Math.ceil(total / workers);
  const segs = [];
  for (let w = 0; w < workers; w++) segs.push([w * per, Math.min(total, (w + 1) * per), path.join(OUT, `seg${w}.mp4`)]);
  console.log(`rendering ${total} frames with ${workers} workers`);
  await Promise.all(segs.map(([a, b, f]) => renderSegment(browser, a, b, f, MV.FPS)));
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'segs.txt'), segs.map(s => `file '${s[2]}'`).join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(OUT, 'segs.txt'), '-c', 'copy', path.join(OUT, 'picture.mp4')]);
  // sound: room tone before/after the song, a single plucked string, the song itself, a distant train at the end
  const pre = MV.PRE, end = MV.TOTAL;
  const songEnd = pre + 240.46;
  const filter = [
    `anoisesrc=color=brown:amplitude=0.05:duration=${end}:sample_rate=48000,lowpass=f=600,volume='if(lt(t,${pre}),0.9,if(gt(t,${songEnd}),0.9,0))':eval=frame,afade=t=in:d=1.5[room]`,
    `[1:a]aresample=48000,adelay=${Math.round((pre - 0.75) * 1000)}|${Math.round((pre - 0.75) * 1000)},volume=0.8[pluck]`,
    `[2:a]aresample=48000,adelay=${pre * 1000}|${pre * 1000}[song]`,
    `anoisesrc=color=brown:amplitude=0.25:duration=${end}:sample_rate=48000,lowpass=f=180,volume='0.9*exp(-pow((t-${pre + 264}),2)/6)':eval=frame[train]`,
    `[room][pluck][song][train]amix=inputs=4:normalize=0,afade=t=out:st=${end - 3}:d=3[a]`,
  ].join(';');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(OUT, 'picture.mp4'), '-i', path.join(ROOT, 'pluck.wav'), '-i', SONG,
    '-filter_complex', filter, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', path.join(OUT, '远去的列车_MV.mp4')]);
  console.log('done:', path.join(OUT, '远去的列车_MV.mp4'));
}

const [mode, ...args] = process.argv.slice(2);
if (mode === 'preview') preview(args).catch(e => { console.error(e); process.exit(1); });
else video(parseInt(args[0] || '4', 10)).catch(e => { console.error(e); process.exit(1); });
