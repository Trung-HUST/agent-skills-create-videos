# Plan: Local AI Video Production Studio (`local-video-studio.md`)

> **Domain**: AI Video Production (`@[video-producer]`) + Local Web Control Studio (`@[frontend-specialist]` & `@[backend-specialist]`)
> **Target Channel**: English Storytelling / Psychology & Knowledge (`16:9` 1920x1080 primary + `9:16` 1080x1920 Shorts toggle)
> **Hardware Profile**: Intel Core i5-14600KF + 32GB RAM + NVIDIA RTX 5060 (8GB VRAM)

---

## 1. System Architecture & Packaging Blueprint

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                   TẦNG 1: BỘ NÃO ĐẠO DIỄN & QC (ANTIGRAVITY AGENT)                   │
│  • Viết kịch bản Tiếng Anh (Storytelling / Psychology) + 3-second Hook               │
│  • Chia Scene (4-7s/scene), khóa Style Bible & Character Anchor vào `scenes.json`    │
│  • Kiểm duyệt (QC) nội dung kịch bản, prompt ảnh và bố cục                           │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │ Đọc / Ghi trực tiếp `scenes.json`
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│            TẦNG 2: LOCAL WEB STUDIO & BACKEND SERVER (`http://127.0.0.1:8080`)       │
│  • Giao diện Editorial Brutalist Dark Studio (#0A0A0A + #FF5500 + #CCFF00, 0-2px)    │
│  • Quản lý danh sách dự án (`projects/<slug>/scenes.json` + `scenes.json` gốc)       │
│  • Storyboard & QC Inspector: Sửa lời thoại / prompt từng cảnh, nghe thử Voice,      │
│    xem ảnh, bấm nút [RE-GEN IMAGE] hoặc [RE-GEN VOICE] cho từng cảnh riêng lẻ        │
│  • Batch Queue Runner: Chạy ngầm toàn bộ 4 Stage (đi cà phê về chỉ việc QC & xuất)  │
└───────┬──────────────────────────┬──────────────────────────┬────────────────────────┘
        │ Stage 2: Visuals         │ Stage 3: Voice AI        │ Stage 4: Subtitles & Video
        ▼                          ▼                          ▼
┌──────────────────────┐  ┌─────────────────────────┐  ┌───────────────────────────────┐
│ ComfyUI Local API    │  │ Kokoro-82M (`kokoro-onnx`│  │ Faster-Whisper / Manifest Sync│
│ (RTX 5060 8GB VRAM)  │  │ + `edge-tts` / FastAPI) │  │ + FFmpeg Ken Burns (`zoompan`)│
│ + Pollinations FLUX  │  │ + `ffprobe` Lock Dur    │  │ + Styled ASS Burn-in -> `.mp4`│
└──────────────────────┘  └─────────────────────────┘  └───────────────────────────────┘
```

---

## 2. Design Commitment (`@[frontend-specialist]`)

- **Selected Radical Style**: **Editorial Brutalist Dark Broadcast Deck** (Lấy cảm hứng từ bàn dựng phim Teenage Engineering / Blackmagic DaVinci Resolve kết hợp Typography Brutalism).
- **Topological Choice**: Phá bỏ bố cục SaaS chia đôi nhàm chán; sử dụng **Asymmetric Command Rail + Horizontal Filmstrip / Modular Storyboard Matrix** với thanh trạng thái phần cứng & pipeline chạy dọc và số thứ tự Scene khổ lớn (`JetBrains Mono` / `Space Grotesk`).
- **Color Palette (Zero Purple Ban Compliance)**:
  - Canvas Primary: `#0A0A0A` (Carbon Obsidian)
  - Surface / Panel: `#121212` & `#181818` với viền sắc cạnh `1px solid #2A2A2A`
  - Primary Accent: `#FF5500` (Signal International Orange)
  - Secondary / Active Status: `#CCFF00` (Acid Volt)
  - Text: `#F5F5F0` (Editorial Paper White) & `#8E8E8A` (Muted Technical Grey)
- **Geometry**: `0px` – `2px` crisp industrial borders, exposed technical grid lines, physical micro-interactions (`translate`, border highlight).

---

## 3. Implementation Tasks

1. **Upgrade Stage 2 (`generate_scene_images.py`)**:
   - Bổ sung kết nối thực tế tới **Local ComfyUI HTTP API (`http://127.0.0.1:8188/prompt`)** (tự động gửi workflow JSON SDXL/FLUX, poll `/history/{prompt_id}`, tải ảnh về `assets/scenes/scene_00N.png`), hỗ trợ tạo lẻ 1 scene (`--scene-id N`) để phục vụ nút **QC Re-gen Image** trên Web UI, kèm fallback thông minh sang Pollinations FLUX hoặc Placeholder nếu ComfyUI chưa bật.
2. **Upgrade Stage 3 (`generate_tts_scenes.py`)**:
   - Bổ sung engine **`kokoro`** tích hợp trực tiếp (`kokoro-onnx` / OpenAI-compatible Kokoro-FastAPI) với giọng Tiếng Anh kể chuyện truyền cảm (`af_heart`, `af_bella`, `am_adam`, `am_michael`, `bf_emma`, `bm_george`) + fallback tự động sang `edge-tts` (`en-US-ChristopherNeural`, `en-US-AriaNeural`, `en-US-GuyNeural`).
   - Hỗ trợ `--scene-id N` để tạo lại từng câu thoại khi QC.
   - Tự động tìm `ffmpeg` / `ffprobe` (kể cả khi cài qua WinGet hoặc `imageio-ffmpeg`) để đo chuẩn xác `audio_duration_sec`.
3. **Create Starter English Storytelling / Psychology Project (`scenes.json`)**:
   - Tạo sẵn một kịch bản mẫu chất lượng cao bằng Tiếng Anh thể loại **Psychology & Storytelling**: *"The Zeigarnik Effect: Why Your Brain Cannot Let Go of Unfinished Stories"* (định dạng `16:9` `1920x1080`, khóa `style_bible` điện ảnh tâm lý học).
4. **Build Local Web Studio Backend & Frontend (`studio_server.py` + `studio/index.html`)**:
   - Backend Python chuẩn (không phụ thuộc thư viện nặng, chạy ngay với Python 3.11 sẵn có trên máy) cung cấp REST API:
     - `GET /api/status`: Kiểm tra kết nối ComfyUI (`127.0.0.1:8188`), Kokoro TTS, Edge-TTS, FFmpeg, GPU RTX 5060.
     - `GET /api/manifest` & `POST /api/manifest`: Đọc/lưu kịch bản `scenes.json`, đổi tỷ lệ `16:9` ↔ `9:16`, đổi giọng đọc, sửa prompt/lời thoại từng scene.
     - `POST /api/scene/{id}/regen-image` & `POST /api/scene/{id}/regen-tts`: QC tạo lại riêng lẻ 1 ảnh hoặc 1 file âm thanh.
     - `POST /api/pipeline/run` & `GET /api/pipeline/logs`: Chạy ngầm toàn bộ dây chuyền 4 bước (Batch Queue) và stream log thời gian thực lên giao diện Web.
5. **1-Click Packaging (`start_studio.bat`)**:
   - Đóng gói file chạy 1-click trên Windows: tự động kiểm tra thư viện, khởi chạy Local Web Studio tại `http://127.0.0.1:8080` và mở trình duyệt.
