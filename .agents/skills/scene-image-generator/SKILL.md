---
name: scene-image-generator
description: Scene Illustration & Visual Asset Generator — generates consistent, high-resolution illustrations for each scene in scenes.json using ComfyUI (FLUX/SDXL), Automatic1111/Forge API, Pollinations Flux API, or OpenAI/Gemini Image APIs with character and style continuity.
when_to_use: "When the user asks to generate images/illustrations for video scenes, create consistent characters across scenes, run batch image generation from a storyboard/scenes.json, or integrate ComfyUI/Flux/SDXL into a video pipeline."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Scene Image Generator (Tạo Ảnh Minh Họa Theo Từng Scene)

> **Visual Consistency Across Every Beat.** Turns each scene in `scenes.json` into a cohesive, resolution-matched visual asset (`assets/scenes/scene_001.png`, ...) ready for Ken Burns camera motion or Image-to-Video (I2V) animation.

---

## Overview

Built on top of open-source visual generation ecosystems (**ComfyUI**, **FLUX.1-dev/schnell**, **SDXL**, **IP-Adapter / PuLID / InstantID**, **Stable Diffusion WebUI Forge**, and **Pollinations Flux Open API**), this skill solves the #1 problem in AI video generation: **visual drift between scenes**.

---

## Protocol

### Step 1: Lock the Style Bible & Character Continuity

Every `scenes.json` must define a `style_bible` block before generating images:
- **Composite Prompt Formula**:
  ```
  {character_anchor}, {scene.visual_prompt}, {style_bible.global_style_prompt}
  ```
- **Model-Specific Prompting**:
  - **FLUX.1 (`flux` / `flux-schnell`)**: Use natural descriptive sentences (50–100 words), CFG `3.5`, no tag spam (`masterpiece, 8k` is unnecessary).
  - **SDXL (`sdxl`)**: Put quality tags (`masterpiece, best quality, photorealistic`) at the start, CFG `7.0`, include `negative_prompt`.
- **Subtitle Safe-Zone Framing**:
  - For vertical videos (`9:16`, `1080x1920`), instruct prompts with `"subject centered in upper two-thirds of frame, clean negative space in lower third"` so burned-in subtitles never obscure faces.

---

### Step 2: Select Generation Backend

| Backend (`--engine`) | Requirements | Best For |
| :--- | :--- | :--- |
| **`comfyui`** | Local ComfyUI running at `http://127.0.0.1:8188` | Full control: FLUX, LoRA, IP-Adapter, PuLID, ControlNet |
| **`sdwebui`** | Automatic1111 / Forge with `--api` (`127.0.0.1:7860`) | Fast local SDXL / SD1.5 batch generation |
| **`pollinations`** | Zero API key, free cloud FLUX endpoint | Instant zero-setup FLUX image generation per scene |
| **`placeholder`** | Local Python (`Pillow` / `ffmpeg`) | Ultra-fast offline layout testing & timing preview |

---

### Step 3: Batch Generate Scene Illustrations via CLI

Run the batch scene image generator script on `scenes.json`:

```bash
# Generate using free Flux API (Pollinations) with locked style bible
python .agents/skills/scene-image-generator/scripts/generate_scene_images.py \
  --manifest scenes.json \
  --engine pollinations \
  --output-dir assets/scenes

# Generate using local ComfyUI API (http://127.0.0.1:8188)
python .agents/skills/scene-image-generator/scripts/generate_scene_images.py \
  --manifest scenes.json \
  --engine comfyui \
  --api-url http://127.0.0.1:8188 \
  --output-dir assets/scenes

# Generate using local SD WebUI / Forge API (http://127.0.0.1:7860)
python .agents/skills/scene-image-generator/scripts/generate_scene_images.py \
  --manifest scenes.json \
  --engine sdwebui \
  --api-url http://127.0.0.1:7860 \
  --output-dir assets/scenes
```

The script automatically:
1. Composes the full prompt (`character_anchor` + `visual_prompt` + `global_style_prompt`).
2. Generates each scene image at the exact target resolution (`1080x1920` or `1920x1080`).
3. Saves `assets/scenes/scene_001.png`, `scene_002.png`, ...
4. Updates `scenes.json` with `"image_path"` for each scene.

---

## Companion Skills (Deep ComfyUI Workflows)

- Prompt optimization for FLUX/SDXL/Wan: `.agents/skills/comfyui-prompt-engineer/SKILL.md`
- Character face & outfit consistency (InstantID/PuLID/LoRA): `.agents/skills/comfyui-character-gen/SKILL.md`
- Custom ComfyUI API workflow JSON building: `.agents/skills/comfyui-workflow-builder/SKILL.md` & `.agents/skills/comfyui-api/SKILL.md`
- Animating scene images into video clips (Wan 2.2 / LTX-2): `.agents/skills/comfyui-video-pipeline/SKILL.md`
