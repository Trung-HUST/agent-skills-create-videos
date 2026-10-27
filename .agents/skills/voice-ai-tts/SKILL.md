---
name: voice-ai-tts
description: Voice AI & Text-to-Speech (TTS) Engine — synthesizes natural scene-by-scene voiceovers and word-level timing cues using top open-source TTS engines (Edge-TTS, Kokoro-82M, F5-TTS zero-shot voice cloning, Chatterbox, VietTTS, Piper) and measures exact audio durations for lockstep video sync.
when_to_use: "When the user asks to generate AI voiceovers, convert script scenes to speech (TTS), clone voices with F5-TTS/Chatterbox, generate Vietnamese or English narration audio, or synchronize scene durations with spoken audio."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Voice AI & TTS Engine (Tạo Giọng Đọc AI / Text-to-Speech)

> **Audio-Driven Timeline Architecture.** In professional automated video production, **audio duration dictates video duration**. Generating voiceover per scene (`scene_001.mp3`, ...) and measuring its exact length via `ffprobe` guarantees 100% lip/subtitle/scene synchronization with zero cumulative drift.

---

## Top Open-Source TTS Engines Selection Matrix

| Engine | GitHub / Package | Vietnamese (`vi`) | Voice Cloning | GPU Needed? | Best Use Case |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Edge-TTS** | `rany2/edge-tts` (`pip install edge-tts`) | ⭐ Native (`HoaiMy`, `NamMinh`) | No | ❌ No (0 VRAM) | Fast, free, natural Vietnamese & multilingual neural voices + word boundary timings |
| **Kokoro-82M** | `hexgrad/Kokoro-82M` (`kokoro-onnx`) | English / Multi | Preset Mixing | ❌ Runs fast on CPU | Best Apache-2.0 local open-weight TTS for English/Multilingual |
| **F5-TTS** | `SWivid/F5-TTS` (`f5-tts` / `EraX-Vi-F5`) | ⭐ With Vi Checkpoint | ✅ Zero-shot (<15s) | ✅ Recommended | Expressive zero-shot voice cloning from a 10s `.wav` sample |
| **Chatterbox** | `resemble-ai/chatterbox` | Multilingual | ✅ Zero-shot (5s) | ✅ Yes | Emotion tags (`[laugh]`, `[sigh]`, `[whisper]`) & exaggeration control |
| **Piper TTS** | `rhasspy/piper` (`piper-tts`) | ✅ Yes (`vi_VN`) | No | ❌ Ultra-fast CPU | 100% offline lightweight ONNX synthesis |

---

## Protocol

### Step 1: Recommended Voice IDs (Edge-TTS Default)

- **Vietnamese (Tiếng Việt)**:
  - Female (Warm, clear storytelling/explainer): `vi-VN-HoaiMyNeural`
  - Male (Deep, authoritative tech/documentary): `vi-VN-NamMinhNeural`
- **English**:
  - Male (Narrator / Documentary): `en-US-ChristopherNeural`, `en-US-GuyNeural`, `en-US-BrianNeural`
  - Female (Engaging / Short-form): `en-US-AriaNeural`, `en-US-avaNeural`

---

### Step 2: Generate Per-Scene Audio & Measure Exact Duration

Never estimate scene video length by character count when rendering the final video. Always synthesize each scene's narration first, then probe its true duration:

```bash
# Install edge-tts if not present
pip install edge-tts

# Synthesize all scenes in scenes.json and record exact durations + word boundaries
python .agents/skills/voice-ai-tts/scripts/generate_tts_scenes.py \
  --manifest scenes.json \
  --engine edge-tts \
  --voice vi-VN-NamMinhNeural \
  --output-dir assets/audio
```

### Step 3: Zero-Shot Voice Cloning with F5-TTS (Optional Local GPU)

When the user provides a reference voice sample (`reference_voice.wav` + transcript):

```bash
python .agents/skills/voice-ai-tts/scripts/generate_tts_scenes.py \
  --manifest scenes.json \
  --engine f5-tts \
  --ref-audio assets/voice_ref.wav \
  --ref-text "Nội dung văn bản khớp chính xác với file ghi âm mẫu." \
  --output-dir assets/audio
```

---

## What `generate_tts_scenes.py` Produces

For every scene `N` in `scenes.json`:
1. `assets/audio/scene_00N.mp3` — Clean synthesized voiceover.
2. `assets/audio/scene_00N.vtt` — Word/phrase timing metadata emitted directly during synthesis.
3. Updates `scenes.json` with:
   - `"audio_path": "assets/audio/scene_001.mp3"`
   - `"subtitle_vtt_path": "assets/audio/scene_001.vtt"`
   - `"audio_duration_sec": 4.62` (measured via `ffprobe`)

---

## Companion Skills

- Deep ComfyUI Voice Cloning (Chatterbox, RVC, IndexTTS-2, Wav2Lip, LivePortrait): `.agents/skills/comfyui-voice-pipeline/SKILL.md`
- Voice Audition & Direction: `.agents/skills/minimax-voice-director/SKILL.md`
- Next step in pipeline: `.agents/skills/auto-subtitle-video-editor/SKILL.md`
