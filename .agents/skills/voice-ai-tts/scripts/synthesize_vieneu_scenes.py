#!/usr/bin/env python3
"""
synthesize_vieneu_scenes.py — Expressive Paralinguistic 48 kHz TTS & Clean Subtitle Pipeline

Primary Vietnamese Engine:
  - VieNeu-TTS v3 Turbo (`pnnbao-ump/VieNeu-TTS-v3-Turbo`, 48 kHz)
  - Default Voice: "Hải Đăng" (⭐ Hải Đăng — Nam · Bắc · Phong cách tự nhiên)
  - Native inline paralinguistic cues in 48 kHz stream:
      * [cười]      : Natural ironic chuckle / laugh (e.g., Nassim Taleb's paradoxes — Scenes 1,2,3,4,5,6,8,9,12)
      * [thở dài]   : Contemplative sigh / deep breath (e.g., Day 1,001 Turkey crash, Silent Evidence, Mediocristan — Scenes 2,7,10)
      * [hắng giọng]: Decisive throat clear before exposing key mental models (e.g., Gaussian Bell Curve Fraud, Epistemic Arrogance, 90/10 Barbell — Scenes 1,4,8,11)

Equivalent Expressive English Engines:
  - chatterbox : Resemble AI Chatterbox-Turbo ([laugh], [chuckle], [sigh], [clear throat], [cough], [gasp])
  - orpheus    : Canopy Labs Orpheus-TTS 3B (Voices: leo, dan, zac, tara; tags: <chuckle>, <sigh>, <cough>)
  - dia        : Nari Labs Dia-1.6B (tags: (laughs), (sighs), (clears throat))
  - kokoro     : Kokoro-82M (Voices: bm_george, am_michael, am_adam; tags converted to natural cadence pauses)
  - edge-tts   : Fallback neural TTS (tags converted to cadence pauses, resampled to 48 kHz)

Clean Subtitle Guarantee:
  - While preserving [cười], [thở dài], [hắng giọng] (and English [laugh], [sigh], [clear throat]) in the
    48 kHz audio synthesis stream, `strip_paralinguistic_tags()` automatically removes all emotion tags from
    `clean_subtitle_text` and generated `.srt` files so on-screen captions are 100% clean.
"""

import argparse
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Regex matching all Vietnamese & English paralinguistic tags across VieNeu-TTS, Chatterbox, Orpheus, and Dia
PARALINGUISTIC_TAG_PATTERN = re.compile(
    r"""
    \[
        \s*(?:
            cười|cười\s+nhẹ|bật\s+cười|thở\s+dài|hắng\s+giọng|lấy\s+hơi|ngập\s+ngừng|
            laugh|laughs|chuckle|chuckles|sigh|sighs|clear\s+throat|clears\s+throat|
            throat\s+clear|cough|coughs|gasp|gasps|whisper|groan|sniffle|yawn
        )\s*
    \]
    |
    <
        \s*(?:
            laugh|chuckle|sigh|cough|clear_throat|gasp|groan|sniffle|yawn
        )\s*
    >
    |
    \(
        \s*(?:
            laughs|chuckles|sighs|clears\s+throat|coughs|gasps
        )\s*
    \)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def strip_paralinguistic_tags(text: str) -> str:
    """
    Removes [cười], [thở dài], [hắng giọng] and all English paralinguistic tags
    ([laugh], [chuckle], [sigh], [clear throat], <laugh>, <sigh>, etc.) so that
    on-screen subtitles are 100% clean.
    """
    cleaned = PARALINGUISTIC_TAG_PATTERN.sub(" ", text)
    # Collapse multiple spaces and clean spaces before punctuation
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def adapt_tags_for_engine(text: str, engine: str) -> str:
    """
    Adapts paralinguistic tags to the target TTS engine's native syntax:
      - vieneu     : keeps [cười], [thở dài], [hắng giọng] (and converts English tags to Vietnamese if needed)
      - chatterbox : converts [cười] -> [chuckle], [thở dài] -> [sigh], [hắng giọng] -> [clear throat]
      - orpheus    : converts to <chuckle>, <sigh>, <cough>
      - dia        : converts to (chuckles), (sighs), (clears throat)
      - kokoro / edge-tts : replaces tags with natural breath punctuation (... / —) so tags are NEVER read aloud
    """
    eng = engine.lower()

    if eng == "vieneu":
        out = re.sub(r"\[\s*(?:laugh|laughs|chuckle|chuckles)\s*\]|<\s*(?:laugh|chuckle)\s*>", "[cười]", text, flags=re.I)
        out = re.sub(r"\[\s*(?:sigh|sighs)\s*\]|<\s*sigh\s*>", "[thở dài]", out, flags=re.I)
        out = re.sub(r"\[\s*(?:clear\s+throat|clears\s+throat|cough)\s*\]|<\s*cough\s*>", "[hắng giọng]", out, flags=re.I)
        return re.sub(r"\s{2,}", " ", out).strip()

    if eng == "chatterbox":
        out = re.sub(r"\[\s*cười\s*\]|<\s*(?:laugh|chuckle)\s*>", "[chuckle]", text, flags=re.I)
        out = re.sub(r"\[\s*thở\s+dài\s*\]|<\s*sigh\s*>", "[sigh]", out, flags=re.I)
        out = re.sub(r"\[\s*hắng\s+giọng\s*\]|<\s*cough\s*>", "[clear throat]", out, flags=re.I)
        return re.sub(r"\s{2,}", " ", out).strip()

    if eng == "orpheus":
        out = re.sub(r"\[\s*(?:cười|laugh|laughs|chuckle|chuckles)\s*\]", "<chuckle>", text, flags=re.I)
        out = re.sub(r"\[\s*(?:thở\s+dài|sigh|sighs)\s*\]", "<sigh>", out, flags=re.I)
        out = re.sub(r"\[\s*(?:hắng\s+giọng|clear\s+throat|clears\s+throat|cough)\s*\]", "<cough>", out, flags=re.I)
        return re.sub(r"\s{2,}", " ", out).strip()

    if eng == "dia":
        out = re.sub(r"\[\s*(?:cười|laugh|laughs|chuckle|chuckles)\s*\]", "(chuckles)", text, flags=re.I)
        out = re.sub(r"\[\s*(?:thở\s+dài|sigh|sighs)\s*\]", "(sighs)", text, flags=re.I)
        out = re.sub(r"\[\s*(?:hắng\s+giọng|clear\s+throat|clears\s+throat|cough)\s*\]", "(clears throat)", out, flags=re.I)
        return re.sub(r"\s{2,}", " ", out).strip()

    # For engines without inline paralinguistic token support (kokoro, edge-tts):
    # Replace mid-sentence tags with natural pause punctuation, and strip leading tags cleanly
    out = PARALINGUISTIC_TAG_PATTERN.sub(" ... ", text)
    out = re.sub(r"^\s*\.\.\.\s*", "", out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out


def probe_duration(audio_path: Path) -> float:
    """Returns exact audio duration in seconds via ffprobe."""
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
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    try:
        return round(float(res.stdout.strip()), 3)
    except ValueError:
        return 0.0


def finalize_48khz_wav(raw_audio_path: Path, final_wav_path: Path, sample_rate: int = 48000, tail_pad_sec: float = 0.55) -> None:
    """
    Ensures studio-grade 48 kHz PCM WAV output and appends a natural room-tone breath pause
    at the end of each scene so scene transitions never clip the speaker's final syllable.
    """
    tmp_path = final_wav_path.with_suffix(".tmp.wav")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(raw_audio_path),
        "-af",
        f"aresample={sample_rate},apad=pad_dur={tail_pad_sec}",
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(tmp_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode == 0 and tmp_path.exists():
        if raw_audio_path != final_wav_path and raw_audio_path.exists():
            raw_audio_path.unlink(missing_ok=True)
        tmp_path.replace(final_wav_path)
    elif raw_audio_path != final_wav_path and raw_audio_path.exists():
        raw_audio_path.replace(final_wav_path)


def synthesize_with_vieneu(
    scenes: List[Dict],
    output_dir: Path,
    voice: str = "Hải Đăng",
    model_id: Optional[str] = None,
    sample_rate: int = 48000,
    tail_pad_sec: float = 0.55,
) -> None:
    """
    Synthesizes 48 kHz Vietnamese audio using VieNeu-TTS v3 Turbo (`pnnbao-ump/VieNeu-TTS-v3-Turbo`)
    with default voice 'Hải Đăng' (⭐ Hải Đăng — Nam · Bắc · Phong cách tự nhiên).
    """
    try:
        from vieneu import Vieneu
    except ImportError:
        print(
            "[ERROR] 'vieneu' package is not installed. Install with: pip install vieneu soundfile",
            file=sys.stderr,
        )
        sys.exit(1)

    kwargs = {}
    if model_id:
        kwargs["backbone_repo"] = model_id
    tts = Vieneu(**kwargs)

    # Resolve voice preset if available in Vieneu preset list
    print(f"[VieNeu-TTS v3 Turbo 48kHz] Initializing voice: '{voice}'...")
    for scene in scenes:
        scene_id = int(scene.get("scene_id", 1))
        raw_text = str(scene.get("narration_text", "")).strip()
        tts_text = adapt_tags_for_engine(raw_text, "vieneu")
        clean_text = strip_paralinguistic_tags(raw_text)

        scene["tts_input_text"] = tts_text
        scene["clean_subtitle_text"] = clean_text

        raw_wav = output_dir / f"scene_{scene_id:03d}_raw.wav"
        final_wav = output_dir / f"scene_{scene_id:03d}.wav"

        audio_spec = tts.infer(text=tts_text, voice=voice)
        tts.save(audio_spec, str(raw_wav))
        finalize_48khz_wav(raw_wav, final_wav, sample_rate=sample_rate, tail_pad_sec=tail_pad_sec)

        dur = probe_duration(final_wav)
        scene["audio_path"] = str(final_wav).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        print(f"  [Scene {scene_id:02d}] {dur:5.2f}s (48kHz) | Clean caption: {clean_text[:68]}...")

    tts.close()


def synthesize_with_chatterbox(
    scenes: List[Dict],
    output_dir: Path,
    ref_audio: Optional[Path] = None,
    exaggeration: float = 0.55,
    cfg_weight: float = 0.4,
    sample_rate: int = 48000,
    tail_pad_sec: float = 0.55,
) -> None:
    """
    Synthesizes English expressive speech using Resemble AI Chatterbox / Chatterbox-Turbo
    with inline [laugh], [chuckle], [sigh], [clear throat] tags.
    """
    try:
        import torch
        import torchaudio as ta
        from chatterbox.tts import ChatterboxTTS
    except ImportError:
        print(
            "[ERROR] 'chatterbox-tts' is not installed. Install with: pip install chatterbox-tts",
            file=sys.stderr,
        )
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)

    for scene in scenes:
        scene_id = int(scene.get("scene_id", 1))
        raw_text = str(scene.get("narration_text", "")).strip()
        tts_text = adapt_tags_for_engine(raw_text, "chatterbox")
        clean_text = strip_paralinguistic_tags(raw_text)

        scene["tts_input_text"] = tts_text
        scene["clean_subtitle_text"] = clean_text

        raw_wav = output_dir / f"scene_{scene_id:03d}_raw.wav"
        final_wav = output_dir / f"scene_{scene_id:03d}.wav"

        gen_kwargs = {"exaggeration": exaggeration, "cfg_weight": cfg_weight}
        if ref_audio and ref_audio.exists():
            gen_kwargs["audio_prompt_path"] = str(ref_audio)

        wav = model.generate(tts_text, **gen_kwargs)
        ta.save(str(raw_wav), wav, model.sr)
        finalize_48khz_wav(raw_wav, final_wav, sample_rate=sample_rate, tail_pad_sec=tail_pad_sec)

        dur = probe_duration(final_wav)
        scene["audio_path"] = str(final_wav).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        print(f"  [Scene {scene_id:02d}] {dur:5.2f}s (Chatterbox->48kHz) | Clean caption: {clean_text[:68]}...")


def synthesize_with_orpheus(
    scenes: List[Dict],
    output_dir: Path,
    voice: str = "leo",
    sample_rate: int = 48000,
    tail_pad_sec: float = 0.55,
) -> None:
    """
    Synthesizes English expressive speech using Canopy Labs Orpheus-TTS 3B (`canopylabs/orpheus-3b-0.1-ft`).
    Default voice 'leo' (or 'dan') is the direct English counterpart to VieNeu-TTS 'Hải Đăng'.
    Supports <laugh>, <chuckle>, <sigh>, <cough>, <gasp>.
    """
    try:
        import wave
        from orpheus_tts import OrpheusModel
    except ImportError:
        print(
            "[ERROR] 'orpheus-speech' is not installed. Install with: pip install orpheus-speech",
            file=sys.stderr,
        )
        sys.exit(1)

    model = OrpheusModel(model_name="canopylabs/orpheus-3b-0.1-ft")
    for scene in scenes:
        scene_id = int(scene.get("scene_id", 1))
        raw_text = str(scene.get("narration_text", "")).strip()
        tts_text = adapt_tags_for_engine(raw_text, "orpheus")
        clean_text = strip_paralinguistic_tags(raw_text)

        scene["tts_input_text"] = tts_text
        scene["clean_subtitle_text"] = clean_text

        raw_wav = output_dir / f"scene_{scene_id:03d}_raw.wav"
        final_wav = output_dir / f"scene_{scene_id:03d}.wav"

        syn_tokens = model.generate_speech(prompt=tts_text, voice=voice)
        with wave.open(str(raw_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            for audio_chunk in syn_tokens:
                wf.writeframes(audio_chunk)

        finalize_48khz_wav(raw_wav, final_wav, sample_rate=sample_rate, tail_pad_sec=tail_pad_sec)
        dur = probe_duration(final_wav)
        scene["audio_path"] = str(final_wav).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        print(f"  [Scene {scene_id:02d}] {dur:5.2f}s (Orpheus '{voice}'->48kHz) | Clean caption: {clean_text[:68]}...")


def synthesize_with_kokoro(
    scenes: List[Dict],
    output_dir: Path,
    voice: str = "bm_george",
    sample_rate: int = 48000,
    tail_pad_sec: float = 0.55,
) -> None:
    """
    Synthesizes English philosophical narration using Kokoro-82M (`bm_george`, `am_michael`, `am_adam`)
    and upsamples to 48 kHz WAV.
    """
    try:
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError:
        print(
            "[ERROR] 'kokoro' package is not installed. Install with: pip install kokoro soundfile",
            file=sys.stderr,
        )
        sys.exit(1)

    lang_code = "b" if voice.startswith("b") else "a"
    pipeline = KPipeline(lang_code=lang_code)
    import numpy as np

    for scene in scenes:
        scene_id = int(scene.get("scene_id", 1))
        raw_text = str(scene.get("narration_text", "")).strip()
        tts_text = adapt_tags_for_engine(raw_text, "kokoro")
        clean_text = strip_paralinguistic_tags(raw_text)

        scene["tts_input_text"] = tts_text
        scene["clean_subtitle_text"] = clean_text

        raw_wav = output_dir / f"scene_{scene_id:03d}_raw.wav"
        final_wav = output_dir / f"scene_{scene_id:03d}.wav"

        chunks = []
        for _, _, audio in pipeline(tts_text, voice=voice, speed=0.96):
            if audio is not None:
                chunks.append(audio)
        full_audio = np.concatenate(chunks) if chunks else np.zeros(24000, dtype=np.float32)
        sf.write(str(raw_wav), full_audio, 24000)
        finalize_48khz_wav(raw_wav, final_wav, sample_rate=sample_rate, tail_pad_sec=tail_pad_sec)

        dur = probe_duration(final_wav)
        scene["audio_path"] = str(final_wav).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        print(f"  [Scene {scene_id:02d}] {dur:5.2f}s (Kokoro '{voice}'->48kHz) | Clean caption: {clean_text[:68]}...")


async def _edge_tts_scene(text: str, voice: str, rate: str, raw_mp3: Path) -> None:
    import edge_tts

    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await comm.save(str(raw_mp3))


def synthesize_with_edge_tts(
    scenes: List[Dict],
    output_dir: Path,
    voice: str = "vi-VN-NamMinhNeural",
    rate: str = "-4%",
    sample_rate: int = 48000,
    tail_pad_sec: float = 0.55,
) -> None:
    """
    Fallback synthesis using Edge-TTS with automatic paralinguistic tag stripping/pause conversion
    so [cười], [thở dài], [hắng giọng] are never read aloud as literal words.
    """
    for scene in scenes:
        scene_id = int(scene.get("scene_id", 1))
        raw_text = str(scene.get("narration_text", "")).strip()
        tts_text = adapt_tags_for_engine(raw_text, "edge-tts")
        clean_text = strip_paralinguistic_tags(raw_text)

        scene["tts_input_text"] = tts_text
        scene["clean_subtitle_text"] = clean_text

        raw_mp3 = output_dir / f"scene_{scene_id:03d}_raw.mp3"
        final_wav = output_dir / f"scene_{scene_id:03d}.wav"

        asyncio.run(_edge_tts_scene(tts_text, voice=voice, rate=rate, raw_mp3=raw_mp3))
        finalize_48khz_wav(raw_mp3, final_wav, sample_rate=sample_rate, tail_pad_sec=tail_pad_sec)

        dur = probe_duration(final_wav)
        scene["audio_path"] = str(final_wav).replace("\\", "/")
        scene["audio_duration_sec"] = dur
        print(f"  [Scene {scene_id:02d}] {dur:5.2f}s (Edge-TTS->48kHz) | Clean caption: {clean_text[:68]}...")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Synthesize 48 kHz expressive voiceovers (VieNeu-TTS v3 Turbo 'Hải Đăng' & English counterparts) while keeping subtitle text 100% free of [cười], [thở dài], [hắng giọng] tags."
    )
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--engine",
        choices=["vieneu", "chatterbox", "orpheus", "kokoro", "edge-tts", "clean-only"],
        default="vieneu",
        help="TTS engine (default: vieneu for VieNeu-TTS v3 Turbo 48kHz; clean-only to strip subtitle tags without running TTS)",
    )
    parser.add_argument(
        "--voice",
        default="Hải Đăng",
        help="Voice preset: 'Hải Đăng' (default VieNeu-TTS v3 Turbo), 'Mai Anh', 'leo'/'dan' (Orpheus), 'bm_george'/'am_michael' (Kokoro)",
    )
    parser.add_argument("--model-id", default=None, help="Optional HuggingFace model repo override")
    parser.add_argument("--ref-audio", type=Path, default=None, help="Reference voice WAV for zero-shot cloning (Chatterbox)")
    parser.add_argument("--sample-rate", type=int, default=48000, help="Output audio sample rate in Hz (default: 48000)")
    parser.add_argument("--tail-pad", type=float, default=0.55, help="End-of-scene natural breath pause in seconds (default: 0.55)")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/audio"), help="Output directory for 48 kHz .wav files")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    if not scenes:
        print("[ERROR] No scenes found in manifest.", file=sys.stderr)
        sys.exit(1)

    # Always populate clean_subtitle_text first so subtitles are guaranteed 100% clean
    for scene in scenes:
        raw_text = str(scene.get("narration_text", "")).strip()
        scene["clean_subtitle_text"] = strip_paralinguistic_tags(raw_text)

    if args.engine == "clean-only":
        args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] Stripped paralinguistic tags ([cười], [thở dài], [hắng giọng], etc.) into 'clean_subtitle_text' for {len(scenes)} scenes.")
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.engine == "vieneu":
        synthesize_with_vieneu(
            scenes,
            output_dir=args.output_dir,
            voice=args.voice,
            model_id=args.model_id,
            sample_rate=args.sample_rate,
            tail_pad_sec=args.tail_pad,
        )
    elif args.engine == "chatterbox":
        synthesize_with_chatterbox(
            scenes,
            output_dir=args.output_dir,
            ref_audio=args.ref_audio,
            sample_rate=args.sample_rate,
            tail_pad_sec=args.tail_pad,
        )
    elif args.engine == "orpheus":
        orpheus_voice = "leo" if args.voice == "Hải Đăng" else args.voice
        synthesize_with_orpheus(
            scenes,
            output_dir=args.output_dir,
            voice=orpheus_voice,
            sample_rate=args.sample_rate,
            tail_pad_sec=args.tail_pad,
        )
    elif args.engine == "kokoro":
        kokoro_voice = "bm_george" if args.voice == "Hải Đăng" else args.voice
        synthesize_with_kokoro(
            scenes,
            output_dir=args.output_dir,
            voice=kokoro_voice,
            sample_rate=args.sample_rate,
            tail_pad_sec=args.tail_pad,
        )
    elif args.engine == "edge-tts":
        edge_voice = "vi-VN-NamMinhNeural" if args.voice == "Hải Đăng" else args.voice
        synthesize_with_edge_tts(
            scenes,
            output_dir=args.output_dir,
            voice=edge_voice,
            sample_rate=args.sample_rate,
            tail_pad_sec=args.tail_pad,
        )

    data["tts_engine"] = args.engine
    data["tts_voice"] = args.voice
    data["audio_sample_rate_hz"] = args.sample_rate
    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Completed 48 kHz expressive synthesis & clean subtitle extraction for {len(scenes)} scenes -> {args.manifest}")


if __name__ == "__main__":
    main()
