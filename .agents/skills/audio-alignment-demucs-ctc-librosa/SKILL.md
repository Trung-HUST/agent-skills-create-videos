---
name: audio-alignment-demucs-ctc-librosa
description: High-Precision Audio Analysis & Forced Alignment Pipeline (Demucs + CTC Forced Alignment + Whisper + Librosa) — separates vocal/drum/bass stems, performs sub-10ms word/syllable CTC Viterbi forced alignment cross-checked with Whisper, and extracts 100fps RMS/frequency envelopes, BPM beat grids, downbeats, and kick/snare/vocal onsets.
when_to_use: "When the user mentions Demucs, CTC forced alignment, Librosa beat/envelope analysis, word-level/syllable-level lyric or narration sync, pdoom-video audio analysis, audio-reactive shaders/animations, or sub-frame subtitle/karaoke alignment."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Audio Analysis & Forced Alignment (`Demucs + CTC Forced Alignment + Whisper + Librosa`)

> **Sub-10ms Word & Beat Synchronization.** Plain ASR timestamps drift on music, held vowels, or expressive speech. By separating the clean vocal stem with **Demucs**, running **CTC Forced Alignment (`MMS_FA` / `wav2vec2`)** cross-checked with **Whisper**, snapping word boundaries to **spectral-flux vocal onsets**, and extracting **100fps Librosa envelopes**, every visual beat and kinetic word lands on the exact millisecond.

---

## 4-Stage Signal & Alignment Architecture (from `mexicat/pdoom-video`)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. DEMUCS STEM SEPARATION (`htdemucs_ft`)                                    │
│    audio.mp3 ──▶ vocals.wav | drums.wav | bass.wav | other.wav               │
│          │                                                                   │
│          ├──▶ 2. CTC FORCED ALIGNMENT + WHISPER CROSS-CHECK                  │
│          │       MMS_FA + wav2vec2 LV60K Viterbi + Onset Snap ──▶ lyrics.json│
│          │                                                                   │
│          └──▶ 3. LIBROSA + SCIPY BEAT & ENVELOPE EXTRACTION (`100 fps`)      │
│                  BPM Grid + Downbeats + Kick/Snare/Vocal Onsets              │
│                  + One-Pole Attack/Release Envelopes ──▶ audio.json          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Protocol

### Step 1: Stem Separation with Demucs (`htdemucs_ft`)

Isolate the vocal stem (for clean forced alignment without BGM bleed) and the drum/bass stems (for beat-grid fitting and audio-reactive visuals):

```bash
python -m demucs -n htdemucs_ft -o assets/stems input_audio.mp3
```

---

### Step 2: CTC Forced Alignment + Whisper + Signal Refinement (`lyrics.json`)

Why fuse CTC + Whisper + Signal Envelopes?
1. **CTC Viterbi Pass (`torchaudio.pipelines.MMS_FA` / `WAV2VEC2_ASR_LARGE_LV60K_960H`)**: Forces alignment against the known ground-truth script/lyrics so zero words are hallucinated or misspelled.
2. **Whisper Cross-Check (`faster-whisper` / `mlx-whisper large-v3-turbo`)**: Verifies macro line windows and flags low-confidence regions.
3. **Signal-Based Boundary Refinement (`refine()` in `references/align.py`)**:
   - **Rest-Onset Rule**: When ≥50ms silence precedes a word and voice RMS re-enters >40ms before the first CTC token (common on held vowels), snap the word start to the true vocal entry.
   - **Spectral-Flux Onset Snap**: Snaps legato vowel/glottal word starts to the local spectral-flux onset peak.
   - **Fricative Tail Extension**: Extends words ending in `/s, z, f, sh, ch/` until high-band (`3–10 kHz`) fricative energy drops.

---

### Step 3: Librosa 100fps Envelopes & Beat Grid (`audio.json`)

Extracted by `scripts/analyze_and_align_audio.py` (and `references/analyze.py`):
- **100 fps Normalized Envelopes (`0.0 .. 1.0`)** smoothed with a visual-friendly one-pole follower (`attack = 10ms`, `release = 90ms`):
  - `rms` (full mix), `low` (`<200 Hz`), `mid` (`200–2500 Hz`), `high` (`>2500 Hz`), `vocal`, `drums`, `bass`.
- **Beat Grid & Onsets**:
  - `bpm`, `beats[]`, `downbeats[]`, `kick[]`, `snare[]`, `hat[]`, `vocal_onsets[]`.

---

## CLI Execution

Run the unified analyzer & aligner script on any voiceover or song file:

```bash
python .agents/skills/audio-alignment-demucs-ctc-librosa/scripts/analyze_and_align_audio.py \
  --audio assets/audio/merged.wav \
  --text-file script.txt \
  --out-audio-json data/audio.json \
  --out-lyrics-json data/lyrics.json
```

---

## Reference Implementations Included

- Full multi-model CTC + Whisper + Spectral-Flux refiner: `.agents/skills/audio-alignment-demucs-ctc-librosa/references/align.py`
- Full Librosa + Butterworth band-split + 100fps one-pole envelope analyzer: `.agents/skills/audio-alignment-demucs-ctc-librosa/references/analyze.py`
- CTC Viterbi aligner core: `.agents/skills/audio-alignment-demucs-ctc-librosa/references/ctcalign.py`
