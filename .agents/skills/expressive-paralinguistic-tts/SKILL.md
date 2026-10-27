---
name: expressive-paralinguistic-tts
description: Expressive Paralinguistic Voice AI (VieNeu-TTS v3 Turbo 48kHz — Giọng Hải Đăng & English Equivalents Chatterbox-Turbo, Orpheus-TTS 3B, Dia-1.6B, Kokoro-82M) — synthesizes 48 kHz philosophical book essays & documentary voiceovers with inline non-verbal cues ([cười]/[laugh], [thở dài]/[sigh], [hắng giọng]/[clear throat]) while keeping on-screen subtitles 100% clean via synthesize_vieneu_scenes.py.
when_to_use: "When the user wants natural expressive Vietnamese TTS (VieNeu-TTS v3 Turbo 48 kHz, voice Hải Đăng) or equivalent expressive English TTS (Chatterbox-Turbo, Orpheus-TTS leo/dan/tara, Dia-1.6B, Kokoro-82M bm_george/am_michael) with inline paralinguistic tags ([cười], [thở dài], [hắng giọng], [laugh], [sigh], [clear throat]) and automatic subtitle tag stripping."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Expressive Paralinguistic Voice AI (VieNeu-TTS v3 Turbo 48 kHz & English Equivalents)

> **Dual-Stream Narration & Clean Caption Architecture.** Great book essays and philosophical documentaries (e.g., Nassim Nicholas Taleb's *The Black Swan* & *Antifragile*) require **non-verbal human micro-expressions**—a wry chuckle before an ironic paradox, a contemplative sigh at a catastrophic blind spot, or a decisive throat-clear before exposing a mathematical fraud. Our pipeline synthesizes these paralinguistic tags directly inside the **48 kHz audio stream**, while `synthesize_vieneu_scenes.py` automatically strips them from the **subtitle stream** so on-screen captions remain 100% clean.

---

## 1. Giọng Đọc Tiếng Việt Tự Nhiên & Giàu Biểu Cảm (`VieNeu-TTS v3 Turbo — 48 kHz`)

- **Model**: [`pnnbao-ump/VieNeu-TTS-v3-Turbo`](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo) (GitHub: [`pnnbao97/VieNeu-TTS`](https://github.com/pnnbao97/VieNeu-TTS), `pip install vieneu`)
- **Training Corpus**: Huấn luyện trên **>10,000 giờ** dữ liệu giao tiếp đời thực & podcast Tiếng Việt chất lượng cao.
- **Audio Output**: **48 kHz (`48,000 Hz`)** native studio sample rate (vượt trội chuẩn 24 kHz thông thường).
- **Default Flagship Voice**: **`Hải Đăng`** (`⭐ Hải Đăng — Nam · Bắc · Phong cách tự nhiên`) — chất giọng nam miền Bắc ấm, giàu nhịp điệu, truyền tải xuất sắc sự châm biếm trí tuệ, chiều sâu triết học và nhịp kể chuyện cuốn hút.
- **Other Preset Voices in VieNeu-TTS v3 Turbo**:
  - `Mai Anh` (Nữ · Bắc · Tự nhiên, podcast/kể chuyện)
  - `Phạm Tuyên` (Nam · Bắc · Trầm ấm, thuyết minh phim tài liệu)
  - `Trúc Ly` (Nữ · Nam · Truyền cảm)
  - `Thiện Minh` (Nam · Nam · Điềm tĩnh)
  - `Thùy Dung`, `Thiền Tâm Đức`, `Ngọc Huyền`, `Quang Sơn`, `Ngọc Trân`

### Inline Paralinguistic Tags (Tái Tạo Biểu Cảm Phi Ngôn Từ Trong Luồng 48 kHz)

| Thẻ biểu cảm (Tag) | Hiệu ứng âm thanh trong luồng 48 kHz | Ứng dụng chuẩn trong kịch bản Phân Tích Sách (VD: Nassim Taleb — *Thiên Nga Đen & Chống Mong Manh*) |
| :--- | :--- | :--- |
| **`[cười]`** | Tiếng bật cười nhẹ / cười mỉa tự nhiên ở đầu hoặc giữa câu | Đặt ở đầu các nghịch lý châm biếm sắc sảo của Nassim Taleb *(Cảnh 1, 2, 3, 4, 5, 6, 8, 9, 12)*. |
| **`[thở dài]`** | Nhịp lấy hơi sâu, trầm lắng, giàu tính chiêm nghiệm | Đặt khi nói về cú sập **Ngày thứ 1,001 của Con Gà Tây**, **Nghĩa địa bằng chứng câm (Silent Evidence)** và **Cái bẫy vùng trung bình (Mediocristan)** *(Cảnh 2, 7, 10)*. |
| **`[hắng giọng]`** | Nhịp chuyển giọng dứt khoát, đanh thép để thu hút sự chú ý | Đặt ngay trước khi vạch trần **Cú lừa đường cong hình chuông Gauss**, **Sự kiêu ngạo nhận thức (Epistemic Arrogance)** và **Chiến lược Tạ Đôi 90/10 (Barbell Strategy)** *(Cảnh 1, 4, 8, 11)*. |

---

## 2. Giọng Đọc Tiếng Anh Tương Đương (`Hải Đăng` English Counterparts & Paralinguistic Engines)

Khi sản xuất video tiếng Anh với cùng phong cách **Book Essay / Philosophical Documentary** và khả năng tái tạo tiếng cười, thở dài, hắng giọng tự nhiên như **`VieNeu-TTS v3 Turbo (Hải Đăng)`**, sử dụng 4 mô hình Open-Source hàng đầu sau:

### Bảng Đối Chiếu Giọng Đọc & Mô Hình Tiếng Anh Tương Đương

| Hạng mục | Tiếng Việt (`VieNeu-TTS v3 Turbo`) | Tiếng Anh Tương Đương #1 (`Chatterbox-Turbo`) | Tiếng Anh Tương Đương #2 (`Orpheus-TTS 3B`) | Tiếng Anh Tương Đương #3 (`Dia-1.6B`) | Tiếng Anh Tương Đương #4 (`Kokoro-82M` + Upsample 48kHz) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Repo / Model** | `pnnbao-ump/VieNeu-TTS-v3-Turbo` | `resemble-ai/chatterbox` (MIT) | `canopylabs/orpheus-3b-0.1-ft` (Apache-2.0) | `nari-labs/Dia-1.6B` (Apache-2.0) | `hexgrad/Kokoro-82M` (Apache-2.0) |
| **Dữ liệu huấn luyện** | >10,000h giao tiếp & podcast Việt | 500,000h speech giàu cảm xúc | >100,000h English podcast & hội thoại tự nhiên | Kho dữ liệu podcast & đối thoại giàu biểu cảm | Tập dữ liệu đọc sách & kể chuyện chuẩn phòng thu |
| **Giọng Nam tương đương `⭐ Hải Đăng`** | **`Hải Đăng`** *(Nam · Bắc · Tự nhiên)* | Zero-shot 5s reference (`haidang_en_ref.wav`) hoặc Default Male | ⭐ **`leo`** *(Warm Intellectual)*, **`dan`** *(Witty Podcast)*, **`zac`** | `[S1]` với audio prompt giọng Nam trầm ấm | ⭐ **`bm_george`** *(British Essayist)*, **`am_michael`** *(US Podcast)*, **`am_adam`** |
| **Giọng Nữ tương đương `Mai Anh`** | **`Mai Anh`** *(Nữ · Bắc · Tự nhiên)* | Zero-shot 5s reference nữ | ⭐ **`tara`** *(Natural Conversational)*, **`leah`**, **`mia`** | `[S2]` | **`af_heart`**, **`af_bella`**, **`bf_emma`** |
| **Thẻ `[cười]`** | `[cười]` | `[laugh]`, `[chuckle]` | `<laugh>`, `<chuckle>` | `(laughs)`, `(chuckles)` | *(Tự động chuyển thành dấu ngắt nhịp tự nhiên)* |
| **Thẻ `[thở dài]`** | `[thở dài]` | `[sigh]` | `<sigh>`, `<gasp>` | `(sighs)`, `(gasps)` | *(Tự động chuyển thành `...` ngắt hơi)* |
| **Thẻ `[hắng giọng]`** | `[hắng giọng]` | `[clear throat]`, `[cough]` | `<cough>`, `<sniffle>` | `(clears throat)`, `(coughs)` | *(Tự động chuyển thành `—` nhấn giọng)* |

### Chi Tiết Các Giọng Tiếng Anh Tương Đương Nhất Với `⭐ Hải Đăng`:

1. **`Orpheus-TTS 3B` — Giọng `leo` & `dan` (`canopylabs/orpheus-3b-0.1-ft`)**:
   - **`leo`**: Giọng nam trầm ấm, điềm tĩnh, tự nhiên theo phong cách host podcast triết học / phân tích sách (Lex Fridman / Philosophize This vibe) — **tương đương 1:1 về sắc thái với giọng `Hải Đăng`**.
   - **`dan`**: Giọng nam sắc sảo, hơi châm biếm thông minh, cực hợp khi đọc các đoạn nghịch lý của Nassim Taleb kèm thẻ `<chuckle>` / `<sigh>` / `<cough>`.
2. **`Chatterbox` / `Chatterbox-Turbo` (`resemble-ai/chatterbox`)**:
   - Hỗ trợ trực tiếp các thẻ `[laugh]`, `[chuckle]`, `[sigh]`, `[clear throat]`, `[cough]`, `[gasp]` ngay trong câu tiếng Anh (cú pháp ngoặc vuông giống hệt `[cười]`, `[thở dài]`, `[hắng giọng]` của VieNeu-TTS v3 Turbo).
   - Có tham số `exaggeration=0.55` và `cfg_weight=0.4` để điều chỉnh độ nhấn nhá biểu cảm.
3. **`Kokoro-82M` — Giọng pha trộn `0.6 * bm_george + 0.4 * am_michael` (`hexgrad/Kokoro-82M`)**:
   - Chạy siêu nhẹ trên CPU (ONNX), kết hợp độ trầm học thuật của `bm_george` (British Male) và nhịp trò chuyện tự nhiên của `am_michael` (American Male), sau đó xuất/resample lên **48 kHz WAV** qua FFmpeg `aresample=48000:resampler=soxr`.

---

## 3. Cơ Chế Ẩn Thẻ Biểu Cảm Khỏi Phụ Đề (`synthesize_vieneu_scenes.py`)

Khi đưa văn bản có chứa `[cười]`, `[thở dài]`, `[hắng giọng]` (hoặc `[laugh]`, `[chuckle]`, `[sigh]`, `[clear throat]`) vào pipeline:

1. **Luồng Âm Thanh (48 kHz Audio Stream)**:
   - Với `vieneu` (`VieNeu-TTS-v3-Turbo`), script giữ nguyên các thẻ `[cười]`, `[thở dài]`, `[hắng giọng]` trong chuỗi đầu vào của `tts.infer(text, voice="Hải Đăng")` để model phát âm trực tiếp tiếng cười, tiếng thở dài và tiếng hắng giọng ở tần số 48 kHz.
   - Với `chatterbox` hoặc `orpheus`, script tự động ánh xạ sang định dạng thẻ tương ứng (`[laugh]`/`<laugh>`, `[sigh]`/`<sigh>`, `[clear throat]`/`<cough>`).
   - Với các engine không hỗ trợ thẻ paralinguistic (như `edge-tts`, `kokoro`), script tự động chuyển thẻ thành nhịp ngắt câu sinh học (`...`, `—`) trước khi đọc để **tuyệt đối không bao giờ đọc thành chữ "mở ngoặc vuông cười đóng ngoặc vuông"**.
2. **Luồng Phụ Đề Hiển Thị (Clean Subtitle Stream — Sạch 100%)**:
   - Hàm `strip_paralinguistic_tags(text)` trong `synthesize_vieneu_scenes.py` và `generate_subtitles.py` tự động loại bỏ hoàn toàn mọi thẻ `[cười]`, `[thở dài]`, `[hắng giọng]`, `[laugh]`, `[chuckle]`, `[sigh]`, `[clear throat]`, `[cough]`, `[gasp]`, `<laugh>`, `<sigh>`, `(laughs)`, v.v.
   - Lưu chuỗi sạch vào trường `clean_subtitle_text` trong `scenes.json` và xuất file `.srt` / `.ass` sạch 100% trên màn hình.

---

## 4. Hướng Dẫn Sử Dụng (`synthesize_vieneu_scenes.py`)

### A. Tổng hợp giọng Tiếng Việt 48 kHz với `VieNeu-TTS v3 Turbo` (Giọng `Hải Đăng`)

```bash
# Cài đặt VieNeu-TTS SDK
pip install vieneu soundfile

# Chạy tổng hợp giọng Hải Đăng 48 kHz cho toàn bộ scenes.json + làm sạch phụ đề
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine vieneu \
  --voice "Hải Đăng" \
  --sample-rate 48000 \
  --output-dir assets/audio
```

### B. Tổng hợp giọng Tiếng Anh biểu cảm tương đương (`Chatterbox` / `Orpheus` / `Kokoro`)

```bash
# 1. Chatterbox-Turbo (hỗ trợ trực tiếp [laugh], [sigh], [clear throat] hoặc tự dịch từ [cười], [thở dài], [hắng giọng])
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine chatterbox \
  --sample-rate 48000 \
  --output-dir assets/audio

# 2. Orpheus-TTS 3B với giọng "leo" (tương đương Hải Đăng bản tiếng Anh)
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine orpheus \
  --voice leo \
  --sample-rate 48000 \
  --output-dir assets/audio

# 3. Kokoro-82M (CPU ONNX nhanh, giọng bm_george hoặc am_michael, resample chuẩn 48 kHz)
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py \
  --manifest scenes.json \
  --engine kokoro \
  --voice bm_george \
  --sample-rate 48000 \
  --output-dir assets/audio
```

---

## 5. Ví Dụ Mẫu `scenes.json` (Kịch Bản Nassim Taleb Với Thẻ Biểu Cảm)

```json
{
  "scenes": [
    {
      "scene_id": 1,
      "title": "Ảo Tưởng Về Sự An Toàn & Đường Cong Hình Chuông",
      "narration_text": "[cười] Bạn thực sự tin rằng rủi ro lớn nhất có thể đo được bằng các mô hình dự báo lịch sử sao? [hắng giọng] Hãy nhìn thẳng vào cú lừa trí tuệ lớn nhất thế kỷ hai mươi: Đường cong hình chuông Gauss.",
      "clean_subtitle_text": "Bạn thực sự tin rằng rủi ro lớn nhất có thể đo được bằng các mô hình dự báo lịch sử sao? Hãy nhìn thẳng vào cú lừa trí tuệ lớn nhất thế kỷ hai mươi: Đường cong hình chuông Gauss."
    },
    {
      "scene_id": 2,
      "title": "Bi Kịch Ngày Thứ 1,001 Của Con Gà Tây",
      "narration_text": "[cười] Hãy tưởng tượng một con gà tây được người đồ tể cho ăn mỗi sáng suốt một nghìn ngày liên tiếp. [thở dài] Đúng vào ngày thứ một nghìn lẻ một, ngay trước Lễ Tạ Ơn, niềm tin khoa học của nó đạt đỉnh điểm—cũng là lúc bi kịch ập xuống.",
      "clean_subtitle_text": "Hãy tưởng tượng một con gà tây được người đồ tể cho ăn mỗi sáng suốt một nghìn ngày liên tiếp. Đúng vào ngày thứ một nghìn lẻ một, ngay trước Lễ Tạ Ơn, niềm tin khoa học của nó đạt đỉnh điểm—cũng là lúc bi kịch ập xuống."
    }
  ]
}
```

---

## Companion Skills

- `.agents/skills/voice-ai-tts/SKILL.md` — Core TTS & Multi-engine Voiceover Pipeline
- `.agents/skills/book-analysis-script/SKILL.md` — Book Essay & Nassim Taleb / Mental Model Scriptwriter
- `.agents/skills/auto-subtitle-video-editor/SKILL.md` — Clean Subtitle Generation & Video Rendering
- `.agents/skills/audio-alignment-demucs-ctc-librosa/SKILL.md` — CTC Forced Alignment & 100fps Audio Envelopes
