---
name: auto-subtitle-video-editor
description: Automated Subtitle Generation & Programmatic Video Editing Engine — generates word-level/phrase-level SRT & styled ASS captions (via faster-whisper, WhisperX, or manifest sync) and renders complete videos with Ken Burns camera motion, transitions, BGM ducking, and burned-in captions using FFmpeg, MoviePy, or Remotion.
when_to_use: "When the user asks to generate subtitles/captions (SRT/ASS) from audio, add TikTok/CapCut/Reels style burned-in captions, stitch scene images and TTS voiceovers into a complete video, apply Ken Burns zoom/pan effects, mix background music with ducking, or render programmatic videos with FFmpeg/Remotion."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Auto Subtitle & Video Editor (Tạo Phụ Đề & Dựng Video Tự Động)

> **Deterministic Post-Production & Assembly.** Transforms generated scene illustrations (`assets/scenes/*.png`) and per-scene voiceovers (`assets/audio/*.mp3`) into a polished, platform-ready `.mp4` with dynamic camera motion, synchronized burned-in subtitles, and broadcast loudness normalization.

---

## Open-Source Stack Architecture

| Layer | Open-Source Tools | Role |
| :--- | :--- | :--- |
| **Speech-to-Subtitle (ASR)** | `faster-whisper` (`SYSTRAN`), `WhisperX` (`m-bain/whisperX`) | Word-level forced alignment & timestamp extraction |
| **Styled Captions** | `ASS (Advanced SubStation Alpha)` / `@remotion/captions` | High-contrast CapCut/TikTok typography, outlines, safe zones |
| **Motion & Assembly** | `FFmpeg` (`zoompan`, `xfade`, `subtitles`/`ass`, `loudnorm`) | Ken Burns camera movement, scene stitching, audio mixing |
| **Programmatic UI Video** | `Remotion` (`remotion-dev/remotion`) / `MoviePy` | React-driven motion graphics & kinetic typography |

---

## Protocol

### Step 1: Generate Synchronized Subtitles (`.srt` & Styled `.ass`)

Generate both standard `.srt` and styled `.ass` subtitles aligned to the exact audio durations in `scenes.json`:

```bash
# Mode 1: Deterministic sync from scenes.json + exact ffprobe audio durations (0 GPU, instant)
python .agents/skills/auto-subtitle-video-editor/scripts/generate_subtitles.py \
  --manifest scenes.json \
  --mode manifest \
  --max-words-per-line 6 \
  --output-dir assets/subtitles

# Mode 2: Faster-Whisper word-level ASR alignment (requires pip install faster-whisper)
python .agents/skills/auto-subtitle-video-editor/scripts/generate_subtitles.py \
  --manifest scenes.json \
  --mode whisper \
  --whisper-model base \
  --output-dir assets/subtitles
```

---

### Step 2: Automated Video Rendering (Ken Burns + Audio Sync + Subtitle Burn-in + BGM)

Run `assemble_video.py` to compile all scenes into the final deliverable `.mp4`:

```bash
python .agents/skills/auto-subtitle-video-editor/scripts/assemble_video.py \
  --manifest scenes.json \
  --subtitles assets/subtitles/captions.ass \
  --output output/final_video.mp4
```

Optional flags:
- `--bgm assets/music/bgm.mp3 --bgm-volume 0.15` — Mix background music under the voiceover.
- `--no-subtitles` — Render clean video without burned-in text.
- `--fast` — Use fast scaling instead of sub-pixel Ken Burns `zoompan` for rapid draft previews.

---

### Step 3: Windows FFmpeg Subtitle Path Rule (Critical Gotcha)

On Windows, FFmpeg's `subtitles=` and `ass=` filters treat `:` as an option separator, which breaks absolute paths like `C:\path\captions.ass`.
- **Always use relative POSIX paths** (e.g., `subtitles=assets/subtitles/captions.ass`) OR escape the drive colon as `C\\:/path/captions.ass`.
- `assemble_video.py` handles this automatically.

---

## Companion Skills (Advanced Editing & Remotion)

- 42 deterministic FFmpeg tools (cutting, silence removal, loudness, LUTs, platform checks): `.agents/skills/ffmpeg-skill/SKILL.md`
- Remotion React programmatic video & animated captions:
  - `.agents/skills/remotion-best-practices/SKILL.md`
  - `.agents/skills/remotion-captions/SKILL.md`
  - `.agents/skills/remotion-create/SKILL.md`
  - `.agents/skills/remotion-render/SKILL.md`
- Audio transcription & subtitle proofreading: `.agents/skills/audio-to-subtitles/SKILL.md`
- Multi-clip FFmpeg/Remotion assembly patterns: `.agents/skills/video-assembly/SKILL.md`
