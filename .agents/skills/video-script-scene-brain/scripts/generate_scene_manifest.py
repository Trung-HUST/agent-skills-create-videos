#!/usr/bin/env python3
"""
generate_scene_manifest.py
Validates a scenes.json manifest or converts a plain text script into a structured scenes.json manifest.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_VOICES = {
    "vi": "vi-VN-HoaiMyNeural",
    "vi-male": "vi-VN-NamMinhNeural",
    "en": "en-US-ChristopherNeural",
    "en-female": "en-US-AriaNeural",
}

CAMERA_MOTIONS = ["zoom_in", "zoom_out", "pan_left", "pan_right", "zoom_in_slow"]


def estimate_duration(text: str, lang: str = "vi") -> float:
    words = len(text.split())
    wps = 2.8 if lang.startswith("vi") else 2.5
    return round(max(2.5, words / wps + 0.4), 2)


def validate_manifest(path: Path) -> bool:
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] Invalid JSON in {path}: {exc}", file=sys.stderr)
        return False

    required_top = ["project_title", "language", "aspect_ratio", "resolution", "scenes"]
    for key in required_top:
        if key not in data:
            print(f"[ERROR] Missing top-level key: '{key}'", file=sys.stderr)
            return False

    scenes = data.get("scenes", [])
    if not isinstance(scenes, list) or len(scenes) == 0:
        print("[ERROR] 'scenes' must be a non-empty list.", file=sys.stderr)
        return False

    total_est = 0.0
    for idx, scene in enumerate(scenes, start=1):
        for skey in ["scene_id", "narration_text", "visual_prompt"]:
            if skey not in scene or not str(scene[skey]).strip():
                print(f"[ERROR] Scene #{idx} missing required field '{skey}'", file=sys.stderr)
                return False
        est = scene.get("estimated_duration_sec") or estimate_duration(
            scene["narration_text"], data.get("language", "vi")
        )
        scene["estimated_duration_sec"] = est
        total_est += float(est)

    print(
        f"[OK] Manifest '{data['project_title']}' validated: "
        f"{len(scenes)} scenes, estimated duration ~{total_est:.1f}s "
        f"({data['aspect_ratio']} @ {data['resolution']['width']}x{data['resolution']['height']})"
    )
    return True


def build_from_text(text_path: Path, lang: str, aspect: str, title: str, style: str) -> dict:
    raw = text_path.read_text(encoding="utf-8").strip()
    # Split by blank lines or sentences
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", raw) if p.strip()]
    if len(paragraphs) == 1:
        paragraphs = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]

    width, height = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    scenes = []
    for i, line in enumerate(paragraphs, start=1):
        beat = "hook" if i == 1 else ("cta" if i == len(paragraphs) else "body")
        motion = CAMERA_MOTIONS[(i - 1) % len(CAMERA_MOTIONS)]
        scenes.append(
            {
                "scene_id": i,
                "beat_type": beat,
                "narration_text": line,
                "visual_prompt": f"{style}, visual illustration representing: {line}",
                "camera_motion": motion,
                "transition": "crossfade",
                "overlay_text": "",
                "estimated_duration_sec": estimate_duration(line, lang),
            }
        )

    return {
        "project_title": title,
        "language": lang,
        "aspect_ratio": aspect,
        "resolution": {"width": width, "height": height},
        "fps": 30,
        "voice_config": {
            "engine": "edge-tts",
            "voice_id": DEFAULT_VOICES.get(lang, "vi-VN-HoaiMyNeural"),
            "rate": "+0%",
            "pitch": "+0Hz",
        },
        "style_bible": {
            "model_family": "flux",
            "global_style_prompt": style,
            "negative_prompt": "text, watermark, blurry, low quality, deformed, ugly",
            "character_anchor": "",
        },
        "scenes": scenes,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate or scaffold scenes.json manifest")
    parser.add_argument("--validate", type=Path, help="Path to scenes.json to validate")
    parser.add_argument("--from-text", type=Path, help="Plain text script file to convert")
    parser.add_argument("--lang", default="vi", help="Language code (vi, vi-male, en, en-female)")
    parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"], help="Video aspect ratio")
    parser.add_argument("--title", default="AI Generated Video", help="Project title")
    parser.add_argument(
        "--style",
        default="cinematic digital illustration, dramatic lighting, vibrant colors, high detail, 8k",
        help="Global visual style prompt",
    )
    parser.add_argument("--output", type=Path, default=Path("scenes.json"), help="Output scenes.json path")
    args = parser.parse_args()

    if args.validate:
        ok = validate_manifest(args.validate)
        sys.exit(0 if ok else 1)

    if args.from_text:
        if not args.from_text.exists():
            print(f"[ERROR] Input text file not found: {args.from_text}", file=sys.stderr)
            sys.exit(1)
        manifest = build_from_text(args.from_text, args.lang, args.aspect, args.title, args.style)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] Generated {args.output} with {len(manifest['scenes'])} scenes.")
        validate_manifest(args.output)
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
