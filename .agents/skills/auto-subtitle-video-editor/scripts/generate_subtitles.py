#!/usr/bin/env python3
"""
generate_subtitles.py
Generates synchronized .srt and styled .ass (CapCut/TikTok style) subtitles from scenes.json.
Supports:
  - --mode manifest: Deterministic word-proportional chunking locked to each scene's exact audio_duration_sec.
  - --mode whisper: Uses faster-whisper with word_timestamps=True on each scene's audio file.
"""
import argparse
import json
import sys
from pathlib import Path


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


def split_into_chunks(text: str, max_words: int = 6) -> list[str]:
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


def build_cues_from_manifest(scenes: list[dict], max_words: int = 6) -> list[dict]:
    cues = []
    cursor = 0.0
    for scene in scenes:
        dur = float(scene.get("audio_duration_sec") or scene.get("estimated_duration_sec") or 4.0)
        text = scene.get("narration_text", "").strip()
        chunks = split_into_chunks(text, max_words=max_words)
        if not chunks:
            cursor += dur
            continue
        total_chars = sum(max(1, len(c)) for c in chunks)
        scene_cursor = cursor
        for i, chunk in enumerate(chunks):
            weight = max(1, len(chunk)) / total_chars
            chunk_dur = dur * weight
            start_t = scene_cursor
            end_t = (cursor + dur) if i == len(chunks) - 1 else (scene_cursor + chunk_dur)
            cues.append({"start": round(start_t, 3), "end": round(end_t, 3), "text": chunk})
            scene_cursor = end_t
        cursor += dur
    return cues


def build_cues_from_whisper(scenes: list[dict], model_size: str, max_words: int = 6) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[WARN] faster-whisper not installed; falling back to --mode manifest")
        return build_cues_from_manifest(scenes, max_words=max_words)

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    cues = []
    cursor = 0.0
    for scene in scenes:
        dur = float(scene.get("audio_duration_sec") or scene.get("estimated_duration_sec") or 4.0)
        audio_path = scene.get("audio_path")
        if not audio_path or not Path(audio_path).exists():
            cursor += dur
            continue
        segments, _ = model.transcribe(audio_path, word_timestamps=True)
        words = []
        for seg in segments:
            if seg.words:
                words.extend(seg.words)
        if not words:
            cursor += dur
            continue
        group = []
        for w in words:
            group.append(w)
            if len(group) >= max_words or w.word.strip().endswith((",", ".", "!", "?")):
                cues.append(
                    {
                        "start": round(cursor + group[0].start, 3),
                        "end": round(cursor + group[-1].end, 3),
                        "text": "".join(x.word for x in group).strip(),
                    }
                )
                group = []
        if group:
            cues.append(
                {
                    "start": round(cursor + group[0].start, 3),
                    "end": round(cursor + group[-1].end, 3),
                    "text": "".join(x.word for x in group).strip(),
                }
            )
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
    font_size = 58 if is_vertical else 46
    margin_v = int(height * 0.18) if is_vertical else int(height * 0.08)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 1
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for cue in cues:
        start_s = format_ass_time(cue["start"])
        end_s = format_ass_time(cue["end"])
        clean_text = cue["text"].replace("\n", "\\N")
        # Subtle pop-in animation using ASS override tags
        anim = r"{\fad(80,60)}"
        events.append(f"Dialogue: 0,{start_s},{end_s},Default,,0,0,0,,{anim}{clean_text}")

    out_ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate SRT and styled ASS subtitles from scenes.json")
    parser.add_argument("--manifest", type=Path, default=Path("scenes.json"), help="Path to scenes.json")
    parser.add_argument(
        "--mode",
        default="manifest",
        choices=["manifest", "whisper"],
        help="Timing extraction mode",
    )
    parser.add_argument("--whisper-model", default="base", help="Whisper model size if --mode whisper")
    parser.add_argument("--max-words-per-line", type=int, default=6, help="Max words per subtitle chunk")
    parser.add_argument("--output-dir", type=Path, default=Path("assets/subtitles"), help="Output directory")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"[ERROR] Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    res = data.get("resolution", {"width": 1080, "height": 1920})
    width, height = int(res.get("width", 1080)), int(res.get("height", 1920))
    scenes = data.get("scenes", [])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_srt = args.output_dir / "captions.srt"
    out_ass = args.output_dir / "captions.ass"

    if args.mode == "whisper":
        cues = build_cues_from_whisper(scenes, args.whisper_model, args.max_words_per_line)
    else:
        cues = build_cues_from_manifest(scenes, args.max_words_per_line)

    write_srt(cues, out_srt)
    write_ass(cues, width, height, out_ass)

    data["subtitle_srt_path"] = str(out_srt).replace("\\", "/")
    data["subtitle_ass_path"] = str(out_ass).replace("\\", "/")
    args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Generated {len(cues)} subtitle cues -> {out_srt} & {out_ass}")


if __name__ == "__main__":
    main()
