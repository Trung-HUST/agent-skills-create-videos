---
name: voice-ai-tts
description: Voice AI & Text-to-Speech (TTS) Engine — synthesizes natural scene-by-scene 48 kHz voiceovers and word-level timing cues using top open-source TTS engines (VieNeu-TTS v3 Turbo 48kHz — Giọng Hải Đăng, Chatterbox-Turbo, Orpheus-TTS 3B, Dia-1.6B, Kokoro-82M, F5-TTS, Edge-TTS, Piper) with inline paralinguistic cues ([cười], [thở dài], [hắng giọng] / [laugh], [sigh], [clear throat]) and 100% clean subtitle stripping.
when_to_use: "When the user asks to generate AI voiceovers, convert script scenes to speech (TTS), use VieNeu-TTS v3 Turbo 48kHz (voice Hải Đăng) with [cười]/[thở dài]/[hắng giọng], use equivalent expressive English voices (Chatterbox, Orpheus leo/dan, Kokoro bm_george/am_michael), clone voices with F5-TTS/Chatterbox, or synchronize scene durations with spoken audio."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Voice AI & TTS Engine (Tạo Giọng Đọc AI 48 kHz & Biểu Cảm Phi Ngôn Từ)

> **Audio-Driven Timeline & Dual-Stream Paralinguistic Architecture.** In professional automated video production, **audio duration dictates video duration**. Furthermore, in philosophical book essays (e.g., Nassim Taleb's *The Black Swan* & *Antifragile*), inline paralinguistic cues (`[cười]`, `[thở dài]`, `[hắng giọng]` / `[laugh]`, `[sigh]`, `[clear throat]`) are synthesized directly inside the **48 kHz audio stream** while `synthesize_vieneu_scenes.py` strips them from `clean_subtitle_text` so on-screen captions remain **100% clean**.

---

## 1. Top Open-Source TTS Engines Selection Matrix

| Engine | GitHub / HuggingFace | Language | Flagship Voice(s) | Inline Paralinguistic Tags | Output Rate | Best Use Case |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **VieNeu-TTS v3 Turbo** | `pnnbao-ump/VieNeu-TTS-v3-Turbo` (`pip install vieneu`) | ⭐ **Tiếng Việt** (>10,000h podcast & giao tiếp) | ⭐ **`Hải Đăng`** *(Nam · Bắc · Tự nhiên)*, `Mai Anh`, `Phạm Tuyên` | `[cười]`, `[thở dài]`, `[hắng giọng]` | **48 kHz** | Giọng đọc phân tích sách, triết học & phim tài liệu Tiếng Việt tự nhiên nhất |
| **Chatterbox-Turbo** | `resemble-ai/chatterbox` (`pip install chatterbox-tts`) | ⭐ **English** & Multilingual | 5s Zero-Shot Clone / Default Narrator | `[laugh]`, `[chuckle]`, `[sigh]`, `[clear throat]`, `[cough]`, `[gasp]` | 24→**48 kHz** | Giọng Tiếng Anh biểu cảm tương đương trực tiếp VieNeu-TTS v3 Turbo |
| **Orpheus-TTS 3B** | `canopylabs/orpheus-3b-0.1-ft` (`pip install orpheus-speech`) | ⭐ **English** (>100,000h podcast) | ⭐ **`leo`**, **`dan`** *(Nam tương đương Hải Đăng)*, **`tara`** *(Nữ)* | `<laugh>`, `<chuckle>`, `<sigh>`, `<cough>`, `<gasp>` | 24→**48 kHz** | Giọng Nam/Nữ podcast triết học & phân tích sách Tiếng Anh tự nhiên nhất |
| **Dia-1.6B** | `nari-labs/Dia-1.6B` | **English** | `[S1]`, `[S2]` + Audio Prompt | `(laughs)`, `(chuckles)`, `(sighs)`, `(clears throat)` | 44.1→**48 kHz** | Podcast 2 host đối thoại kiểu NotebookLM giàu biểu cảm |
| **Kokoro-82M** | `hexgrad/Kokoro-82M` (`pip install kokoro`) | **English** / Multi | ⭐ **`bm_george`**, **`am_michael`**, **`am_adam`** | Tự động chuyển thành nhịp ngắt câu sinh học | 24→**48 kHz** | Chạy siêu nhanh trên CPU (ONNX), giọng đọc học thuật Criterion/BBC |
| **F5-TTS** | `SWivid/F5-TTS` (`EraX-Vi-F5`) | **Vi / En** | Zero-shot (<15s `.wav`) | Theo mẫu tham chiếu | 24→**48 kHz** | Nhân bản giọng đọc cá nhân từ mẫu thu âm 10 giây |
| **Edge-TTS** | `rany2/edge-tts` (`pip install edge-tts`) | **Vi / En** | `vi-VN-NamMinhNeural`, `vi-VN-HoaiMyNeural`, `en-US-BrianNeural` | Tự động lọc sạch thẻ trước khi đọc | 24→**48 kHz** | Không cần GPU (0 VRAM), tốc độ cực nhanh, có sẵn word boundary |

---

## 2. Giọng Đọc Tiếng Việt Chuẩn Phòng Thu 48 kHz (`VieNeu-TTS v3 Turbo` — Giọng `Hải Đăng`)

- **Model**: `pnnbao-ump/VieNeu-TTS-v3-Turbo` (huấn luyện trên >10,000 giờ dữ liệu giao tiếp & podcast Tiếng Việt) với giọng **`Hải Đăng`** (`⭐ Hải Đăng — Nam · Bắc · Phong cách tự nhiên`).
- **Tái tạo trực tiếp biểu cảm phi ngôn từ ngay trong luồng phát âm 48 kHz**:
  - **`[cười]`**: Tiếng bật cười tự nhiên ở đầu các nghịch lý châm biếm của Nassim Taleb *(Cảnh 1, 2, 3, 4, 5, 6, 8, 9, 12)*.
  - **`[thở dài]`**: Nhịp lấy hơi trầm lắng khi nói về cú sập Ngày thứ 1,001 của Con Gà Tây, Nghĩa địa bằng chứng câm và Cái bẫy vùng trung bình *(Cảnh 2, 7, 10)*.
  - **`[hắng giọng]`**: Nhịp chuyển giọng dứt khoát trước khi vạch trần Cú lừa đường cong Gauss, Sự kiêu ngạo nhận thức và Chiến lược Tạ Đôi 90/10 *(Cảnh 1, 4, 8, 11)*.
- **Phụ đề sạch 100%**: Trong khi giữ nguyên tiếng cười/thở dài trong file âm thanh 48 kHz, bộ xử lý `synthesize_vieneu_scenes.py` tự động ẩn các thẻ `[cười]`, `[thở dài]`, `[hắng giọng]` khỏi dòng phụ đề (`clean_subtitle_text`) để chữ hiển thị trên màn hình sạch 100%.

```bash
# Tổng hợp giọng Hải Đăng 48 kHz + tự động lọc sạch thẻ [cười], [thở dài], [hắng giọng] khỏi phụ đề
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine vieneu \
  --voice "Hải Đăng" \
  --sample-rate 48000 \
  --output-dir assets/audio
```

---

## 3. Giọng Đọc Tiếng Anh Tương Đương `⭐ Hải Đăng` (`Chatterbox`, `Orpheus-TTS`, `Kokoro-82M`)

```bash
# 1. Chatterbox-Turbo (hỗ trợ trực tiếp [laugh], [chuckle], [sigh], [clear throat])
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine chatterbox \
  --sample-rate 48000 \
  --output-dir assets/audio

# 2. Orpheus-TTS 3B — Giọng "leo" hoặc "dan" (Nam · Podcast triết học tương đương 1:1 với Hải Đăng)
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine orpheus \
  --voice leo \
  --sample-rate 48000 \
  --output-dir assets/audio

# 3. Kokoro-82M — Giọng "bm_george" (British Essayist) hoặc "am_michael" (US Podcast)
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine kokoro \
  --voice bm_george \
  --sample-rate 48000 \
  --output-dir assets/audio
```

---

## 4. Fast Zero-VRAM Fallback (`generate_tts_scenes.py` với Edge-TTS)

```bash
python .agents/skills/voice-ai-tts/scripts/generate_tts_scenes.py \
  --manifest scenes.json \
  --engine edge-tts \
  --voice vi-VN-NamMinhNeural \
  --output-dir assets/audio
```

---

## Companion Skills

- Deep Paralinguistic & English Voice Counterpart Guide: `.agents/skills/expressive-paralinguistic-tts/SKILL.md`
- Audio Stem Separation, CTC Forced Alignment & 100fps Librosa Envelopes: `.agents/skills/audio-alignment-demucs-ctc-librosa/SKILL.md`
- Deep ComfyUI Voice Cloning (Chatterbox, RVC, IndexTTS-2, Wav2Lip, LivePortrait): `.agents/skills/comfyui-voice-pipeline/SKILL.md`
- Next step in pipeline: `.agents/skills/auto-subtitle-video-editor/SKILL.md`
