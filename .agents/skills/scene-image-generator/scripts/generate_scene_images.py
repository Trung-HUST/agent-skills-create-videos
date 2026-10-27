#!/usr/bin/env python3
"""
generate_scene_images.py
Batch-generates or single-scene regenerates illustrations from scenes.json using:
  - comfyui (Local ComfyUI HTTP API at http://127.0.0.1:8188 with auto checkpoint discovery)
  - pollinations (Free FLUX endpoint, zero API key)
  - sdwebui (Automatic1111 / Forge local REST API at http://127.0.0.1:7860)
  - placeholder (High-contrast Pillow cinematic storyboard cards for offline testing)
Updates scenes.json with the generated `image_path` and `image_engine_used` for each scene.
"""
import argparse
import base64
import json
import random
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def get_ffmpeg_exe() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


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


def discover_comfyui_checkpoint(api_url: str) -> str:
    url = f"{api_url.rstrip('/')}/object_info/CheckpointLoaderSimple"
    req = urllib.request.Request(url, headers={"User-Agent": "AG-Video-Studio/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        info = json.loads(resp.read().decode("utf-8"))
        ckpts = (
            info.get("CheckpointLoaderSimple", {})
            .get("input", {})
            .get("required", {})
            .get("ckpt_name", [[]])[0]
        )
        if ckpts and isinstance(ckpts, list):
            return ckpts[0]
    return "sd_xl_base_1.0.safetensors"


def generate_via_comfyui(
    prompt: str,
    neg_prompt: str,
    width: int,
    height: int,
    seed: int,
    api_url: str,
    out_path: Path,
    checkpoint: str = "",
) -> bool:
    base_url = api_url.rstrip("/")
    try:
        ckpt_name = checkpoint or discover_comfyui_checkpoint(base_url)
    except Exception as exc:
        print(f"  [WARN] ComfyUI server not reachable at {base_url}: {exc}")
        return False

    is_flux_or_lightning = any(k in ckpt_name.lower() for k in ("flux", "lightning", "turbo", "schnell"))
    steps = 6 if is_flux_or_lightning else 22
    cfg = 2.0 if is_flux_or_lightning else 6.5
    sampler = "euler" if is_flux_or_lightning else "dpmpp_2m"
    scheduler = "simple" if is_flux_or_lightning else "karras"

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": cfg,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": sampler,
                "scheduler": scheduler,
                "seed": seed,
                "steps": steps,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": ckpt_name},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": height, "width": width},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": prompt},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": neg_prompt},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "ag_studio_scene", "images": ["8", 0]},
        },
    }

    client_id = str(uuid.uuid4())
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            prompt_id = res_data["prompt_id"]
    except Exception as exc:
        print(f"  [WARN] ComfyUI /prompt queue failed: {exc}")
        return False

    print(f"  [COMFYUI] Queued job {prompt_id} on {ckpt_name} ({width}x{height}, {steps} steps)...")
    deadline = time.time() + 240
    while time.time() < deadline:
        time.sleep(1.5)
        try:
            with urllib.request.urlopen(f"{base_url}/history/{prompt_id}", timeout=10) as hresp:
                hist = json.loads(hresp.read().decode("utf-8"))
                if prompt_id in hist:
                    outputs = hist[prompt_id].get("outputs", {})
                    for node_output in outputs.values():
                        images = node_output.get("images", [])
                        if images:
                            img_info = images[0]
                            q = urllib.parse.urlencode(
                                {
                                    "filename": img_info["filename"],
                                    "subfolder": img_info.get("subfolder", ""),
                                    "type": img_info.get("type", "output"),
                                }
                            )
                            with urllib.request.urlopen(f"{base_url}/view?{q}", timeout=30) as vresp:
                                out_path.write_bytes(vresp.read())
                                return out_path.exists() and out_path.stat().st_size > 1024
        except Exception:
            pass

    print("  [WARN] ComfyUI timed out waiting for image output.")
    return False


def generate_via_pollinations(prompt: str, width: int, height: int, seed: int, out_path: Path) -> bool:
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}&model=flux&nologo=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AG-Video-Pipeline)"})
    for attempt in range(1, 3):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
                if len(data) > 1024:
                    out_path.write_bytes(data)
                    return True
        except Exception as exc:
            print(f"  [WARN] Pollinations attempt {attempt}/2 failed: {exc}")
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
    """Renders a high-contrast cinematic storyboard card using Pillow (or FFmpeg fallback)."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        sid = int(scene.get("scene_id", 1))
        palettes = [
            ((12, 13, 18), (255, 85, 0), (204, 255, 0)),
            ((16, 18, 24), (204, 255, 0), (255, 85, 0)),
            ((10, 15, 22), (255, 110, 40), (240, 240, 235)),
            ((18, 14, 16), (220, 255, 50), (255, 85, 0)),
        ]
        bg, accent, secondary = palettes[(sid - 1) % len(palettes)]
        img = Image.new("RGB", (width, height), color=bg)
        draw = ImageDraw.Draw(img)

        # Subtle architectural grid lines
        step = max(60, width // 16)
        for x in range(0, width, step):
            draw.line([(x, 0), (x, height)], fill=(26, 28, 36), width=1)
        for y in range(0, height, step):
            draw.line([(0, y), (width, y)], fill=(26, 28, 36), width=1)

        # Brutalist frame border + corner markers
        pad = 48
        draw.rectangle([pad, pad, width - pad, height - pad], outline=(55, 58, 70), width=2)
        draw.rectangle([pad, pad, pad + 220, pad + 54], fill=accent)

        try:
            font_lg = ImageFont.truetype("arialbd.ttf", 48)
            font_md = ImageFont.truetype("arial.ttf", 30)
            font_sm = ImageFont.truetype("consola.ttf", 22)
        except Exception:
            font_lg = ImageFont.load_default()
            font_md = ImageFont.load_default()
            font_sm = ImageFont.load_default()

        beat = str(scene.get("beat_type", "SCENE")).upper()
        draw.text((pad + 18, pad + 12), f"SCENE {sid:02d} // {beat}", fill=(10, 10, 10), font=font_sm)

        # Visual prompt preview block
        vp = scene.get("visual_prompt", "")
        words = vp.split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 58:
                lines.append(" ".join(cur[:-1]))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))

        y_text = height // 2 - 90
        draw.text((pad + 40, y_text - 55), "VISUAL DIRECTION (STORYBOARD PREVIEW)", fill=secondary, font=font_sm)
        for line in lines[:5]:
            draw.text((pad + 40, y_text), line, fill=(240, 240, 235), font=font_md)
            y_text += 42

        img.save(out_path, "PNG")
        return out_path.exists()
    except Exception:
        palette = ["0x121318", "0x16213e", "0x0f3460", "0x1f2937"]
        color = palette[(int(scene.get("scene_id", 1)) - 1) % len(palette)]
        cmd = [
            get_ffmpeg_exe(),
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
        default="comfyui",
        choices=["comfyui", "pollinations", "sdwebui", "placeholder"],
        help="Image generation backend",
    )
    parser.add_argument("--api-url", default="http://127.0.0.1:8188", help="Local API URL for comfyui/sdwebui")
    parser.add_argument("--checkpoint", default="", help="Optional ComfyUI checkpoint filename")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/scenes"), help="Output folder for PNGs")
    parser.add_argument("--seed", type=int, default=4200, help="Base seed for visual consistency")
    parser.add_argument("--scene-id", type=int, default=0, help="Regenerate only a specific scene_id (for QC)")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate existing images")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    res = data.get("resolution", {"width": 1920, "height": 1080})
    width, height = int(res.get("width", 1920)), int(res.get("height", 1080))
    style_bible = data.get("style_bible", {})
    neg_prompt = style_bible.get("negative_prompt", "text, watermark, blurry, low quality")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenes = data.get("scenes", [])

    for idx, scene in enumerate(scenes, start=1):
        sid = int(scene.get("scene_id", idx))
        if args.scene_id and sid != args.scene_id:
            continue

        out_file = args.output_dir / f"scene_{sid:03d}.png"
        if out_file.exists() and not args.overwrite and not args.scene_id:
            print(f"[SKIP] Scene #{sid} already exists: {out_file}")
            scene["image_path"] = str(out_file).replace("\\", "/")
            continue

        full_prompt = compose_prompt(scene, style_bible)
        scene_seed = (args.seed + sid) if not args.scene_id else random.randint(10000, 999999)
        print(f"[GEN] Scene #{sid} ({args.engine}) -> {out_file}")

        ok = False
        used_engine = args.engine
        if args.engine == "comfyui":
            ok = generate_via_comfyui(
                full_prompt, neg_prompt, width, height, scene_seed, args.api_url, out_file, args.checkpoint
            )
            if not ok:
                print(f"  [FALLBACK] ComfyUI unavailable -> trying Pollinations FLUX for Scene #{sid}...")
                ok = generate_via_pollinations(full_prompt, width, height, scene_seed, out_file)
                used_engine = "pollinations" if ok else "placeholder"
        elif args.engine == "pollinations":
            ok = generate_via_pollinations(full_prompt, width, height, scene_seed, out_file)
        elif args.engine == "sdwebui":
            ok = generate_via_sdwebui(
                full_prompt, neg_prompt, width, height, scene_seed, args.api_url, out_file
            )

        if not ok:
            print(f"  [FALLBACK] Generating cinematic storyboard card for Scene #{sid}")
            ok = generate_placeholder_card(scene, width, height, out_file)
            used_engine = "placeholder"

        if ok:
            scene["image_path"] = str(out_file).replace("\\", "/")
            scene["image_engine_used"] = used_engine
            scene["image_seed"] = scene_seed
        else:
            print(f"[ERROR] Could not generate image for Scene #{sid}", file=sys.stderr)
            sys.exit(1)

    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Scene image generation completed -> {args.manifest}")


if __name__ == "__main__":
    main()
