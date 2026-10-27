# agent-skills-create-videos

> **Enterprise AI Video Production & Agent Skills Toolkit (AG Kit — Video Edition)**
> Bộ kỹ năng chuẩn hóa cho **Antigravity**, **Claude Code**, **Cursor**, **Copilot**, và **Codex** chuyên biệt hóa cho quy trình **Sản xuất Video AI Tự Động 4 Giai Đoạn (4-Stage Automated Video Pipeline)** kết hợp cùng hệ sinh thái 290+ Agent Skills.

---

## ⚡ Quick Start

Cài đặt trực tiếp bộ `.agents/` (bao gồm đầy đủ Video Production Skills, Specialist Agents, Memory & Rules) vào bất kỳ dự án nào:

```bash
npx github:Trung-HUST/agent-skills-create-videos
```

Hoặc clone trực tiếp:

```bash
git clone https://github.com/Trung-HUST/agent-skills-create-videos.git
```

---

## 🎬 Kiến Trúc 4 Giai Đoạn Sản Xuất Video Tự Động (`create-videos`)

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ 1. BỘ NÃO KỊCH BẢN & CHIA SCENE (`video-script-scene-brain`)                   │
│    Topic / Idea ──▶ Hook 3s + Narration + Style Bible ──▶ scenes.json          │
│          │                                                                     │
│          ├──▶ 2. TẠO ẢNH THEO SCENE (`scene-image-generator`)                  │
│          │       ComfyUI / FLUX.1 / SDXL / Pollinations ──▶ scene_00N.png      │
│          │                                                                     │
│          └──▶ 3. TẠO GIỌNG ĐỌC AI / TTS (`voice-ai-tts`)                       │
│                  Edge-TTS (Vi/En) / Kokoro-82M / F5-TTS ──▶ scene_00N.mp3      │
│                         │                                                      │
│                         ▼                                                      │
│ 4. TẠO PHỤ ĐỀ & DỰNG VIDEO TỰ ĐỘNG (`auto-subtitle-video-editor`)              │
│    Faster-Whisper / ASS Styled Captions + Ken Burns Zoom + FFmpeg ──▶ .mp4     │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 🧩 Danh Sách 26 Skills Sản Xuất Video Đã Tích Hợp (`.agents/skills/`)

| Nhóm Chức Năng | Skills Chính (Flagship) | Skills Open-Source Tích Hợp Cùng |
| :--- | :--- | :--- |
| **Master Orchestrator** | **`create-videos`** (+ Agent `@[video-producer]`, Workflow `/create-video`) | Điều phối toàn trình từ ý tưởng/sách đến file `.mp4` hoàn chỉnh |
| **1. Bộ não viết kịch bản, Phân tích sách & chia Scene** | **`video-script-scene-brain`** (`generate_scene_manifest.py`), **`book-analysis-script`** (`book_to_video_scenes.py`) | `book-to-skill` (`virgiliojr94/book-to-skill` — PDF/EPUB/DOCX parser), `video-script` (Director Layer & Beat Graph), `hook-writing`, `viral-video-benchmark` |
| **2. Tạo ảnh minh họa theo từng Scene** | **`scene-image-generator`** (`generate_scene_images.py`) | `comfyui-prompt-engineer`, `comfyui-character-gen`, `comfyui-workflow-builder`, `comfyui-api`, `comfyui-video-pipeline`, `comfyui-video-production` |
| **3. Tạo giọng đọc (Voice AI / TTS)** | **`voice-ai-tts`** (`generate_tts_scenes.py`) | `comfyui-voice-pipeline` (Chatterbox, F5-TTS, RVC, Wav2Lip, LivePortrait), `minimax-voice-director` |
| **4. Tạo phụ đề & Dựng video tự động** | **`auto-subtitle-video-editor`** (`generate_subtitles.py`, `assemble_video.py`) | `ffmpeg-skill` (42 công cụ FFmpeg), `video-assembly`, `audio-to-subtitles`, `media-to-transcript`, `remotion-best-practices`, `remotion-captions`, `remotion-create`, `remotion-multimedia`, `remotion-render`, `remotion-studio` |

---

## 🚀 Chạy Pipeline Tự Động Bằng CLI

Sau khi Agent tạo file `scenes.json`, có thể chạy toàn bộ 4 bước chỉ với 1 lệnh duy nhất:

```bash
python .agents/skills/create-videos/scripts/run_video_pipeline.py \
  --manifest scenes.json \
  --image-engine pollinations \
  --tts-engine edge-tts \
  --subtitle-mode manifest \
  --output output/final_video.mp4
```

---

## 📄 License

MIT © [Trung-HUST](https://github.com/Trung-HUST)
