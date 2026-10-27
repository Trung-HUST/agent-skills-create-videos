#!/usr/bin/env python3
"""
generate_tts_scenes.py
Synthesizes voiceover audio for each scene in scenes.json using:
  - edge-tts (Default: free neural voices for Vietnamese & English + native VTT/SRT timing extraction)
  - f5-tts (Local zero-shot voice cloning via f5-tts_infer-cli)
  - openai (Any OpenAI-compatible /v1/audio/speech endpoint, e.g., Kokoro-FastAPI or OpenAI)
Measures exact audio duration via ffprobe and updates scenes.json.
"""
import argparse
import asyncio
import json
import subprocess
import sys
import urllib.request
from pathlib import Path


def probe_duration(audio_path: Path) -> float:
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
        return round(float(res.stdout.strip()), 3)
    except Exception:
        return 4.0


async def synthesize_edge_tts(
    text: str, voice: str, rate: str, pitch: str, out_audio: Path, out_sub: Path
) -> bool:
    try:
        import edge_tts
    except ImportError:
        print("[INFO] Installing edge-tts...")
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "-q"], check=True)
        import edge_tts

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    submaker = edge_tts.SubMaker()
    with open(out_audio, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    if hasattr(submaker, "get_srt"):
        out_sub.write_text(submaker.get_srt(), encoding="utf-8")
    elif hasattr(submaker, "generate_subs"):
        out_sub.write_text(submaker.generate_subs(), encoding="utf-8")
    return out_audio.exists() and out_audio.stat().st_size > 0


def synthesize_f5_tts(text: str, ref_audio: Path, ref_text: str, out_audio: Path) -> bool:
    cmd = [
        "f5-tts_infer-cli",
        "--model",
        "F5TTS_v1_Base",
        "--ref_audio",
        str(ref_audio),
        "--ref_text",
        ref_text,
        "--gen_text",
        text,
        "--output_dir",
        str(out_audio.parent),
        "--output_file",
        out_audio.name,
    ]
    res = subprocess.run(cmd)
    return res.returncode == 0 and out_audio.exists()


def synthesize_openai_compatible(
    text: str, voice: str, api_url: str, api_key: str, model: str, out_audio: Path
) -> bool:
    payload = {"model": model, "input": text, "voice": voice, "response_format": "mp3"}
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/v1/audio/speech",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        out_audio.write_bytes(resp.read())
    return out_audio.exists() and out_audio.stat().st_size > 0


async def run_pipeline(args):
    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    vcfg = data.get("voice_config", {})
    voice = args.voice or vcfg.get("voice_id", "vi-VN-HoaiMyNeural")
    rate = vcfg.get("rate", "+0%")
    pitch = vcfg.get("pitch", "+0Hz")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenes = data.get("scenes", [])
    total_dur = 0.0

    for idx, scene in enumerate(scenes, start=1):
        sid = int(scene.get("scene_id", idx))
        text = scene.get("narration_text", "").strip()
        out_audio = args.output_dir / f"scene_{sid:03d}.mp3"
        out_sub = args.output_dir / f"scene_{sid:03d}.srt"

        if out_audio.exists() and not args.overwrite:
            dur = probe_duration(out_audio)
            scene["audio_path"] = str(out_audio).replace("\\", "/")
            scene["audio_duration_sec"] = dur
            if out_sub.exists():
                scene["scene_srt_path"] = str(out_sub).replace("\\", "/")
            total_dur += dur
            print(f"[SKIP] Scene #{sid} audio exists ({dur:.2f}s): {out_audio}")
            continue

        print(f"[TTS] Scene #{sid} ({args.engine} / {voice}) -> {out_audio}")
        ok = False
        if args.engine == "edge-tts":
            ok = await synthesize_edge_tts(text, voice, rate, pitch, out_audio, out_sub)
        elif args.engine == "f5-tts":
            if not args.ref_audio:
                print("[ERROR] --ref-audio is required for f5-tts engine", file=sys.stderr)
                sys.exit(1)
            ok = synthesize_f5_tts(text, args.ref_audio, args.ref_text, out_audio)
        elif args.engine == "openai":
            ok = synthesize_openai_compatible(
                text, voice, args.api_url, args.api_key, args.model, out_audio
            )

        if not ok:
            print(f"[ERROR] Failed to synthesize TTS for Scene #{sid}", file=sys.stderr)
            sys.exit(1)

        dur = probe_duration(out_audio)
        scene["audio_path"] = str(out_audio).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        if out_sub.exists():
            scene["scene_srt_path"] = str(out_sub).replace("\\", "/")
        total_dur += dur
        print(f"  [OK] Scene #{sid} duration: {dur:.2f}s")

    data["total_audio_duration_sec"] = round(total_dur, 3)
    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Synthesized {len(scenes)} scenes. Total voiceover duration: {total_dur:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Synthesize per-scene TTS audio from scenes.json")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--engine",
        default="edge-tts",
        choices=["edge-tts", "f5-tts", "openai"],
        help="TTS Engine to use",
    )
    parser.add_argument("--voice", default="", help="Override voice ID (e.g. vi-VN-NamMinhNeural)")
    parser.add_argument("--ref-audio", type=Path, help="Reference WAV file for F5-TTS voice cloning")
    parser.add_argument("--ref-text", default="", help="Reference transcript for F5-TTS")
    parser.add_argument(
        "--api-url", default="http://127.0.0.1:8880", help="OpenAI-compatible TTS endpoint (e.g. Kokoro-FastAPI)"
    )
    parser.add_argument("--api-key", default="", help="API key for OpenAI-compatible endpoint")
    parser.add_argument("--model", default="kokoro", help="Model name for OpenAI-compatible endpoint")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/audio"), help="Output directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing audio files")
    args = parser.parse_args()

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
