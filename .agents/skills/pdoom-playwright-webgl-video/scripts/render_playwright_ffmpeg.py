#!/usr/bin/env python3
"""
render_playwright_ffmpeg.py
Deterministic Offline Video Renderer using Playwright (Headless Chromium) + FFmpeg (libx264).
Inspired by mexicat/pdoom-video: steps time `t = frame_idx / fps` deterministically,
calls window.__pdoom.still(t) or window.renderAtTime(t) in headless Chrome, and pipes frames
directly into FFmpeg with BT.709 color tagging and libx264 CRF 16 encoding.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def probe_audio_duration(audio_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 10.0


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Playwright (Headless Chrome) -> FFmpeg (libx264) Video Renderer"
    )
    parser.add_argument("--url", required=True, help="URL or file:// path of deterministic web scene")
    parser.add_argument("--audio", type=Path, default=None, help="Optional audio track to mux")
    parser.add_argument("--from-sec", type=float, default=0.0, help="Start time in seconds")
    parser.add_argument("--duration", type=float, default=0.0, help="Duration in seconds (0 = auto from audio)")
    parser.add_argument("--fps", type=int, default=60, help="Frames per second (default: 60)")
    parser.add_argument("--width", type=int, default=1920, help="Logical viewport width")
    parser.add_argument("--height", type=int, default=1080, help="Logical viewport height")
    parser.add_argument("--scale", type=int, default=1, help="Resolution scale factor (2 = 4K 3840x2160)")
    parser.add_argument("--crf", type=int, default=16, help="x264 CRF quality (default: 16)")
    parser.add_argument("--preset", default="slow", help="x264 encoding preset")
    parser.add_argument("--output", type=Path, default=Path("output/render.mp4"), help="Output MP4 file")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "[ERROR] Playwright is required. Install via: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    duration = args.duration
    if duration <= 0 and args.audio and args.audio.exists():
        duration = probe_audio_duration(args.audio) - args.from_sec
    if duration <= 0:
        duration = 10.0

    out_w = args.width * args.scale
    out_h = args.height * args.scale
    total_frames = max(1, int(round(duration * args.fps)))
    args.output.parent.mkdir(parents=True, exist_ok=True)

    ff_cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-r",
        str(args.fps),
        "-i",
        "pipe:0",
    ]
    if args.audio and args.audio.exists():
        ff_cmd.extend(["-ss", str(args.from_sec), "-t", str(duration), "-i", str(args.audio)])

    ff_cmd.extend(
        [
            "-vf",
            "scale=out_color_matrix=bt709,setparams=color_primaries=bt709:color_trc=bt709",
            "-c:v",
            "libx264",
            "-preset",
            args.preset,
            "-crf",
            str(args.crf),
            "-pix_fmt",
            "yuv420p",
            "-x264-params",
            "aq-mode=3",
        ]
    )
    if args.audio and args.audio.exists():
        ff_cmd.extend(["-c:a", "aac", "-b:a", "320k", "-shortest"])
    ff_cmd.extend(["-movflags", "+faststart", str(args.output)])

    print(
        f"[RENDER] Launching Headless Chrome ({out_w}x{out_h} @ {args.fps}fps, {total_frames} frames) -> {args.output}"
    )
    ff_proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--enable-gpu-rasterization",
                "--ignore-gpu-blocklist",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
            ],
        )
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        page.goto(args.url, wait_until="networkidle", timeout=120000)

        for f_idx in range(total_frames):
            t = args.from_sec + (f_idx / args.fps)
            page.evaluate(
                """(t) => {
                    if (window.__pdoom && typeof window.__pdoom.still === 'function') {
                        window.__pdoom.still(t, 1, 0.2);
                    } else if (typeof window.renderAtTime === 'function') {
                        window.renderAtTime(t);
                    }
                }""",
                t,
            )
            png_bytes = page.screenshot(type="png")
            ff_proc.stdin.write(png_bytes)
            if (f_idx + 1) % 30 == 0 or (f_idx + 1) == total_frames:
                sys.stdout.write(f"\r  Rendered {f_idx + 1}/{total_frames} frames (t={t:.2f}s)")
                sys.stdout.flush()

        browser.close()

    ff_proc.stdin.close()
    ret = ff_proc.wait()
    print()
    if ret != 0:
        print(f"[ERROR] FFmpeg exited with code {ret}", file=sys.stderr)
        sys.exit(ret)
    print(f"[OK] Deterministic video rendered: {args.output}")


if __name__ == "__main__":
    main()
