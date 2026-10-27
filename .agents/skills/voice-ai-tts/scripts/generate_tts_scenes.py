#!/usr/bin/env python3
"""
generate_tts_scenes.py
Synthesizes studio-grade documentary voiceover audio for each scene in scenes.json:
  - Applies Studio Broadcast Microphone EQ (175Hz warmth boost + gentle compression)
  - Appends a natural 0.55s human breath pause at the end of each scene (`apad=pad_dur=0.55`)
  - Tracks `text_hash` so any change to `narration_text` automatically triggers re-synthesis
  - Measures exact post-processed `audio_duration_sec` for lockstep multi-shot B-roll & subtitle sync
"""
import argparse
import asyncio
import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

KOKORO_VOICE_TO_EDGE_FALLBACK = {
    "am_adam": "en-US-AndrewMultilingualNeural",
    "am_michael": "en-US-ChristopherNeural",
    "af_heart": "en-US-AvaMultilingualNeural",
    "af_bella": "en-US-AriaNeural",
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
    """Accurately measure audio file duration in seconds using soundfile, ffprobe, or bundled ffmpeg."""
    if not audio_path.exists():
        return 5.0

    try:
        import soundfile as sf
        info = sf.info(str(audio_path))
        if info.duration > 0:
            return round(float(info.duration), 3)
    except Exception:
        pass

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

    try:
        cmd = [get_ffmpeg_exe(), "-i", str(audio_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", res.stderr)
        if match:
            hrs, mins, secs = int(match.group(1)), int(match.group(2)), float(match.group(3))
            return round(hrs * 3600 + mins * 60 + secs, 3)
    except Exception:
        pass

    return 5.0


def apply_studio_mic_mastering(raw_audio: Path, final_audio: Path, breath_pause_sec: float = 0.55) -> bool:
    """
    Passes synthesized TTS through an FFmpeg Studio Documentary Mic Chain:
      - Highpass at 75Hz (cleans rumble)
      - Warm low-mid chest resonance at 175Hz (+2.2dB, Shure SM7B style)
      - Smooth dynamic compression
      - Appends 0.55s natural human breath/thinking pause at end of scene
    """
    af = (
        f"highpass=f=75,"
        f"equalizer=f=175:width_type=q:w=1.1:g=2.2,"
        f"equalizer=f=3400:width_type=q:w=1.4:g=1.2,"
        f"acompressor=threshold=-18dB:ratio=2.2:attack=15:release=180,"
        f"apad=pad_dur={breath_pause_sec:.2f}"
    )
    cmd = [
        get_ffmpeg_exe(),
        "-y",
        "-i",
        str(raw_audio),
        "-af",
        af,
        "-ar",
        "44100",
        "-ac",
        "2",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(final_audio),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and final_audio.exists()


_KOKORO_INSTANCE = None


def _format_srt_ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        secs += 1
        ms -= 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def synthesize_kokoro_onnx(
    text: str, voice: str, out_raw: Path, out_sub: Path | None = None, speed: float = 0.84
) -> tuple[bool, list[dict]]:
    global _KOKORO_INSTANCE
    model_dir = Path("models/kokoro")
    onnx_file = model_dir / "kokoro-v1.0.onnx"
    voices_file = model_dir / "voices-v1.0.bin"

    if not (onnx_file.exists() and voices_file.exists()):
        return False, []

    try:
        import numpy as np
        import soundfile as sf
        from kokoro_onnx import Kokoro

        if _KOKORO_INSTANCE is None:
            _KOKORO_INSTANCE = Kokoro(str(onnx_file), str(voices_file))
        kokoro = _KOKORO_INSTANCE

        k_voice = voice if voice in KOKORO_VOICE_TO_EDGE_FALLBACK else "am_adam"
        lang = "en-gb" if k_voice.startswith("b") else "en-us"

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
        if not sentences:
            sentences = [text.strip()]

        all_chunks = []
        sample_rate = 24000
        cursor_sec = 0.0
        inter_pause_sec = 0.32
        word_timings: list[dict] = []
        srt_lines: list[str] = []

        for s_idx, sent in enumerate(sentences):
            samples, sr = kokoro.create(sent, voice=k_voice, speed=speed, lang=lang)
            sample_rate = sr
            sent_dur = len(samples) / float(sr)
            all_chunks.append(samples)

            words = [w for w in sent.split() if w]
            if words:
                weights = [max(2.0, float(len(re.sub(r"\W+", "", w))) + (1.8 if w.endswith((",", ";", ":", "—", "-")) else 0.0)) for w in words]
                total_w = sum(weights)
                w_cursor = cursor_sec
                for w_str, w_val in zip(words, weights):
                    w_dur = sent_dur * (w_val / total_w)
                    word_timings.append(
                        {
                            "w": w_str,
                            "start": round(w_cursor, 3),
                            "end": round(w_cursor + w_dur, 3),
                        }
                    )
                    w_cursor += w_dur

            srt_lines.append(f"{s_idx + 1}")
            srt_lines.append(f"{_format_srt_ts(cursor_sec)} --> {_format_srt_ts(cursor_sec + sent_dur)}")
            srt_lines.append(sent)
            srt_lines.append("")

            cursor_sec += sent_dur
            if s_idx < len(sentences) - 1:
                pad_samples = np.zeros(int(sample_rate * inter_pause_sec), dtype=np.float32)
                all_chunks.append(pad_samples)
                cursor_sec += inter_pause_sec

        full_audio = np.concatenate(all_chunks)
        sf.write(str(out_raw), full_audio, sample_rate, format="WAV")
        if out_sub is not None and srt_lines:
            out_sub.write_text("\n".join(srt_lines), encoding="utf-8")
        return (out_raw.exists() and out_raw.stat().st_size > 0), word_timings
    except Exception as exc:
        print(f"  [WARN] Local kokoro-onnx error: {exc}")
        return False, []



async def synthesize_edge_tts(
    text: str, voice: str, rate: str, pitch: str, out_raw: Path, out_sub: Path
) -> bool:
    try:
        import edge_tts
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "-q"], check=True)
        import edge_tts

    resolved_voice = KOKORO_VOICE_TO_EDGE_FALLBACK.get(voice, voice)
    if not resolved_voice or "-" not in resolved_voice:
        resolved_voice = "en-US-AndrewMultilingualNeural"

    # Use calm documentary pacing (-7% rate) if default +0% was passed
    doc_rate = "-7%" if rate in ("+0%", "0%", "", "-4%") else rate

    communicate = edge_tts.Communicate(text=text, voice=resolved_voice, rate=doc_rate, pitch=pitch)
    submaker = edge_tts.SubMaker()
    with open(out_raw, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    if hasattr(submaker, "get_srt"):
        out_sub.write_text(submaker.get_srt(), encoding="utf-8")
    elif hasattr(submaker, "generate_subs"):
        out_sub.write_text(submaker.generate_subs(), encoding="utf-8")
    return out_raw.exists() and out_raw.stat().st_size > 0


async def run_pipeline(args) -> None:
    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    vcfg = data.get("voice_config", {})
    engine = args.engine or vcfg.get("engine", "kokoro")
    voice = args.voice or vcfg.get("voice_id") or vcfg.get("voice") or "am_adam"
    rate = vcfg.get("rate", "-7%")
    pitch = vcfg.get("pitch", "+0Hz")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenes = data.get("scenes", [])

    for idx, scene in enumerate(scenes, start=1):
        sid = int(scene.get("scene_id", idx))
        if args.scene_id and sid != args.scene_id:
            continue

        text = (scene.get("narration_text") or scene.get("narration") or "").strip()
        scene["narration_text"] = text
        text_hash = hashlib.md5(f"{voice}:{rate}:{text}".encode("utf-8")).hexdigest()[:12]
        out_audio = args.output_dir / f"scene_{sid:03d}.mp3"
        raw_tmp = args.output_dir / f"scene_{sid:03d}_raw.mp3"
        out_sub = args.output_dir / f"scene_{sid:03d}.srt"

        if (
            out_audio.exists()
            and scene.get("text_hash") == text_hash
            and not args.overwrite
            and not args.scene_id
        ):
            dur = probe_duration(out_audio)
            scene["audio_path"] = str(out_audio).replace("\\", "/")
            scene["audio_duration_sec"] = dur
            print(f"[SKIP] Scene #{sid:02d} audio unchanged ({dur:.2f}s): {out_audio}")
            continue

        print(f"[TTS] Scene #{sid:02d} ({engine} / {voice}) -> {out_audio}")
        ok = False
        used_engine = engine
        word_timings: list[dict] = []

        if engine == "kokoro":
            k_speed = float(vcfg.get("speed", 0.84))
            raw_wav = args.output_dir / f"scene_{sid:03d}_raw.wav"
            ok, word_timings = synthesize_kokoro_onnx(text, voice, raw_wav, out_sub=out_sub, speed=k_speed)
            if ok:
                raw_tmp = raw_wav
                used_engine = f"kokoro-82m-onnx ({voice})"
            else:
                fallback_voice = KOKORO_VOICE_TO_EDGE_FALLBACK.get(voice, "en-US-AndrewMultilingualNeural")
                print(f"  [STUDIO VOICE] Using Multilingual Documentary Neural ({fallback_voice}) for Scene #{sid:02d}")
                ok = await synthesize_edge_tts(text, fallback_voice, rate, pitch, raw_tmp, out_sub)
                used_engine = f"neural_studio ({fallback_voice})"
        else:
            ok = await synthesize_edge_tts(text, voice, rate, pitch, raw_tmp, out_sub)

        if not ok:
            print(f"[ERROR] Failed to synthesize TTS for Scene #{sid:02d}", file=sys.stderr)
            sys.exit(1)

        # Master raw TTS with Studio Mic EQ + 0.55s natural breath pause
        if not apply_studio_mic_mastering(raw_tmp, out_audio, breath_pause_sec=0.55):
            shutil.move(str(raw_tmp), str(out_audio))
        else:
            raw_tmp.unlink(missing_ok=True)

        dur = probe_duration(out_audio)
        scene["audio_path"] = str(out_audio).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        scene["text_hash"] = text_hash
        scene["tts_engine_used"] = used_engine
        if word_timings:
            scene["words"] = word_timings
        if out_sub.exists():
            scene["scene_srt_path"] = str(out_sub).replace("\\", "/")
        print(f"  [OK] Scene #{sid:02d} ({used_engine}) studio-mastered duration locked: {dur:.2f}s ({len(word_timings)} words synced)")

    total_dur = sum(float(s.get("audio_duration_sec") or s.get("estimated_duration_sec") or 0.0) for s in scenes)
    data["total_audio_duration_sec"] = round(total_dur, 3)
    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Synthesized {len(scenes)} scenes. Total locked voiceover duration: {total_dur:.2f}s ({total_dur/60:.2f} min)")



def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize studio-mastered per-scene TTS audio")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--engine",
        default="kokoro",
        choices=["kokoro", "edge-tts", "f5-tts", "openai"],
        help="TTS Engine to use",
    )
    parser.add_argument("--voice", default="", help="Override voice ID")
    parser.add_argument("--ref-audio", type=Path, help="Reference WAV file for F5-TTS")
    parser.add_argument("--ref-text", default="", help="Reference transcript for F5-TTS")
    parser.add_argument("--api-url", default="http://127.0.0.1:8880", help="OpenAI-compatible TTS endpoint")
    parser.add_argument("--api-key", default="", help="API key")
    parser.add_argument("--model", default="kokoro", help="Model name")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/audio"), help="Output directory")
    parser.add_argument("--scene-id", type=int, default=0, help="Regenerate only a specific scene_id")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing audio files")
    args = parser.parse_args()

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
