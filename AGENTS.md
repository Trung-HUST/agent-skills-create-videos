# AGENTS.md

> Workspace entry point for AI coding agents.

## Rule Source Of Truth

- Read [.agents/ARCHITECTURE.md](.agents/ARCHITECTURE.md) first.
- Then read [.agents/rules/GEMINI.md](.agents/rules/GEMINI.md).
- Treat `.agents/` as the authoritative AG Kit bundle for agents, skills, workflows, and memory.

## Loading Policy

- Do not load every skill folder.
- Read a skill's `SKILL.md` only when the task matches its `when_to_use` or description.
- Prefer the smallest relevant agent/skill set for the request.

## Change Policy

- Keep `.agents/` in the workspace so the editor can index it.
- Do not add secret values or environment tokens to committed instructions.
- Use the project verification scripts in `.agents/scripts/` when a task needs final validation.

## Practical Routing

- AI Video Production & Automated Video Pipeline (Priority Domain):
  - Master Orchestrator & Agent: `@[video-producer]` agent, `create-videos` skill (`/create-video` workflow).
  - 1. Bộ não viết kịch bản & chia Scene: `video-script-scene-brain`, `video-script`, `hook-writing`, `viral-video-benchmark`.
  - 2. Tạo ảnh minh họa theo từng Scene: `scene-image-generator`, `comfyui-prompt-engineer`, `comfyui-character-gen`, `comfyui-workflow-builder`, `comfyui-api`, `comfyui-video-pipeline`, `comfyui-video-production`.
  - 3. Tạo giọng đọc (Voice AI / TTS): `voice-ai-tts` (Edge-TTS, Kokoro-82M, F5-TTS, Chatterbox, Piper), `comfyui-voice-pipeline`, `minimax-voice-director`.
  - 4. Tạo phụ đề & Dựng video tự động: `auto-subtitle-video-editor` (faster-whisper, WhisperX, ASS/SRT burn-in, Ken Burns FFmpeg), `ffmpeg-skill` (42 tools), `video-assembly`, `audio-to-subtitles`, `remotion-best-practices`, `remotion-captions`, `remotion-create`, `remotion-render`.
- Web UI and React work:
  - Design & Architecture: `ui-ux-pro-max`, `frontend-ui-engineering` (no generic AI aesthetic), `web-design-guidelines`.
  - Component & Styling: `shadcn-ui`, `ui-styling`, `composition-patterns`, `css-animation-patterns`, `ui-ux-polish`.
  - Performance & React 19: `react-best-practices`, `react-view-transitions`.
- Pixel Art & 2D Game Assets:
  - Deterministic & Code-drawn Pixel Art: `pixel-art-studio` (Pillow-based, ramps, dithering, outlines, preview & critique loop).
  - AI Generation & Sprite Sheet Pipeline: `generate2dsprite`, `generate2dmap`, `create-game-assets` (chroma-key cleanup, transparent frames, engine atlas).
  - Retro & Procedural: `generating-dot-assets`, `directing-game-visuals`.
- API, data, and sync work: prefer backend/database-oriented skills.
- Testing and debugging: prefer the matching testing or systematic-debugging skills.
- Game Development work (FPS, Shooter, Godot, Unreal, Unity, Shaders, Game AI, Studio Design):
  - Consult `gamedev-router` or the detected engine/genre skill (`fps-shooter`, `game-feel`, `game-ai`, `shader-programming`).
  - For studio structure and production gates (GDD, balance check, architecture decisions), activate CCGS specialist agents and workflow skills (`balance-check`, `art-bible`, `asset-audit`).
  - For gameplay invariants, procedural audio, and game verification, consult the `aba-*` verification skills.



