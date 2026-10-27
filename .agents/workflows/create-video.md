---
description: End-to-end automated AI video creation workflow — from topic/script to scene breakdown, AI illustration generation, TTS voiceover, auto subtitles, and final MP4 rendering.
---

# /create-video — Automated AI Video Production Workflow

Activate `@[video-producer]` and execute the 4-stage pipeline in `.agents/skills/create-videos/SKILL.md`:

1. **Stage 1 — Script & Scene Breakdown (`video-script-scene-brain`)**:
   - Design hook, narration, visual style bible, and scene breakdown.
   - Write and validate `scenes.json`:
     ```bash
     python .agents/skills/video-script-scene-brain/scripts/generate_scene_manifest.py --validate scenes.json
     ```
2. **Stage 2 — Scene Illustration Generation (`scene-image-generator`)**:
   - Generate consistent scene images (`assets/scenes/scene_001.png`, ...):
     ```bash
     python .agents/skills/scene-image-generator/scripts/generate_scene_images.py --manifest scenes.json --engine pollinations
     ```
3. **Stage 3 — Voice AI / TTS Synthesis (`voice-ai-tts`)**:
   - Generate per-scene voiceover audio and lock exact `ffprobe` durations:
     ```bash
     python .agents/skills/voice-ai-tts/scripts/generate_tts_scenes.py --manifest scenes.json --engine edge-tts
     ```
4. **Stage 4 — Auto Subtitles & Video Assembly (`auto-subtitle-video-editor`)**:
   - Generate `.srt` and styled `.ass` captions and render the final `.mp4`:
     ```bash
     python .agents/skills/auto-subtitle-video-editor/scripts/generate_subtitles.py --manifest scenes.json --mode manifest
     python .agents/skills/auto-subtitle-video-editor/scripts/assemble_video.py --manifest scenes.json --output output/final_video.mp4
     ```
