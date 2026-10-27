---
name: video-script-scene-brain
description: AI Scriptwriting & Scene Breakdown Brain — transforms topics or ideas into high-retention video scripts and structured JSON scene manifests (scenes.json) with hooks, narration, visual prompts, camera motion, and timing cues.
when_to_use: "When the user asks to write a video script, break a topic into scenes, create a storyboard/beat graph, plan a TikTok/Reels/YouTube Short or long-form explainer video, or prepare a scenes.json manifest for automated video production."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Video Script & Scene Breakdown Brain (Bộ Não Viết Kịch Bản & Chia Scene)

> **Single Source of Truth for Downstream Video Production.** Every great AI video starts with a tightly structured script and deterministic `scenes.json` manifest that locks narration, visual continuity, camera motion, and pacing before any TTS or image generation runs.

---

## Overview

Inspired by leading open-source pipelines (**ShortGPT**, **MoneyPrinterTurbo**, **Remotion Director**, and **Video-Skills-Toolkit**), this skill acts as the **Director & Scriptwriter Brain**:
1. **Crafts high-retention scripts** with pattern-interrupt hooks, curiosity loops, evidence/value progression, and a clear payoff.
2. **Decomposes scripts into atomic visual scenes** (typically 3–6 seconds per scene for short-form, 5–10 seconds for long-form) to prevent "static PPT fatigue".
3. **Outputs a standardized `scenes.json` contract** consumed directly by:
   - `scene-image-generator` (Module 2: Scene Illustration)
   - `voice-ai-tts` (Module 3: Voice AI / TTS)
   - `auto-subtitle-video-editor` (Module 4: Auto Subtitles & Video Assembly)

---

## Protocol

### Step 1: Narrative & Retention Architecture

Before splitting into scenes, lock the 4 narrative pillars:
1. **The 3-Second Hook (`hook`)**:
   - Never start with "Hello guys, today we will talk about...".
   - Start with a **Pattern Interrupt**, **Counter-Intuitive Fact**, **High-Stakes Question**, or **Visual Proof**.
2. **The Value / Tension Escalation (`setup` → `escalation` → `proof`)**:
   - Every 10–15 seconds must introduce a "But / Therefore" pivot rather than "And then" lists.
3. **Prosody-Ready Narration (`narration_text`)**:
   - Write for the **ear**, not the eye.
   - Short clauses (8–15 words). Use commas `,` for micro-pauses (0.2s) and periods/ellipses `...` for dramatic beats.
   - Spell out numbers or ambiguous abbreviations so TTS engines (`edge-tts`, `Kokoro`, `F5-TTS`, `VietTTS`) pronounce them naturally.
4. **Visual Continuity Anchor (`style_bible` & `character_anchor`)**:
   - Define a global `style_prompt` (e.g., `"cinematic 35mm photography, moody cyberpunk neon lighting, shallow depth of field, 8k"` or `"2D flat vector explainer illustration, warm pastel palette, clean lines"`) and optional `character_anchor` so every scene looks like it belongs to the same film.

---

### Step 2: Scene Breakdown Rules (Anti-PPT Gate)

| Rule | Short-Form (TikTok / Reels / Shorts) | Long-Form (YouTube 16:9) |
| :--- | :--- | :--- |
| **Aspect Ratio** | `9:16` (`1080x1920`) | `16:9` (`1920x1080`) |
| **Scene Duration** | `2.5s – 5.0s` per scene (10–20 words VO) | `4.0s – 8.0s` per scene (15–35 words VO) |
| **Camera Motion** | Alternate `zoom_in`, `zoom_out`, `pan_left`, `pan_right` | Subtle `zoom_in_slow`, `pan_right`, `static_focus` |
| **Subtitle Safe Zone** | Keep main subject in upper/middle 65% of frame | Keep bottom 18% clear for lower-thirds/subtitles |

---

### Step 3: Standardized `scenes.json` Schema

Always write the breakdown to `scenes.json` (or `workspace/scenes.json`) following this exact schema:

```json
{
  "project_title": "Why 90% of AI Agents Fail in Production",
  "language": "vi",
  "aspect_ratio": "9:16",
  "resolution": {
    "width": 1080,
    "height": 1920
  },
  "fps": 30,
  "voice_config": {
    "engine": "edge-tts",
    "voice_id": "vi-VN-NamMinhNeural",
    "rate": "+5%",
    "pitch": "+0Hz"
  },
  "style_bible": {
    "model_family": "flux",
    "global_style_prompt": "cinematic sci-fi concept art, dramatic volumetric lighting, rich contrast, Unreal Engine 5 render style, high detail",
    "negative_prompt": "text, watermark, blurry, deformed hands, extra fingers, low quality, cropped head",
    "character_anchor": "a young software architect wearing round glasses and a dark hoodie"
  },
  "scenes": [
    {
      "scene_id": 1,
      "beat_type": "hook",
      "narration_text": "Bạn có biết 90 phần trăm các dự án AI Agent sập ngay trong tuần đầu tiên chạy thật không?",
      "visual_prompt": "A glowing holographic AI brain shattering into digital fragments inside a dark server room, dramatic red alert rim lighting, wide angle shot",
      "camera_motion": "zoom_in_fast",
      "transition": "fade",
      "overlay_text": "90% AI AGENT THẤT BẠI?!",
      "sfx_cue": "whoosh_impact",
      "estimated_duration_sec": 4.2
    },
    {
      "scene_id": 2,
      "beat_type": "setup",
      "narration_text": "Lý do không phải vì mô hình yếu, mà vì thiếu một bộ khung điều phối kỹ năng và bộ nhớ chuẩn chỉnh.",
      "visual_prompt": "A young software architect wearing round glasses and a dark hoodie looking at a tangled web of glowing red wires on a transparent monitor, moody blue studio lighting",
      "camera_motion": "pan_right",
      "transition": "crossfade",
      "overlay_text": "Thiếu Orchestration & Memory",
      "sfx_cue": "digital_glitch",
      "estimated_duration_sec": 4.8
    }
  ]
}
```

---

### Step 4: Validate & Scaffold with CLI Script

Run the built-in validator and manifest generator script to verify `scenes.json` before passing it to image or audio generation:

```bash
python .agents/skills/video-script-scene-brain/scripts/generate_scene_manifest.py --validate scenes.json
```

Or generate a starter `scenes.json` from a plain-text script file:

```bash
python .agents/skills/video-script-scene-brain/scripts/generate_scene_manifest.py --from-text script.txt --lang vi --aspect 9:16 --output scenes.json
```

---

## Companion Skills

- For deep Beat Graph & Director Treatment on existing voiceovers: read `.agents/skills/video-script/SKILL.md`
- For viral short-form hook formulas: read `.agents/skills/hook-writing/SKILL.md`
- Next step in pipeline: `.agents/skills/scene-image-generator/SKILL.md` & `.agents/skills/voice-ai-tts/SKILL.md`
