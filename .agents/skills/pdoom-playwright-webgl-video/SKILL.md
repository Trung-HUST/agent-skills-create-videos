---
name: pdoom-playwright-webgl-video
description: Deterministic Code-Rendered Video Engine (inspired by mexicat/pdoom-video) — renders frame-accurate 60fps 1080p/4K videos from HTML5 Canvas2D, Three.js/WebGL shaders, and kinetic typography using Playwright (Headless Chrome) streaming raw RGB24 frames into FFmpeg (libx264) with adaptive tile-based sub-frame motion blur.
when_to_use: "When the user mentions pdoom-video, deterministic code-rendered video, Playwright Headless Chrome + FFmpeg video rendering, WebGL/Three.js/Canvas2D programmatic video export, frame-by-frame browser capture to libx264, or beat-synced shader/kinetic typography videos."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# P(doom) Deterministic WebGL/Canvas Video Engine (`Playwright Headless Chrome + FFmpeg libx264`)

> **Every Frame is a Pure Function of Time `f(t)`.** Inspired by [`mexicat/pdoom-video`](https://github.com/mexicat/pdoom-video), this architecture replaces non-deterministic screen recording with a deterministic render loop where the live browser preview (`?t=23.0`) and the offline 1080p60 / 4K60 `libx264` export are pixel-identical.

---

## Core Architectural Principles (`mexicat/pdoom-video`)

1. **Pure Determinism (`f.t` Only)**:
   - Visuals must never call `Math.random()`, `Date.now()`, or `performance.now()`.
   - Use seeded PRNG (`mulberry32(seed)`) and `frameIdx(t)` so any frame `t` can be rendered out-of-order or multi-sampled across worker processes.
2. **Logical Layout vs Physical Resolution (`--scale 2` for True 4K)**:
   - Author all scenes in logical `1920×1080` coordinates (`W=1920, H=1080`).
   - Passing `?scale=2` scales WebGL render targets and Canvas2D backing stores to physical `3840×2160` so hairlines, shaders, and typography render at native 4K sharpness.
3. **Adaptive Tile-Based Sub-Frame Motion Blur (`--samples auto --shutter 0.2`)**:
   - Averages `4 → 12 → 36 → 108 → 324` sub-frames spread over `shutter × (1/fps)` per `32×32` logical-pixel tile.
   - Static tiles stop at 12 samples and are masked out via early-Z depth testing; fast whips, zooms, and slams refine up to 108–324 samples for cinema-grade continuous motion blur.
4. **Multi-Worker Playwright Headless Chrome → WebSocket → FFmpeg (`libx264`)**:
   - Spawns `N` headless Chrome GPU instances (`--workers 2 --chunk 8`) with flags:
     `--enable-gpu-rasterization --ignore-gpu-blocklist --disable-background-timer-throttling --disable-renderer-backgrounding`
   - Streams raw `rgb24` pixel buffers over WebSocket into a bounded memory (`--mem-gb 1`) + disk reorder spool (`--spool-gb 20`) and pipes ordered frames to a single FFmpeg encoder with explicit **BT.709 color matrix tagging**:
     ```bash
     ffmpeg -y -f rawvideo -pix_fmt rgb24 -s 1920x1080 -r 60 -i pipe:0 \
       -i audio.mp3 \
       -vf "vflip,scale=out_color_matrix=bt709,setparams=color_primaries=bt709:color_trc=bt709" \
       -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -tune grain -x264-params aq-mode=3 \
       -c:a aac -b:a 320k -shortest -movflags +faststart out/video.mp4
     ```

---

## Window Contract on the Web Page (`window.__renderer` / `window.__pdoom`)

Any HTML/Canvas/Three.js scene page driven by the offline renderer exposes a deterministic hook on `window`:

```ts
window.__pdoom = {
  ready: true,
  width: 1920,
  height: 1080,
  errors: [],
  // Render a single frame (or average of `samples` sub-frames over `shutter`) at exact time `t` seconds:
  still(t: number, samples = 1, shutter = 0.2): number {
    renderSceneAtTime(t, samples, shutter);
    return samples;
  },
};
```

---

## CLI Execution: Render Any Deterministic Web Page to MP4 (`Playwright + FFmpeg`)

Use the built-in Python Playwright + FFmpeg raw-pipe renderer script when rendering HTML5 Canvas / WebGL / Three.js / SVG scenes to `.mp4`:

```bash
python .agents/skills/pdoom-playwright-webgl-video/scripts/render_playwright_ffmpeg.py \
  --url http://localhost:5173/?export=1 \
  --audio assets/audio/merged.wav \
  --duration 60.0 \
  --fps 60 \
  --width 1920 \
  --height 1080 \
  --crf 16 \
  --output output/deterministic_render.mp4
```

Or if using the full Bun/TypeScript `pdoom-video` engine:

```bash
# Render 1080p60 with adaptive sub-frame motion blur
bun scripts/render.ts video --samples auto --shutter 0.2 --out ../out/video.mp4

# Render Contact Sheet to inspect scene cuts & typography
bun scripts/render.ts sheet --from 0 --to 60 --n 16 --cols 4 --out ../out/sheet.png

# Render True 4K60
bun scripts/render.ts video --scale 2 --samples auto --shutter 0.2 --x264 aq-mode=3:rc-lookahead=30 --out ../out/video-4k.mp4
```

---

## Companion Skills

- Audio stem separation, CTC forced alignment & 100fps Librosa envelopes: `.agents/skills/audio-alignment-demucs-ctc-librosa/SKILL.md`
- Expressive 48 kHz TTS (`VieNeu-TTS v3 Turbo` & English `Chatterbox`/`Orpheus`): `.agents/skills/expressive-paralinguistic-tts/SKILL.md`
