# Memory Index

## Project
- [project] Always create a new dedicated branch for major code changes → project-conventions.md
- [video-pipeline] For any AI video generation task, prioritize `@[video-producer]` and the 4-stage pipeline (`create-videos` -> `video-script-scene-brain` -> `scene-image-generator` -> `voice-ai-tts` -> `auto-subtitle-video-editor`). Always lock `scenes.json` and measure true TTS `audio_duration_sec` via `ffprobe` before rendering video.
