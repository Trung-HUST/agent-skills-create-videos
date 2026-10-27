#!/usr/bin/env python3
"""
generate_subtitles.py
Generates synchronized .srt and Netflix/MasterClass Documentary styled .ass subtitles from scenes.json.
Accounts for the 0.55s end-of-scene natural breath pause so captions appear strictly during speech.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PARALINGUISTIC_TAG_PATTERN = re.compile(
    r"""
    \[
        \s*(?:
            cười|cười\s+nhẹ|bật\s+cười|thở\s+dài|hắng\s+giọng|lấy\s+hơi|ngập\s+ngừng|
            laugh|laughs|chuckle|chuckles|sigh|sighs|clear\s+throat|clears\s+throat|
            throat\s+clear|cough|coughs|gasp|gasps|whisper|groan|sniffle|yawn
        )\s*
    \]
    |
    <
        \s*(?:
            laugh|chuckle|sigh|cough|clear_throat|gasp|groan|sniffle|yawn
        )\s*
    >
    |
    \(
        \s*(?:
            laughs|chuckles|sighs|clears\s+throat|coughs|gasps
        )\s*
    \)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def strip_paralinguistic_tags(text: str) -> str:
    """Strips [cười], [thở dài], [hắng giọng] and English paralinguistic tags so captions are 100% clean."""
    cleaned = PARALINGUISTIC_TAG_PATTERN.sub(" ", text)
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def format_srt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        secs += 1
        ms -= 1000
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def format_ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        secs += 1
        cs -= 100
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"


def split_into_chunks(text: str, max_words: int = 8) -> list[str]:
    words = text.strip().split()
    if not words:
        return []
    chunks = []
    current = []
    for w in words:
        current.append(w)
        if len(current) >= max_words or w.endswith((",", ".", "!", "?", ";", ":")):
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def build_cues_from_manifest(scenes: list[dict], max_words: int = 8) -> list[dict]:
    cues = []
    cursor = 0.0
    breath_pad = 0.50
    for scene in scenes:
        dur = float(scene.get("audio_duration_sec") or scene.get("estimated_duration_sec") or 6.0)
        speech_dur = max(1.5, dur - breath_pad)
        raw_text = scene.get("clean_subtitle_text") or scene.get("narration_text", "")
        text = strip_paralinguistic_tags(str(raw_text))
        scene["clean_subtitle_text"] = text
        chunks = split_into_chunks(text, max_words=max_words)
        if not chunks:
            cursor += dur
            continue
        total_chars = sum(max(1, len(c)) for c in chunks)
        scene_cursor = cursor
        for i, chunk in enumerate(chunks):
            weight = max(1, len(chunk)) / total_chars
            chunk_dur = speech_dur * weight
            start_t = scene_cursor
            end_t = (cursor + speech_dur) if i == len(chunks) - 1 else (scene_cursor + chunk_dur)
            cues.append({"start": round(start_t, 3), "end": round(end_t, 3), "text": chunk})
            scene_cursor = end_t
        cursor += dur
    return cues


def write_srt(cues: list[dict], out_srt: Path) -> None:
    lines = []
    for idx, cue in enumerate(cues, start=1):
        lines.append(f"{idx}")
        lines.append(f"{format_srt_time(cue['start'])} --> {format_srt_time(cue['end'])}")
        lines.append(cue["text"])
        lines.append("")
    out_srt.write_text("\n".join(lines), encoding="utf-8")


def write_ass(cues: list[dict], width: int, height: int, out_ass: Path) -> None:
    is_vertical = height > width
    font_size = 50 if is_vertical else 38
    margin_v = int(height * 0.16) if is_vertical else 44

    # Criterion / Netflix Documentary Subtitle Styling (Warm Paper White &H00E8F0F4, subtle charcoal border)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 1
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Georgia,{font_size},&H00E8F0F4,&H00FFFFFF,&H00101216,&H9008080A,0,0,0,0,100,100,0.4,0,1,2.2,1.5,2,90,90,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for cue in cues:
        start_s = format_ass_time(cue["start"])
        end_s = format_ass_time(cue["end"])
        clean_text = cue["text"].replace("\n", "\\N")
        anim = r"{\fad(110,90)}"
        events.append(f"Dialogue: 0,{start_s},{end_s},Default,,0,0,0,,{anim}{clean_text}")

    out_ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SRT and Documentary ASS subtitles from scenes.json")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--mode",
        default="manifest",
        choices=["manifest", "whisper"],
        help="Timing extraction mode",
    )
    parser.add_argument("--whisper-model", default="base", help="Whisper model size")
    parser.add_argument("--max-words-per-line", type=int, default=8, help="Max words per subtitle line")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/subtitles"), help="Output directory")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    res = data.get("resolution", {"width": 1920, "height": 1080})
    width, height = int(res.get("width", 1920)), int(res.get("height", 1080))
    scenes = data.get("scenes", [])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_srt = args.output_dir / "captions.srt"
    out_ass = args.output_dir / "captions.ass"

    cues = build_cues_from_manifest(scenes, args.max_words_per_line)
    write_srt(cues, out_srt)
    write_ass(cues, width, height, out_ass)

    data["subtitle_srt_path"] = str(out_srt).replace("\\", "/")
    data["subtitle_ass_path"] = str(out_ass).replace("\\", "/")
    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Generated {len(cues)} documentary subtitle cues -> {out_srt} & {out_ass}")


if __name__ == "__main__":
    main()
