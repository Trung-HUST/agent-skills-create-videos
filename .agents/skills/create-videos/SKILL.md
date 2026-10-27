---
name: create-videos
description: Master End-to-End AI Video Production Orchestrator — combines Scriptwriting & Scene Breakdown Brain, Scene Image Generation (ComfyUI/FLUX/SDXL), Voice AI / TTS (Edge-TTS/Kokoro/F5-TTS), and Auto Subtitles & Video Editing (Whisper/FFmpeg/Remotion) into a single automated pipeline.
when_to_use: "Always activate when the user asks to create a video, build an automated AI video generator, make a TikTok/Reels/YouTube Short or explainer video from a topic/script, or run the 4-stage video production pipeline."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Create Videos — Master 4-Stage AI Video Production Pipeline

> **From Idea to Rendered MP4 in 4 Deterministic Stages.**

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ 1. SCRIPT & SCENE BRAIN  ──▶  scenes.json (Hook, Narration, Visual Prompts)    │
│          │                                                                     │
│          ├──▶ 2. SCENE IMAGE GENERATOR ──▶ assets/scenes/scene_00N.png         │
│          │                                                                     │
│          └──▶ 3. VOICE AI / TTS        ──▶ assets/audio/scene_00N.mp3 + Dur    │
│                         │                                                      │
│                         ▼                                                      │
│ 4. AUTO SUBTITLES & VIDEO EDITOR ──▶ captions.ass + Ken Burns + BGM ──▶ .mp4   │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## The 4 Core Pillars & Specialized Sub-Skills

| Stage | Primary Skill | Companion Open-Source Skills |
| :--- | :--- | :--- |
| **1. Bộ não viết kịch bản & chia Scene** | `video-script-scene-brain` | `video-script`, `hook-writing`, `viral-video-benchmark` |
| **2. Tạo ảnh minh họa theo từng Scene** | `scene-image-generator` | `comfyui-prompt-engineer`, `comfyui-character-gen`, `comfyui-workflow-builder`, `comfyui-api`, `comfyui-video-pipeline`, `comfyui-video-production` |
| **3. Tạo giọng đọc (Voice AI / TTS)** | `voice-ai-tts` | `comfyui-voice-pipeline`, `minimax-voice-director` |
| **4. Tạo phụ đề & Dựng video tự động** | `auto-subtitle-video-editor` | `ffmpeg-skill` (42 tools), `video-assembly`, `audio-to-subtitles`, `media-to-transcript`, `remotion-best-practices`, `remotion-captions`, `remotion-create`, `remotion-render` |

---

## End-to-End Execution Protocol

### Option A: One-Command Full Pipeline Execution

Once `scenes.json` is authored by the agent (following `video-script-scene-brain`), run the master pipeline script to execute Stages 2, 3, and 4 automatically:

```bash
python .agents/skills/create-videos/scripts/run_video_pipeline.py \
  --manifest scenes.json \
  --image-engine pollinations \
  --tts-engine edge-tts \
  --subtitle-mode manifest \
  --output output/final_video.mp4
```

### Option B: Step-by-Step Granular Control

1. **Validate Scene Manifest**:
   ```bash
   python .agents/skills/video-script-scene-brain/scripts/generate_scene_manifest.py --validate scenes.json
   ```
2. **Generate Scene Illustrations**:
   ```bash
   python .agents/skills/scene-image-generator/scripts/generate_scene_images.py --manifest scenes.json --engine pollinations
   ```
3. **Synthesize Voiceover & Lock Durations**:
   ```bash
   python .agents/skills/voice-ai-tts/scripts/generate_tts_scenes.py --manifest scenes.json --engine edge-tts
   ```
4. **Generate Subtitles (`.srt` + `.ass`) & Render Final Video**:
   ```bash
   python .agents/skills/auto-subtitle-video-editor/scripts/generate_subtitles.py --manifest scenes.json --mode manifest
   python .agents/skills/auto-subtitle-video-editor/scripts/assemble_video.py --manifest scenes.json --output output/final_video.mp4
   ```

---

## Quality Gates Before Delivery

- [ ] Every scene in `scenes.json` has a non-empty `narration_text` and `visual_prompt`.
- [ ] `audio_duration_sec` is measured from real synthesized audio (`ffprobe`), never guessed.
- [ ] Subtitles fit within max 2 lines on vertical (`9:16`) videos and stay inside safe margins.
- [ ] Final `.mp4` uses `libx264` (`yuv420p`) and `aac` (`44.1kHz` stereo) for universal playback across TikTok, YouTube Shorts, Reels, and browsers.
