#!/usr/bin/env python3
"""
assemble_video.py
Automated Video Editor & Renderer using FFmpeg.
Reads scenes.json, renders each scene with Ken Burns camera motion synced to its TTS audio,
concatenates all scenes, burns in styled ASS/SRT subtitles, mixes optional BGM, and verifies the final MP4.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def build_camera_filter(motion: str, width: int, height: int, fps: int, duration: float, fast: bool) -> str:
    base_scale = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1"
    )
    if fast:
        return f"{base_scale},fps={fps},format=yuv420p"

    total_frames = max(1, int(round(duration * fps)))
    # Smooth Ken Burns zoom using zoompan
    if motion in ("zoom_out", "zoom_out_slow"):
        z_expr = f"if(eq(on,1),1.12,max(1.0,zoom-0.12/{total_frames}))"
    else:
        z_expr = f"min(zoom+0.12/{total_frames},1.12)"

    return (
        f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,"
        f"crop={width * 2}:{height * 2},"
        f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:s={width}x{height}:fps={fps},"
        f"setsar=1,format=yuv420p"
    )


def escape_ffmpeg_filter_path(p: Path) -> str:
    """Escape path for FFmpeg subtitles/ass filter across Windows & POSIX."""
    try:
        rel = os.path.relpath(p, Path.cwd())
        if not rel.startswith(".."):
            return rel.replace("\\", "/")
    except ValueError:
        pass
    posix = str(p.resolve()).replace("\\", "/")
    return posix.replace(":", r"\:")


def render_scene_clip(
    scene: dict, width: int, height: int, fps: int, clip_path: Path, fast: bool
) -> bool:
    img_path = Path(scene["image_path"])
    aud_path = Path(scene["audio_path"])
    dur = float(scene.get("audio_duration_sec") or scene.get("estimated_duration_sec") or 4.0)
    motion = scene.get("camera_motion", "zoom_in")

    vf = build_camera_filter(motion, width, height, fps, dur, fast)
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(img_path),
        "-i",
        str(aud_path),
        "-t",
        f"{dur:.3f}",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast" if fast else "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-shortest",
        str(clip_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[ERROR] FFmpeg failed on scene clip {clip_path}:\n{res.stderr[-600:]}", file=sys.stderr)
        return False
    return clip_path.exists()


def main():
    parser = argparse.ArgumentParser(description="Assemble final MP4 video from scenes.json")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument("--subtitles", type=Path, default=None, help="Override path to .ass or .srt")
    parser.add_argument("--no-subtitles", action="store_true", help="Do not burn in subtitles")
    parser.add_argument("--bgm", type=Path, default=None, help="Optional background music file")
    parser.add_argument("--bgm-volume", type=float, default=0.15, help="Background music volume (0.0-1.0)")
    parser.add_argument("--fast", action="store_true", help="Fast draft render mode")
    parser.add_argument("--output", type=Path, default=Path("output/final_video.mp4"), help="Output MP4 path")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    res = data.get("resolution", {"width": 1080, "height": 1920})
    width, height = int(res.get("width", 1080)), int(res.get("height", 1920))
    fps = int(data.get("fps", 30))
    scenes = data.get("scenes", [])

    clips_dir = Path("assets/clips")
    clips_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    clip_files = []
    for idx, scene in enumerate(scenes, start=1):
        sid = int(scene.get("scene_id", idx))
        clip_path = clips_dir / f"clip_{sid:03d}.mp4"
        print(f"[RENDER] Scene #{sid} clip -> {clip_path}")
        if not render_scene_clip(scene, width, height, fps, clip_path, args.fast):
            sys.exit(1)
        clip_files.append(clip_path)

    concat_list = clips_dir / "concat_list.txt"
    concat_lines = [f"file '{c.resolve().as_posix()}'" for c in clip_files]
    concat_list.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

    merged_raw = clips_dir / "merged_raw.mp4"
    cmd_concat = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(merged_raw),
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    sub_path = args.subtitles
    if not sub_path and not args.no_subtitles:
        cand = data.get("subtitle_ass_path") or data.get("subtitle_srt_path")
        if cand and Path(cand).exists():
            sub_path = Path(cand)

    vf_filters = []
    if sub_path and sub_path.exists() and not args.no_subtitles:
        escaped_sub = escape_ffmpeg_filter_path(sub_path)
        if sub_path.suffix.lower() == ".ass":
            vf_filters.append(f"ass='{escaped_sub}'")
        else:
            vf_filters.append(f"subtitles='{escaped_sub}'")

    cmd_final = ["ffmpeg", "-y", "-i", str(merged_raw)]
    if args.bgm and args.bgm.exists():
        cmd_final.extend(["-stream_loop", "-1", "-i", str(args.bgm)])

    if vf_filters:
        cmd_final.extend(["-vf", ",".join(vf_filters)])
        cmd_final.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "19"])
    else:
        cmd_final.extend(["-c:v", "copy"])

    if args.bgm and args.bgm.exists():
        af = (
            f"[1:a]volume={args.bgm_volume}[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd_final.extend(["-filter_complex", af, "-map", "0:v:0", "-map", "[aout]", "-c:a", "aac", "-b:a", "192k"])
    else:
        cmd_final.extend(["-c:a", "copy"])

    cmd_final.append(str(args.output))
    print(f"[FINALIZE] Exporting final video -> {args.output}")
    res_final = subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_final.returncode != 0:
        print(f"[ERROR] Final FFmpeg step failed:\n{res_final.stderr[-600:]}", file=sys.stderr)
        sys.exit(1)

    print(f"[SUCCESS] Video rendered successfully: {args.output} ({args.output.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
