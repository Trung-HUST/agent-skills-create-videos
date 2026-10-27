#!/usr/bin/env python3
"""
generate_soundscape.py
Generates an organic Dark Academia / Documentary Ambient Soundtrack (warm analog cello/rhodes chords,
subtle vinyl/room atmosphere, and gentle low-pass warmth) to mix underneath voiceover narration so
the final video sounds like a human-produced studio documentary essay.
"""
import argparse
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter


def lowpass(data: np.ndarray, cutoff: float, fs: int, order: int = 4) -> np.ndarray:
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return lfilter(b, a, data)


def synthesize_documentary_bgm(duration_sec: float, out_path: Path, sr: int = 44100) -> Path:
    total_samples = int((duration_sec + 4.0) * sr)
    t = np.linspace(0, duration_sec + 4.0, total_samples, endpoint=False)

    # Warm minor-key documentary chord progression (D minor 9 -> Bb major 7 -> G minor 7 -> A7sus4)
    # Frequencies in low-mid cello / warm analog pad register
    chords = [
        [146.83, 174.61, 220.00, 261.63, 329.63],  # Dm9
        [116.54, 174.61, 220.00, 293.66, 349.23],  # Bbmaj7
        [98.00, 146.83, 174.61, 220.00, 293.66],   # Gm7
        [110.00, 164.81, 196.00, 220.00, 277.18],  # A7sus4/A7
    ]

    chord_len_sec = 8.0
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    num_blocks = int(np.ceil((duration_sec + 4.0) / chord_len_sec))
    block_samples = int(chord_len_sec * sr)

    for b_idx in range(num_blocks):
        start = b_idx * block_samples
        end = min(total_samples, start + block_samples)
        seg_len = end - start
        if seg_len <= 0:
            break
        seg_t = np.linspace(0, seg_len / sr, seg_len, endpoint=False)
        freqs = chords[b_idx % len(chords)]

        # Smooth swell envelope per chord
        env = np.sin(np.pi * seg_t / (seg_len / sr)) ** 1.4

        sig_l = np.zeros(seg_len, dtype=np.float32)
        sig_r = np.zeros(seg_len, dtype=np.float32)

        for i, f in enumerate(freqs):
            detune_l = f * (1.0 - 0.0015 * (i % 2))
            detune_r = f * (1.0 + 0.0018 * ((i + 1) % 2))
            # Fundamental + warm 2nd harmonic
            wave_l = 0.65 * np.sin(2 * np.pi * detune_l * seg_t) + 0.20 * np.sin(4 * np.pi * detune_l * seg_t)
            wave_r = 0.65 * np.sin(2 * np.pi * detune_r * seg_t + 0.4) + 0.20 * np.sin(4 * np.pi * detune_r * seg_t + 0.4)
            sig_l += wave_l / len(freqs)
            sig_r += wave_r / len(freqs)

        # Gentle sub-bass pulse on chord attack
        sub_env = np.exp(-seg_t * 1.8)
        sub_freq = freqs[0] * 0.5
        sub_wave = 0.35 * np.sin(2 * np.pi * sub_freq * seg_t) * sub_env

        left[start:end] += (sig_l * env + sub_wave)
        right[start:end] += (sig_r * env + sub_wave)

    # Subtle warm room tone (filtered pink/brown noise) so audio never sounds dead-digital
    rng = np.random.default_rng(42)
    room_l = lowpass(rng.normal(0, 0.012, total_samples).astype(np.float32), 420.0, sr)
    room_r = lowpass(rng.normal(0, 0.012, total_samples).astype(np.float32), 420.0, sr)

    left = lowpass(left, 1100.0, sr) + room_l
    right = lowpass(right, 1100.0, sr) + room_r

    # Master fade-in (2s) and fade-out (3s)
    fade_in = min(int(2.0 * sr), total_samples // 4)
    fade_out = min(int(3.0 * sr), total_samples // 4)
    left[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    right[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    left[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)
    right[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

    stereo = np.stack([left, right], axis=1)
    peak = np.max(np.abs(stereo)) or 1.0
    stereo = (stereo / peak) * 0.45

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), stereo, sr)
    print(f"[SOUNDSCAPE] Generated documentary BGM ({duration_sec:.1f}s) -> {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate documentary ambient BGM soundtrack")
    parser.add_argument("--duration", type=float, default=180.0, help="Duration in seconds")
    parser.add_argument("--output", type=Path, default=Path("assets/music/documentary_bgm.wav"), help="Output WAV path")
    args = parser.parse_args()
    synthesize_documentary_bgm(args.duration, args.output)


if __name__ == "__main__":
    main()
