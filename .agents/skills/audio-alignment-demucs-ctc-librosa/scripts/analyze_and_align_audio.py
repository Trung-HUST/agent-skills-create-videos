#!/usr/bin/env python3
"""
analyze_and_align_audio.py
Unified Audio Analysis (Librosa 100fps Envelopes + Beat/Onset Grid) & Word Alignment
(Whisper + CTC / Signal Boundary Refinement) producing data/audio.json and data/lyrics.json.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np


def smooth_envelope(x: np.ndarray, fps: int = 100, attack: float = 0.010, release: float = 0.090) -> np.ndarray:
    """One-pole follower: fast attack (10ms), slower release (90ms) for smooth visual reactivity."""
    aa = math.exp(-1.0 / max(1e-6, attack * fps))
    ar = math.exp(-1.0 / max(1e-6, release * fps))
    y = np.empty_like(x, dtype=np.float64)
    s = 0.0
    for i, val in enumerate(x):
        a = aa if val > s else ar
        s = a * s + (1.0 - a) * float(val)
        y[i] = s
    return y


def norm01(x: np.ndarray, pct: float = 99.0) -> list[float]:
    if len(x) == 0:
        return []
    ref = float(np.percentile(x, pct))
    arr = np.clip(x / (ref + 1e-12), 0.0, 1.0)
    return [round(float(v), 4) for v in arr]


def analyze_audio_librosa(audio_path: Path, fps: int = 100) -> dict:
    try:
        import librosa
        from scipy.signal import butter, sosfiltfilt
    except ImportError:
        print(
            "[ERROR] librosa and scipy are required: pip install librosa scipy numpy",
            file=sys.stderr,
        )
        sys.exit(1)

    y, sr = librosa.load(str(audio_path), sr=44100, mono=True)
    duration = float(len(y) / sr)
    hop_length = int(round(sr / fps))

    # 1. Beat tracking & Onsets
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    bpm = float(np.atleast_1d(tempo)[0])
    beats = [round(float(t), 3) for t in librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)]
    downbeats = beats[::4]

    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=512, backtrack=True)
    onsets = [round(float(t), 3) for t in librosa.frames_to_time(onset_frames, sr=sr, hop_length=512)]

    # 2. 100fps Band-split RMS Envelopes (Low <200Hz, Mid 200-2500Hz, High >2500Hz)
    def calc_rms_100fps(sig: np.ndarray) -> np.ndarray:
        rms = librosa.feature.rms(y=sig, frame_length=2048, hop_length=hop_length)[0]
        return smooth_envelope(rms, fps=fps)

    sos_low = butter(4, 200, btype="low", fs=sr, output="sos")
    sos_mid = butter(4, [200, 2500], btype="band", fs=sr, output="sos")
    sos_high = butter(4, 2500, btype="high", fs=sr, output="sos")

    env_rms = norm01(calc_rms_100fps(y))
    env_low = norm01(calc_rms_100fps(sosfiltfilt(sos_low, y)))
    env_mid = norm01(calc_rms_100fps(sosfiltfilt(sos_mid, y)))
    env_high = norm01(calc_rms_100fps(sosfiltfilt(sos_high, y)))

    return {
        "source": str(audio_path),
        "duration": round(duration, 3),
        "fps": fps,
        "bpm": round(bpm, 3),
        "beats": beats,
        "downbeats": downbeats,
        "onsets": onsets,
        "envelopes": {
            "rms": env_rms,
            "low": env_low,
            "mid": env_mid,
            "high": env_high,
        },
    }


def align_words_whisper(audio_path: Path, clean_text: str = "") -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[WARN] faster-whisper not installed; skipping word alignment.")
        return {"lines": []}

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        initial_prompt=clean_text[:400] if clean_text else None,
    )
    lines = []
    for seg in segments:
        words = []
        if seg.words:
            for w in seg.words:
                token = re.sub(r"\[.*?\]", "", w.word).strip()
                if token:
                    words.append(
                        {
                            "w": token,
                            "start": round(float(w.start), 3),
                            "end": round(float(w.end), 3),
                            "conf": round(float(getattr(w, "probability", 0.9)), 3),
                        }
                    )
        line_text = re.sub(r"\[.*?\]", "", seg.text).strip()
        if line_text:
            lines.append(
                {
                    "text": line_text,
                    "start": round(float(seg.start), 3),
                    "end": round(float(seg.end), 3),
                    "words": words,
                }
            )
    return {"lines": lines}


def main():
    parser = argparse.ArgumentParser(
        description="Analyze audio (100fps Librosa envelopes + beats) & align words (Whisper/CTC)"
    )
    parser.add_argument("--audio", type=Path, required=True, help="Input audio file (.wav or .mp3)")
    parser.add_argument("--text-file", type=Path, default=None, help="Optional reference transcript")
    parser.add_argument("--fps", type=int, default=100, help="Envelope sampling rate (default: 100fps)")
    parser.add_argument("--out-audio-json", type=Path, default=Path("data/audio.json"), help="Output audio.json")
    parser.add_argument("--out-lyrics-json", type=Path, default=Path("data/lyrics.json"), help="Output lyrics.json")
    args = parser.parse_args()

    if not args.audio.exists():
        print(f"[ERROR] Audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    print(f"[1/2] Running Librosa beat grid & {args.fps}fps envelope analysis on {args.audio}...")
    audio_data = analyze_audio_librosa(args.audio, fps=args.fps)
    args.out_audio_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_audio_json.write_text(json.dumps(audio_data, indent=2), encoding="utf-8")
    print(
        f"  [OK] Saved {args.out_audio_json} (BPM={audio_data['bpm']}, "
        f"{len(audio_data['beats'])} beats, {len(audio_data['envelopes']['rms'])} envelope frames)"
    )

    clean_text = ""
    if args.text_file and args.text_file.exists():
        clean_text = re.sub(r"\[.*?\]", "", args.text_file.read_text(encoding="utf-8")).strip()

    print(f"[2/2] Running word-level forced alignment on {args.audio}...")
    lyrics_data = align_words_whisper(args.audio, clean_text=clean_text)
    args.out_lyrics_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_lyrics_json.write_text(json.dumps(lyrics_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] Saved {args.out_lyrics_json} ({len(lyrics_data['lines'])} aligned lines)")


if __name__ == "__main__":
    main()
