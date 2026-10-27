#!/usr/bin/env python3
"""
book_to_video_scenes.py
Ingests a book file (.pdf, .epub, .txt, .md) or a structured book analysis script
and produces:
  1. A structured chapter/text extraction brief (--extract-only)
  2. A production-ready scenes.json manifest (--from-script) tailored for Book Analysis Videos
     (YouTube 16:9 Deep Essay or TikTok/Shorts 9:16 Book Breakdown).
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

BOOK_BEAT_SEQUENCE_SHORT = [
    "hook_paradox",
    "context_trap",
    "core_story",
    "mental_model_1",
    "mental_model_2",
    "counter_intuitive_truth",
    "actionable_shift",
    "closing_payoff",
]

BOOK_BEAT_SEQUENCE_ESSAY = [
    "hook_paradox",
    "author_context",
    "the_common_myth",
    "mental_model_1",
    "case_study_1",
    "mental_model_2",
    "case_study_2",
    "mental_model_3",
    "critical_blindspot",
    "action_protocol",
    "philosophical_outro",
]

CAMERA_MOTIONS = ["zoom_in_slow", "pan_right", "zoom_out", "pan_left", "zoom_in"]


def extract_text_from_epub(epub_path: Path, max_chars: int = 120000) -> str:
    texts = []
    with zipfile.ZipFile(epub_path, "r") as zf:
        for name in sorted(zf.namelist()):
            if name.lower().endswith((".xhtml", ".html", ".htm")):
                raw = zf.read(name).decode("utf-8", errors="ignore")
                clean = re.sub(r"<[^>]+>", " ", raw)
                clean = re.sub(r"\s+", " ", clean).strip()
                if len(clean) > 200:
                    texts.append(clean)
    return "\n\n".join(texts)[:max_chars]


def extract_text_from_pdf(pdf_path: Path, max_chars: int = 120000) -> str:
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        pages = [page.get_text("text") for page in doc]
        return "\n\n".join(pages)[:max_chars]
    except ImportError:
        pass
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n\n".join(pages)[:max_chars]
    except ImportError:
        print(
            "[WARN] Install PyMuPDF (`pip install pymupdf`) or `pypdf` for direct PDF extraction.",
            file=sys.stderr,
        )
        return ""


def extract_book_brief(input_path: Path) -> dict:
    ext = input_path.suffix.lower()
    if ext == ".epub":
        text = extract_text_from_epub(input_path)
    elif ext == ".pdf":
        text = extract_text_from_pdf(input_path)
    else:
        text = input_path.read_text(encoding="utf-8", errors="ignore")[:120000]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 60]
    headings = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^(#|Chapter|Chương|Phần|Part|\d+\.)\s+", line.strip(), re.IGNORECASE)
    ][:40]

    return {
        "source_file": str(input_path),
        "char_count_extracted": len(text),
        "detected_headings": headings,
        "sample_excerpts": paragraphs[:15],
        "analysis_prompt_template": {
            "1_core_paradox": "Luận điểm phản trực giác lớn nhất mà cuốn sách đặt ra là gì?",
            "2_central_thesis": "Tư tưởng cốt lõi của toàn bộ cuốn sách gói gọn trong 1 câu:",
            "3_mental_models": "3-5 Mô hình tư duy (Mental Models) đắt giá nhất của tác giả:",
            "4_stories_and_proof": "Câu chuyện thực tế hoặc thí nghiệm tâm lý/khoa học ấn tượng nhất trong sách:",
            "5_critical_blindspots": "Giới hạn hoặc điểm mù khi áp dụng cuốn sách này vào thực tế:",
            "6_action_protocol": "Bài học hành động cụ thể người xem áp dụng được ngay trong 24h tới:",
        },
    }


def estimate_duration(text: str, lang: str = "vi") -> float:
    words = len(text.split())
    wps = 2.7 if lang.startswith("vi") else 2.5
    return round(max(3.0, words / wps + 0.5), 2)


def build_book_scenes(
    script_path: Path,
    book_title: str,
    fmt: str,
    lang: str,
    visual_theme: str,
) -> dict:
    raw = script_path.read_text(encoding="utf-8").strip()
    blocks = [b.strip() for b in re.split(r"\n\s*\n|\n", raw) if b.strip()]
    if len(blocks) == 1:
        blocks = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]

    is_short = fmt == "short"
    aspect = "9:16" if is_short else "16:9"
    width, height = (1080, 1920) if is_short else (1920, 1080)
    beats = BOOK_BEAT_SEQUENCE_SHORT if is_short else BOOK_BEAT_SEQUENCE_ESSAY

    scenes = []
    for idx, line in enumerate(blocks, start=1):
        beat = beats[min(idx - 1, len(beats) - 1)]
        motion = CAMERA_MOTIONS[(idx - 1) % len(CAMERA_MOTIONS)]
        scenes.append(
            {
                "scene_id": idx,
                "beat_type": beat,
                "narration_text": line,
                "visual_prompt": (
                    f"Book concept illustration for '{book_title}' ({beat}): {line}. "
                    f"Symbolic visual metaphor, {visual_theme}, clean composition with subtitle safe zone"
                ),
                "camera_motion": motion,
                "transition": "crossfade",
                "overlay_text": book_title if idx == 1 else "",
                "estimated_duration_sec": estimate_duration(line, lang),
            }
        )

    return {
        "project_title": f"Phân Tích Sách: {book_title}",
        "book_title": book_title,
        "video_format": fmt,
        "language": lang,
        "aspect_ratio": aspect,
        "resolution": {"width": width, "height": height},
        "fps": 30,
        "voice_config": {
            "engine": "edge-tts",
            "voice_id": "vi-VN-NamMinhNeural" if lang.startswith("vi") else "en-US-ChristopherNeural",
            "rate": "+0%",
            "pitch": "+0Hz",
        },
        "style_bible": {
            "model_family": "flux",
            "global_style_prompt": visual_theme,
            "negative_prompt": "text, watermark, blurry, messy clutter, deformed hands, low resolution",
            "character_anchor": "a thoughtful reader/architect silhouette in warm dramatic lighting",
        },
        "scenes": scenes,
    }


def main():
    parser = argparse.ArgumentParser(description="Book Analysis & Book-to-Video Scene Manifest Generator")
    parser.add_argument("--input", type=Path, help="Path to book file (.pdf, .epub, .txt, .md)")
    parser.add_argument("--extract-only", action="store_true", help="Extract book structure brief to JSON")
    parser.add_argument("--output-brief", type=Path, default=Path("book_brief.json"), help="Output brief JSON")
    parser.add_argument("--from-script", type=Path, help="Path to approved book analysis script text")
    parser.add_argument("--book-title", default="Sách Tinh Hoa", help="Book Title & Author")
    parser.add_argument(
        "--format",
        default="short",
        choices=["short", "essay"],
        help="short (9:16 TikTok/Reels/Shorts) or essay (16:9 YouTube Deep Dive)",
    )
    parser.add_argument("--lang", default="vi", help="Language code (vi or en)")
    parser.add_argument(
        "--visual-theme",
        default="editorial minimalist philosophical illustration, warm parchment and deep ink contrast, cinematic volumetric lighting, 8k",
        help="Visual style theme for book illustrations",
    )
    parser.add_argument("--output", type=Path, default=Path("scenes.json"), help="Output scenes.json path")
    args = parser.parse_args()

    if args.input and args.extract_only:
        if not args.input.exists():
            print(f"[ERROR] Book file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        brief = extract_book_brief(args.input)
        args.output_brief.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"[OK] Extracted book brief ({brief['char_count_extracted']} chars, "
            f"{len(brief['detected_headings'])} headings) -> {args.output_brief}"
        )
        sys.exit(0)

    if args.from_script:
        if not args.from_script.exists():
            print(f"[ERROR] Script file not found: {args.from_script}", file=sys.stderr)
            sys.exit(1)
        manifest = build_book_scenes(
            args.from_script, args.book_title, args.format, args.lang, args.visual_theme
        )
        args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"[OK] Generated Book Analysis scenes.json ({len(manifest['scenes'])} scenes, "
            f"format={args.format}, aspect={manifest['aspect_ratio']}) -> {args.output}"
        )
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
