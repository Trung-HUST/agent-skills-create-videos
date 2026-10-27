#!/usr/bin/env python3
"""
generate_tts_scenes.py
Synthesizes voiceover audio for each scene in scenes.json using:
  - kokoro (Local Kokoro-82M via kokoro-onnx or Kokoro-FastAPI, with automatic Edge-TTS neural fallback)
  - edge-tts (Free Microsoft Neural voices for English & Vietnamese + native SRT word boundary extraction)
  - f5-tts (Local zero-shot voice cloning via f5-tts_infer-cli)
  - openai (Any OpenAI-compatible /v1/audio/speech endpoint)
Measures exact audio duration via ffprobe / soundfile / bundled ffmpeg and updates scenes.json.
"""
import argparse
import asyncio
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

KOKORO_VOICE_TO_EDGE_FALLBACK = {
    "af_heart": "en-US-AriaNeural",
    "af_bella": "en-US-JennyNeural",
    "af_nicole": "en-US-AvaNeural",
    "am_adam": "en-US-ChristopherNeural",
    "am_michael": "en-US-GuyNeural",
    "bm_george": "en-GB-RyanNeural",
    "bf_emma": "en-GB-SoniaNeural",
}


def get_ffmpeg_exe() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def probe_duration(audio_path: Path) -> float:
    """Accurately measure audio file duration in seconds using ffprobe, soundfile, or bundled ffmpeg."""
    if not audio_path.exists():
        return 4.0

    # 1. Try soundfile (fast & exact)
    try:
        import soundfile as sf
        info = sf.info(str(audio_path))
        if info.duration > 0:
            return round(float(info.duration), 3)
    except Exception:
        pass

    # 2. Try ffprobe if in PATH
    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        try:
            cmd = [
                ffprobe_bin,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return round(float(res.stdout.strip()), 3)
        except Exception:
            pass

    # 3. Parse Duration from bundled ffmpeg -i stderr
    try:
        cmd = [get_ffmpeg_exe(), "-i", str(audio_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", res.stderr)
        if match:
            hrs, mins, secs = int(match.group(1)), int(match.group(2)), float(match.group(3))
            return round(hrs * 3600 + mins * 60 + secs, 3)
    except Exception:
        pass

    return 4.0


def synthesize_kokoro_onnx(text: str, voice: str, out_audio: Path) -> bool:
    """Synthesize using local kokoro-onnx if model files exist in models/kokoro/."""
    model_dir = Path("models/kokoro")
    onnx_file = model_dir / "kokoro-v1.0.onnx"
    voices_file = model_dir / "voices-v1.0.bin"

    if not (onnx_file.exists() and voices_file.exists()):
        return False

    try:
        import soundfile as sf
        from kokoro_onnx import Kokoro

        kokoro = Kokoro(str(onnx_file), str(voices_file))
        k_voice = voice if voice in KOKORO_VOICE_TO_EDGE_FALLBACK else "am_adam"
        lang = "en-gb" if k_voice.startswith("b") else "en-us"
        samples, sample_rate = kokoro.create(text, voice=k_voice, speed=1.0, lang=lang)
        wav_tmp = out_audio.with_suffix(".wav")
        sf.write(str(wav_tmp), samples, sample_rate)
        # Convert WAV to MP3 using bundled ffmpeg for consistent pipeline handling
        cmd = [
            get_ffmpeg_exe(),
            "-y",
            "-i",
            str(wav_tmp),
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(out_audio),
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        wav_tmp.unlink(missing_ok=True)
        return out_audio.exists() and out_audio.stat().st_size > 0
    except Exception as exc:
        print(f"  [WARN] Local kokoro-onnx error: {exc}")
        return False


async def synthesize_edge_tts(
    text: str, voice: str, rate: str, pitch: str, out_audio: Path, out_sub: Path
) -> bool:
    try:
        import edge_tts
    except ImportError:
        print("[INFO] Installing edge-tts...")
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "-q"], check=True)
        import edge_tts

    # Map Kokoro voice names to high-retention English Edge-TTS neural voices if needed
    resolved_voice = KOKORO_VOICE_TO_EDGE_FALLBACK.get(voice, voice)
    if not resolved_voice or "-" not in resolved_voice:
        resolved_voice = "en-US-ChristopherNeural"

    communicate = edge_tts.Communicate(text=text, voice=resolved_voice, rate=rate, pitch=pitch)
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
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            out_audio.write_bytes(resp.read())
        return out_audio.exists() and out_audio.stat().st_size > 0
    except Exception:
        return False


async def run_pipeline(args):
    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    vcfg = data.get("voice_config", {})
    engine = args.engine or vcfg.get("engine", "kokoro")
    voice = args.voice or vcfg.get("voice_id", "am_adam")
    rate = vcfg.get("rate", "+0%")
    pitch = vcfg.get("pitch", "+0Hz")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenes = data.get("scenes", [])
    total_dur = 0.0

    for idx, scene in enumerate(scenes, start=1):
        sid = int(scene.get("scene_id", idx))
        if args.scene_id and sid != args.scene_id:
            if scene.get("audio_duration_sec"):
                total_dur += float(scene["audio_duration_sec"])
            continue

        text = scene.get("narration_text", "").strip()
        out_audio = args.output_dir / f"scene_{sid:03d}.mp3"
        out_sub = args.output_dir / f"scene_{sid:03d}.srt"

        if out_audio.exists() and not args.overwrite and not args.scene_id:
            dur = probe_duration(out_audio)
            scene["audio_path"] = str(out_audio).replace("\\", "/")
            scene["audio_duration_sec"] = dur
            if out_sub.exists():
                scene["scene_srt_path"] = str(out_sub).replace("\\", "/")
            total_dur += dur
            print(f"[SKIP] Scene #{sid} audio exists ({dur:.2f}s): {out_audio}")
            continue

        print(f"[TTS] Scene #{sid} ({engine} / {voice}) -> {out_audio}")
        ok = False
        used_engine = engine

        if engine == "kokoro":
            # 1. Try local kokoro-onnx weights in models/kokoro/
            ok = synthesize_kokoro_onnx(text, voice, out_audio)
            # 2. Try local Kokoro-FastAPI server on port 8880
            if not ok:
                ok = synthesize_openai_compatible(
                    text, voice if voice in KOKORO_VOICE_TO_EDGE_FALLBACK else "am_adam", args.api_url, args.api_key, "kokoro", out_audio
                )
            # 3. Seamless fallback to Edge-TTS Neural voice
            if not ok:
                fallback_voice = KOKORO_VOICE_TO_EDGE_FALLBACK.get(voice, "en-US-ChristopherNeural")
                print(f"  [FALLBACK] Using Neural TTS ({fallback_voice}) for Scene #{sid}")
                ok = await synthesize_edge_tts(text, fallback_voice, rate, pitch, out_audio, out_sub)
                used_engine = f"edge-tts ({fallback_voice})"
        elif engine == "edge-tts":
            ok = await synthesize_edge_tts(text, voice, rate, pitch, out_audio, out_sub)
        elif engine == "f5-tts":
            if not args.ref_audio:
                print("[ERROR] --ref-audio is required for f5-tts engine", file=sys.stderr)
                sys.exit(1)
            ok = synthesize_f5_tts(text, args.ref_audio, args.ref_text, out_audio)
        elif engine == "openai":
            ok = synthesize_openai_compatible(
                text, voice, args.api_url, args.api_key, args.model, out_audio
            )

        if not ok:
            print(f"[ERROR] Failed to synthesize TTS for Scene #{sid}", file=sys.stderr)
            sys.exit(1)

        dur = probe_duration(out_audio)
        scene["audio_path"] = str(out_audio).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        scene["tts_engine_used"] = used_engine
        if out_sub.exists():
            scene["scene_srt_path"] = str(out_sub).replace("\\", "/")
        total_dur += dur
        print(f"  [OK] Scene #{sid} duration locked: {dur:.2f}s")

    # Recompute total duration across all scenes
    total_dur = sum(float(s.get("audio_duration_sec") or s.get("estimated_duration_sec") or 0.0) for s in scenes)
    data["total_audio_duration_sec"] = round(total_dur, 3)
    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Synthesized TTS. Total locked voiceover duration: {total_dur:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Synthesize per-scene TTS audio from scenes.json")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--engine",
        default="kokoro",
        choices=["kokoro", "edge-tts", "f5-tts", "openai"],
        help="TTS Engine to use",
    )
    parser.add_argument("--voice", default="", help="Override voice ID (e.g. am_adam, af_heart, en-US-ChristopherNeural)")
    parser.add_argument("--ref-audio", type=Path, help="Reference WAV file for F5-TTS voice cloning")
    parser.add_argument("--ref-text", default="", help="Reference transcript for F5-TTS")
    parser.add_argument(
        "--api-url", default="http://127.0.0.1:8880", help="OpenAI-compatible TTS endpoint (e.g. Kokoro-FastAPI)"
    )
    parser.add_argument("--api-key", default="", help="API key for OpenAI-compatible endpoint")
    parser.add_argument("--model", default="kokoro", help="Model name for OpenAI-compatible endpoint")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/audio"), help="Output directory")
    parser.add_argument("--scene-id", type=int, default=0, help="Regenerate only a specific scene_id (for QC)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing audio files")
    args = parser.parse_args()

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
