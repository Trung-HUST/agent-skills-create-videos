#!/usr/bin/env python3
"""
run_video_pipeline.py
Master end-to-end orchestrator that runs all 4 stages of AI Video Production:
  Stage 1: Validate scenes.json manifest
  Stage 2: Generate per-scene illustrations
  Stage 3: Synthesize per-scene TTS voiceovers & probe exact durations
  Stage 4: Generate synchronized SRT/ASS subtitles & assemble final MP4 video
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]


def run_step(title: str, cmd: list[str]) -> None:
    print(f"\n{'=' * 60}\n[STAGE] {title}\n{'=' * 60}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[ERROR] Stage failed: {title}", file=sys.stderr)
        sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(description="Run full 4-stage AI video production pipeline")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--image-engine",
        default="pollinations",
        choices=["pollinations", "sdwebui", "comfyui", "placeholder"],
        help="Scene image generator engine",
    )
    parser.add_argument(
        "--tts-engine",
        default="edge-tts",
        choices=["edge-tts", "f5-tts", "openai"],
        help="TTS voice engine",
    )
    parser.add_argument("--voice", default="", help="Optional TTS voice override")
    parser.add_argument(
        "--subtitle-mode",
        default="manifest",
        choices=["manifest", "whisper"],
        help="Subtitle generation mode",
    )
    parser.add_argument("--bgm", type=Path, default=None, help="Optional background music file")
    parser.add_argument("--fast", action="store_true", help="Fast draft render mode")
    parser.add_argument("--output", type=Path, default=Path("output/final_video.mp4"), help="Output MP4 path")
    args = parser.parse_args()

    s1 = SKILLS_ROOT / "video-script-scene-brain" / "scripts" / "generate_scene_manifest.py"
    s2 = SKILLS_ROOT / "scene-image-generator" / "scripts" / "generate_scene_images.py"
    s3 = SKILLS_ROOT / "voice-ai-tts" / "scripts" / "generate_tts_scenes.py"
    s4_sub = SKILLS_ROOT / "auto-subtitle-video-editor" / "scripts" / "generate_subtitles.py"
    s4_vid = SKILLS_ROOT / "auto-subtitle-video-editor" / "scripts" / "assemble_video.py"

    # Stage 1: Validate Manifest
    run_step("1/4 - Validate Script & Scene Breakdown Manifest", [sys.executable, str(s1), "--validate", str(args.manifest)])

    # Stage 2: Scene Image Generation
    run_step(
        "2/4 - Generate Scene Illustrations",
        [sys.executable, str(s2), "--manifest", str(args.manifest), "--engine", args.image_engine],
    )

    # Stage 3: Voice AI / TTS
    tts_cmd = [sys.executable, str(s3), "--manifest", str(args.manifest), "--engine", args.tts_engine]
    if args.voice:
        tts_cmd.extend(["--voice", args.voice])
    run_step("3/4 - Synthesize Voice AI / TTS & Lock Durations", tts_cmd)

    # Stage 4a: Subtitle Generation
    run_step(
        "4a/4 - Generate Synchronized SRT & Styled ASS Subtitles",
        [sys.executable, str(s4_sub), "--manifest", str(args.manifest), "--mode", args.subtitle_mode],
    )

    # Stage 4b: Automated Video Assembly
    vid_cmd = [sys.executable, str(s4_vid), "--manifest", str(args.manifest), "--output", str(args.output)]
    if args.bgm:
        vid_cmd.extend(["--bgm", str(args.bgm)])
    if args.fast:
        vid_cmd.append("--fast")
    run_step("4b/4 - Render & Assemble Final Video", vid_cmd)

    print(f"\n[PIPELINE COMPLETE] Final video ready at: {args.output}")


if __name__ == "__main__":
    main()
