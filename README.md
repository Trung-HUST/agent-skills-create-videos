# 🎬 AG Local AI Video Production Studio (Trạm Sản Xuất Video AI Tự Động)

> **Hệ thống Tự Động Hóa Làm Video YouTube View Ngoại (Tiếng Anh)** — Kết hợp bộ não đạo diễn **Antigravity**, vẽ ảnh **ComfyUI (NVIDIA RTX 5060 8GB)** / **FLUX**, giọng đọc **Kokoro-82M / Neural TTS**, đóng phụ đề **ASS/SRT** và dựng phim tự động bằng **FFmpeg**.

---

## 🚀 1. Cách Khởi Chạy Giao Diện Web Local (`http://127.0.0.1:8080`)

### Cách 1: Chạy 1-Click trên Windows (Khuyên dùng)
Nhấp đúp chuột trực tiếp vào file:
```bat
start_studio.bat
```
*(Hệ thống sẽ tự động bật máy chủ Local và mở trình duyệt tại địa chỉ `http://127.0.0.1:8080`)*.

### Cách 2: Chạy bằng lệnh trong Terminal / PowerShell
Mở PowerShell tại thư mục `c:\Users\PT\Documents\Ai-local` và chạy lệnh:
```powershell
python studio_server.py --host 127.0.0.1 --port 8080
```
Sau đó mở trình duyệt truy cập: **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

---

## 🎲 2. Kho 1.000 Lệnh Xúc Xắc Ngẫu Nhiên & Cơ Chế Chống Trùng Lặp

Trên giao diện Web **[http://127.0.0.1:8080](http://127.0.0.1:8080)**, hệ thống được tích hợp sẵn **2 Trạm Xúc Xắc Ngẫu Nhiên Độc Lập** (lưu trữ tại `data/topic_prompts.json`):

1. **🎲 Xúc Xắc 1 — 500 Lệnh Kể Chuyện / Kiến Thức / Tâm Lý Học (`SP-001` $\rightarrow$ `SP-500`):**
   * Gồm 100 hiệu ứng tâm lý học, thiên kiến nhận thức, thí nghiệm hành vi và nghịch lý cuộc sống nổi tiếng nhất (*Dunning-Kruger, Zeigarnik, Sunk Cost, Stanford Prison, Pavlov, Shadow Work, Flow State...*) nhân với 5 góc tiếp cận kể chuyện kịch tính.
2. **📚 Xúc Xắc 2 — 500 Lệnh Phân Tích Sách Chuyên Sâu (`BK-001` $\rightarrow$ `BK-500`):**
   * Gồm 100 cuốn sách kinh điển thế giới về Tâm lý, Tư duy, Tài chính, Triết học và Thói quen (*Thinking Fast and Slow, Atomic Habits, The Psychology of Money, Antifragile, Deep Work, Meditations, The 48 Laws of Power...*) nhân với 5 lăng kính phân tích chuyên sâu theo chuẩn `book-analysis-script`.

### Cơ chế Tự Động Loại Bỏ Chủ Đề Đã Dùng:
* Mỗi lần bấm **`🎲 ĐỔ XÚC XẮC NGẪU NHIÊN`**, hệ thống chỉ bốc từ những chủ đề **chưa từng sử dụng** (`used: false`).
* Khi bạn bấm **`✅ DÙNG CHỦ ĐỀ NÀY (NẠP KỊCH BẢN & LOẠI KHỎI XÚC XẮC)`** hoặc **`🚀 DÙNG CHỦ ĐỀ & CHẠY TẠO VIDEO NGAY`**:
  1. Chủ đề đó lập tức được đánh dấu **`used: true`** trong file `data/topic_prompts.json`.
  2. Chủ đề đó **bị loại vĩnh viễn khỏi vòng quay xúc xắc** (bộ đếm giảm từ `500` xuống `499`, `498`...) để kênh của bạn không bao giờ làm trùng chủ đề.
  3. Toàn bộ chủ đề đã dùng được liệt kê ở mục **`🔒 CÁC CHỦ ĐỀ ĐÃ SỬ DỤNG`** bên dưới (có nút **Khôi phục** nếu bạn bấm nhầm hoặc muốn đặt lại toàn bộ kho).

---

## 🛠️ 3. Quy Trình 4 Bước Tạo Video "Treo Máy Đi Cà Phê"

### Bước 1: Chọn Chủ Đề & Lên Kịch Bản (`scenes.json`)
Bạn có **2 cách** để lên kịch bản sau khi đổ xúc xắc trên Web:
* **Cách A (Tự động nhanh trên Web):** Bấm **`✅ DÙNG CHỦ ĐỀ NÀY`** (hoặc **`🚀 DÙNG CHỦ ĐỀ & CHẠY TẠO VIDEO NGAY`**) — hệ thống tự động khóa chủ đề khỏi xúc xắc và tạo ngay khung kịch bản Tiếng Anh 5 cảnh vào `scenes.json`.
* **Cách B (Kịch bản sâu 10–15 cảnh cùng Antigravity):**
  1. Bấm **`📋 COPY LỆNH GỬI ANTIGRAVITY`** ngay dưới ô xúc xắc.
  2. Dán (`Ctrl + V`) câu lệnh đó vào khung chat của **Antigravity**, ví dụ:
     > *"Viết cho tôi kịch bản Tiếng Anh 10 cảnh về hiệu ứng tâm lý Dunning-Kruger theo phong cách kể chuyện kịch tính, khóa Style Bible điện ảnh vào scenes.json"*
  3. Bấm **`✅ DÙNG CHỦ ĐỀ NÀY`** trên Web để loại chủ đề đó khỏi kho xúc xắc. Antigravity sẽ viết kịch bản chi tiết 10–12 cảnh trực tiếp vào file `scenes.json`.

---

### Bước 2: Chạy Hàng Đợi Tự Động (Batch Queue)
Ở cột bên trái của trang Web `http://127.0.0.1:8080`:
1. **Tỷ lệ khung hình:** Chọn `16:9 Ngang (YouTube Dài)` hoặc `9:16 Dọc (Shorts / TikTok)`.
2. **Bộ máy Vẽ Ảnh:**
   * Chọn **`ComfyUI Local (:8188)`** nếu bạn đang bật ComfyUI trên card **RTX 5060**.
   * Chọn **`Pollinations FLUX (Miễn phí)`** nếu muốn tạo ảnh FLUX đám mây không cần bật ComfyUI.
   * Chọn **`Thẻ Storyboard Nháp (Siêu tốc)`** nếu muốn dựng nháp kiểm tra âm thanh và phụ đề trong 10 giây.
3. **Bộ máy Giọng đọc:**
   * Chọn **`Kokoro-82M`** hoặc **`Edge-TTS Neural`** và chọn giọng đọc (`am_adam`, `af_heart`, `bm_george`, `en-US-ChristopherNeural`...).
   * *(Mẹo: Bấm nút **`⬇ TẢI TRỌNG SỐ KOKORO-82M OFFLINE (310MB)`** ở cột trái nếu muốn tải mô hình Kokoro chạy 100% không cần mạng)*.
4. Bấm nút màu cam **`▶ CHẠY TOÀN BỘ 4 BƯỚC TỰ ĐỘNG`** rồi rời máy đi làm việc khác.

---

### Bước 3: Kiểm Duyệt & Chỉnh Sửa Từng Cảnh (Human-in-the-loop QC)
Khi quay lại máy, bạn lướt qua **Bảng Phân Cảnh Chi Tiết (Storyboard)**:
* **Muốn sửa lời thoại của 1 cảnh:** Sửa trực tiếp ô *Lời thoại Tiếng Anh* $\rightarrow$ bấm **`↻ ĐỌC LẠI CÂU NÀY`** (hệ thống chỉ tạo lại đúng file âm thanh của cảnh đó và tự động đo lại thời lượng giây).
* **Muốn vẽ lại bức ảnh của 1 cảnh:** Sửa ô *Câu lệnh Vẽ Ảnh Minh Họa* $\rightarrow$ bấm **`↻ TẠO LẠI ẢNH NÀY`** (hệ thống chỉ vẽ lại đúng bức ảnh của cảnh đó mà không làm mất ảnh các cảnh khác).
* **Đổi góc máy chuyển động:** Chọn `Phóng to chậm (Zoom In)`, `Thu nhỏ mở rộng (Zoom Out)`, `Lia máy sang phải (Pan Right)` hoặc `Lia máy sang trái (Pan Left)`.

---

### Bước 4: Đóng Phụ Đề & Xuất Bản Video MP4
* Sau khi đã ưng ý tất cả các cảnh, bấm nút **`BƯỚC 4: ĐÓNG PHỤ ĐỀ & XUẤT VIDEO MP4`** ở cột bên trái.
* Xem trực tiếp video hoàn chỉnh tại khung **`04 // VIDEO MP4 XUẤT BẢN CUỐI CÙNG`** và bấm **`⬇ TẢI VIDEO MP4 VỀ MÁY`** (hoặc lấy file tại `output/final_video.mp4`).

---

## 💻 4. Các Lệnh Chạy Bằng Dòng Lệnh (CLI Dành Cho Tự Động Hóa)

Nếu muốn gọi trực tiếp từng công cụ qua Terminal mà không cần mở trình duyệt:

```powershell
# 1. Tạo lại cơ sở dữ liệu 1.000 chủ đề (500 Kể chuyện/Tâm lý + 500 Phân tích sách)
python scripts/build_1000_prompts_db.py

# 2. Chạy trọn gói 4 bước tạo video từ scenes.json
python .agents/skills/create-videos/scripts/run_video_pipeline.py --manifest scenes.json --image-engine comfyui --tts-engine kokoro --output output/final_video.mp4

# 3. Chỉ tạo lại ảnh của riêng Cảnh số 2 bằng ComfyUI
python .agents/skills/scene-image-generator/scripts/generate_scene_images.py --manifest scenes.json --engine comfyui --scene-id 2 --overwrite

# 4. Chỉ tạo lại giọng đọc của riêng Cảnh số 2
python .agents/skills/voice-ai-tts/scripts/generate_tts_scenes.py --manifest scenes.json --engine kokoro --voice am_adam --scene-id 2 --overwrite

# 5. Đóng phụ đề ASS/SRT (tự động lọc sạch thẻ [cười], [thở dài], [hắng giọng]) và ghép lại video MP4
python .agents/skills/auto-subtitle-video-editor/scripts/generate_subtitles.py --manifest scenes.json --mode manifest
python .agents/skills/auto-subtitle-video-editor/scripts/assemble_video.py --manifest scenes.json --output output/final_video.mp4

# 6. Tổng hợp giọng đọc 48 kHz giàu biểu cảm (VieNeu-TTS v3 Turbo — Giọng Hải Đăng & Giọng Tiếng Anh tương đương)
#    Giữ nguyên [cười], [thở dài], [hắng giọng] trong file âm thanh 48 kHz nhưng ẩn sạch 100% khỏi phụ đề:
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py --manifest scenes.json --engine vieneu --voice "Hải Đăng" --sample-rate 48000 --output-dir assets/audio
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py --manifest scenes.json --engine chatterbox --sample-rate 48000 --output-dir assets/audio
python .agents/skills/voice-ai-tts/scripts/synthesize_vieneu_scenes.py --manifest scenes.json --engine orpheus --voice leo --sample-rate 48000 --output-dir assets/audio

# 7. Tách stem Demucs + CTC Forced Alignment (MMS_FA / wav2vec2) + Whisper + Librosa 100fps Envelopes
python .agents/skills/audio-alignment-demucs-ctc-librosa/scripts/analyze_and_align_audio.py --audio assets/audio/scene_001.wav --lyrics lyrics.txt --output output/audio_analysis.json

# 8. Render video 60fps bằng Playwright (Headless Chrome WebGL/Canvas2D) + Adaptive Sub-frame Motion Blur + FFmpeg (libx264)
python .agents/skills/pdoom-playwright-webgl-video/scripts/render_playwright_ffmpeg.py --url http://127.0.0.1:5173 --duration 30 --fps 60 --subframes 4 --output output/webgl_video.mp4
```

---

## 🎙️ 5. Bộ 3 Skill Nâng Cao: `pdoom-video`, `Demucs + CTC + Librosa` & Giọng Đọc Biểu Cảm 48 kHz

| Skill | Đường dẫn | Chức năng cốt lõi |
| :--- | :--- | :--- |
| **`expressive-paralinguistic-tts`** | `.agents/skills/expressive-paralinguistic-tts/SKILL.md` | **Tiếng Việt 48 kHz**: `VieNeu-TTS v3 Turbo` (`pnnbao-ump/VieNeu-TTS-v3-Turbo`, >10,000h podcast) với giọng **`⭐ Hải Đăng`** tái tạo trực tiếp `[cười]`, `[thở dài]`, `[hắng giọng]` trong luồng 48 kHz.<br>**Tiếng Anh tương đương**: `Chatterbox-Turbo` (`[laugh]`, `[sigh]`, `[clear throat]`), `Orpheus-TTS 3B` (giọng `leo`, `dan`, `tara`), `Dia-1.6B`, `Kokoro-82M` (`bm_george`, `am_michael`).<br>**Phụ đề sạch 100%**: `synthesize_vieneu_scenes.py` tự động ẩn toàn bộ thẻ biểu cảm khỏi dòng phụ đề. |
| **`audio-alignment-demucs-ctc-librosa`** | `.agents/skills/audio-alignment-demucs-ctc-librosa/SKILL.md` | Tách vocal bằng **Demucs (`htdemucs_ft`)**, căn chỉnh từ/âm tiết chính xác tới từng mili-giây bằng **CTC Forced Alignment (`MMS_FA` + `wav2vec2`)** đối chiếu chéo với **Whisper**, và trích xuất **100fps Librosa RMS/Frequency Envelopes** (`attack=10ms, release=90ms`). |
| **`pdoom-playwright-webgl-video`** | `.agents/skills/pdoom-playwright-webgl-video/SKILL.md` | Kiến trúc dựng video từ code dựa trên [`mexicat/pdoom-video`](https://github.com/mexicat/pdoom-video): **Playwright (Headless Chrome)** khóa thời gian ảo `window.__seekTo(t)`, tính **Adaptive Tile Sub-frame Motion Blur (`32×32` tiles, `4..324` samples)** và truyền luồng raw `rgb24` qua WebSocket thẳng vào **FFmpeg (`libx264`, CRF 16, BT.709)**. |

---

## 📂 5. Cấu Trúc Thư Mục Dự Án

```plaintext
Ai-local/
├── start_studio.bat             # File chạy 1-Click mở Web Studio Local
├── studio_server.py             # Máy chủ Backend điều phối Pipeline & Kho 1000 chủ đề
├── scenes.json                  # File kịch bản phân cảnh trung tâm (Single Source of Truth)
├── studio/
│   └── index.html               # Giao diện Web Tiếng Việt điều khiển & QC
├── data/
│   └── topic_prompts.json       # Kho 1.000 lệnh (500 Kể chuyện/Tâm lý + 500 Phân tích sách)
├── scripts/
│   └── build_1000_prompts_db.py # Script khởi tạo kho 1.000 chủ đề
├── assets/
│   ├── scenes/                  # Ảnh minh họa từng cảnh (scene_001.png...)
│   ├── audio/                   # File giọng đọc từng cảnh (scene_001.mp3...)
│   ├── subtitles/               # File phụ đề (captions.srt & captions.ass)
│   └── clips/                   # Các đoạn video từng cảnh trước khi nối
└── output/
    └── final_video.mp4          # Video MP4 thành phẩm cuối cùng
```
