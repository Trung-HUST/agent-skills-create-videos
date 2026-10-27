---
name: book-analysis-script
description: Book Analysis & Video Essay Scriptwriter — distills books (PDF, EPUB, DOCX, TXT, or Book Title) into deep mental-model analyses, chapter syntheses, and high-retention video scripts (YouTube Book Essay, Short-Form Book Breakdown, or NotebookLM Dual-Host Podcast) with ready-to-render scenes.json output.
when_to_use: "When the user asks to analyze a book, summarize a book into a video script, write a YouTube book review/essay (Escaping Ordinary / Spiderum / Better Ideas style), extract mental models from a PDF/EPUB book, or turn a book into a TikTok/Reels short or podcast script."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
priority: CRITICAL
---

# Book Analysis & Video Essay Scriptwriter (Lên Kịch Bản Phân Tích & Review Sách)

> **Distill Structure & Mental Models, Never Flat Chapter Summaries.** A great book analysis video does not recite "Chapter 1 says X, Chapter 2 says Y." It extracts the author's **Core Thesis**, **Counter-Intuitive Paradoxes**, **Named Mental Models**, **Vivid Stories/Experiments**, and **Actionable Shifts in Thinking** — then dramatizes them into a visual narrative (`scenes.json`).

---

## Open-Source Foundations Integrated

| Open-Source Project | GitHub Stars | Role in This Skill |
| :--- | :---: | :--- |
| **`danielmiessler/fabric` (`extract_wisdom`)** | ⭐ 39.1k+ | Deep extraction of Thesis, Mental Models, Quotes, Habits & Counter-Intuitive Ideas |
| **`virgiliojr94/book-to-skill`** | ⭐ 36.1k+ | Deterministic parsing of `.pdf`, `.epub`, `.docx`, `.txt`, `.md` into structured chapters |
| **`souzatharsis/podcastfy` & `open-notebook`** | ⭐ 4.7k+ | NotebookLM-style conversational synthesis & narrative storytelling arcs |
| **`video-script-scene-brain`** | Core | Direct compilation of book scripts into `scenes.json` for automated video rendering |

---

## Protocol: 4-Step Book-to-Video Script Engine

### Step 1: Ingest & Parse Book Source (File or Known Title)

If the user provides a book file (`.pdf`, `.epub`, `.docx`, `.txt`, `.md`), extract its structured chapters and metadata first:

```bash
# Extract text & chapter outlines from PDF / EPUB / TXT into a structured JSON brief
python .agents/skills/book-analysis-script/scripts/book_to_video_scenes.py \
  --input path/to/book.pdf \
  --extract-only \
  --output-brief book_brief.json
```
*(Or use `.agents/skills/book-to-skill/scripts/extract.py` for full multi-chapter skill conversion).*

---

### Step 2: Run the 6-Axis Book Wisdom Extraction (`Fabric extract_wisdom` + Mental Models)

Before writing a single line of narration, synthesize the book across **6 analytical axes** (save to `book_analysis.md`):

1. **The Core Paradox / Enemy (`Luận điểm phản trực giác`)**:
   - What common belief does this book attack? Why do most people get this wrong?
2. **The Central Thesis in 1 Sentence (`Trục tư tưởng cốt lõi`)**:
   - If the entire 300-page book were compressed into one unforgettable law, what is it?
3. **Top 3–5 Named Mental Models / Frameworks (`Mô hình tư duy cốt lõi`)**:
   - Preserve the author's exact terminology (e.g., *System 1 vs System 2*, *Antifragility*, *The Flywheel Effect*, *1% Compounding*).
4. **Golden Stories, Experiments & Case Studies (`Câu chuyện / Thí nghiệm đắt giá`)**:
   - Extract the concrete human stories or scientific experiments the author uses as proof (these make the best visual scenes!).
5. **Critical Nuance & Blind Spots (`Góc nhìn phản biện / Giới hạn của sách`)**:
   - Where does the book's advice fail or get misapplied? (Adding critical nuance separates top-tier analysis channels like *Spiderum / Escaping Ordinary* from generic AI summaries).
6. **The 24-Hour Action Protocol (`Bài học áp dụng ngay`)**:
   - 1–3 concrete behavioral changes the viewer can execute today.

---

### Step 3: Select the Video Script Format

#### Format 1: YouTube Deep-Dive Book Essay (`16:9`, 8–15 mins / 15–30 Scenes)
- **Act I — The Hook & The Trap (0:00–1:30)**: Open with a relatable life paradox or a shocking experiment from the book. Do NOT open with *"Hôm nay mình sẽ tóm tắt cuốn sách..."*.
- **Act II — Mental Model #1: The Root Cause (1:30–4:00)**: Unpack the first core framework with a visual metaphor + real-world story.
- **Act III — Mental Model #2 & #3: The System Shift (4:00–8:00)**: Escalate depth; show how the concepts connect using diagrams/metaphors.
- **Act IV — The Blind Spot / Critique (8:00–10:00)**: Honest critique — when *not* to apply this book blindly.
- **Act V — The Synthesis & Takeaway (10:00–End)**: Tie back to the opening hook + 1 lingering question.

#### Format 2: Short-Form Viral Book Breakdown (`9:16` TikTok/Reels/Shorts, 45–75s / 8–12 Scenes)
- **Rule of One**: Never cram an entire book into 60 seconds. Pick **1 single counter-intuitive Mental Model** or **1 famous experiment** from the book.
- **Structure**:
  - `Scene 1 (0–3s Hook)`: *"Cuốn sách 400 trang [Tên Sách] thực ra chỉ cảnh báo bạn đúng 1 cái bẫy tâm lý này..."*
  - `Scenes 2–4 (The Story/Experiment)`: Tell the concrete experiment or paradox in fast 3.5-second visual beats.
  - `Scenes 5–8 (The Mental Model)`: Reveal the principle and why 90% of people fall into it.
  - `Scenes 9–10 (The Shift / CTA)`: Actionable rule + question for comments.

#### Format 3: NotebookLM / Podcastfy Dual-Host Book Discussion
- Alternates between **Host A (The Architect — explains frameworks)** and **Host B (The Skeptic — asks sharp questions, challenges assumptions, gives relatable examples)**.

---

### Step 4: Compile Directly to `scenes.json` for Video Rendering

Convert the approved book analysis script into a ready-to-render `scenes.json` manifest:

```bash
python .agents/skills/book-analysis-script/scripts/book_to_video_scenes.py \
  --from-script book_script.txt \
  --book-title "Tư Duy Nhanh Và Chậm - Daniel Kahneman" \
  --format short \
  --visual-theme "editorial minimalist philosophical illustration, warm parchment and deep ink contrast, cinematic lighting" \
  --output scenes.json
```

Then run the master video pipeline to generate illustrations, voiceover, subtitles, and final `.mp4`:

```bash
python .agents/skills/create-videos/scripts/run_video_pipeline.py --manifest scenes.json --output output/book_analysis.mp4
```

---

## Companion Skills

- Full multi-chapter book extraction (`.pdf`, `.epub`, `.docx`): `.agents/skills/book-to-skill/SKILL.md`
- Scene breakdown validation: `.agents/skills/video-script-scene-brain/SKILL.md`
- End-to-end video rendering: `.agents/skills/create-videos/SKILL.md`
