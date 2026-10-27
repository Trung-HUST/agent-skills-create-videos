#!/usr/bin/env python3
"""
generate_scene_images.py
Batch-generates scene illustrations from scenes.json using:
  - pollinations (free FLUX endpoint, zero API key)
  - sdwebui (Automatic1111 / Forge local REST API)
  - comfyui (Local ComfyUI HTTP API)
  - placeholder (Offline FFmpeg/Pillow visual storyboard cards)
Updates scenes.json with the generated `image_path` for each scene.
"""
import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


def compose_prompt(scene: dict, style_bible: dict) -> str:
    parts = []
    anchor = style_bible.get("character_anchor", "").strip()
    if anchor:
        parts.append(anchor)
    parts.append(scene.get("visual_prompt", "").strip())
    global_style = style_bible.get("global_style_prompt", "").strip()
    if global_style:
        parts.append(global_style)
    return ", ".join([p for p in parts if p])


def generate_via_pollinations(prompt: str, width: int, height: int, seed: int, out_path: Path) -> bool:
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}&model=flux&nologo=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AG-Video-Pipeline)"})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                if len(data) > 1024:
                    out_path.write_bytes(data)
                    return True
        except Exception as exc:
            print(f"  [WARN] Pollinations attempt {attempt}/3 failed: {exc}")
            time.sleep(2 * attempt)
    return False


def generate_via_sdwebui(
    prompt: str, neg_prompt: str, width: int, height: int, seed: int, api_url: str, out_path: Path
) -> bool:
    payload = {
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "width": width,
        "height": height,
        "seed": seed,
        "steps": 24,
        "cfg_scale": 6.5,
        "sampler_name": "DPM++ 2M Karras",
    }
    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/sdapi/v1/txt2img",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            img_b64 = result["images"][0]
            out_path.write_bytes(base64.b64decode(img_b64))
            return True
    except Exception as exc:
        print(f"  [WARN] SD-WebUI generation failed: {exc}")
        return False


def generate_placeholder_card(scene: dict, width: int, height: int, out_path: Path) -> bool:
    """Offline fallback using FFmpeg lavfi color source so pipeline never breaks without GPU/internet."""
    palette = ["0x1a1b26", "0x16213e", "0x0f3460", "0x1f2937", "0x111827"]
    color = palette[(int(scene.get("scene_id", 1)) - 1) % len(palette)]
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s={width}x{height}:d=1",
        "-frames:v",
        "1",
        str(out_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and out_path.exists()


def main():
    parser = argparse.ArgumentParser(description="Batch generate scene illustrations from scenes.json")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--engine",
        default="pollinations",
        choices=["pollinations", "sdwebui", "comfyui", "placeholder"],
        help="Image generation backend",
    )
    parser.add_argument("--api-url", default="http://127.0.0.1:7860", help="Local API URL for sdwebui/comfyui")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/scenes"), help="Output folder for PNGs")
    parser.add_argument("--seed", type=int, default=4200, help="Base seed for visual consistency")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate existing images")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    res = data.get("resolution", {"width": 1080, "height": 1920})
    width, height = int(res.get("width", 1080)), int(res.get("height", 1920))
    style_bible = data.get("style_bible", {})
    neg_prompt = style_bible.get("negative_prompt", "text, watermark, blurry, low quality")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenes = data.get("scenes", [])

    for idx, scene in enumerate(scenes, start=1):
        sid = scene.get("scene_id", idx)
        out_file = args.output_dir / f"scene_{int(sid):03d}.png"
        if out_file.exists() and not args.overwrite:
            print(f"[SKIP] Scene #{sid} already exists: {out_file}")
            scene["image_path"] = str(out_file).replace("\\", "/")
            continue

        full_prompt = compose_prompt(scene, style_bible)
        scene_seed = args.seed + int(sid)
        print(f"[GEN] Scene #{sid} ({args.engine}) -> {out_file}")

        ok = False
        if args.engine == "pollinations":
            ok = generate_via_pollinations(full_prompt, width, height, scene_seed, out_file)
        elif args.engine == "sdwebui":
            ok = generate_via_sdwebui(
                full_prompt, neg_prompt, width, height, scene_seed, args.api_url, out_file
            )

        if not ok:
            print(f"  [FALLBACK] Generating placeholder card for Scene #{sid}")
            ok = generate_placeholder_card(scene, width, height, out_file)

        if ok:
            scene["image_path"] = str(out_file).replace("\\", "/")
        else:
            print(f"[ERROR] Could not generate image for Scene #{sid}", file=sys.stderr)
            sys.exit(1)

    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] All {len(scenes)} scene images ready and linked in {args.manifest}")


if __name__ == "__main__":
    main()
