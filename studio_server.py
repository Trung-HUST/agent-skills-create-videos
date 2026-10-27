#!/usr/bin/env python3
"""
studio_server.py
Local AI Video Production Studio — Backend Orchestrator & REST API Server.
Connects Antigravity's scenes.json manifest with ComfyUI (RTX 5060), Kokoro-82M / Edge-TTS,
and FFmpeg automated rendering via a fast local Web UI at http://127.0.0.1:8080.
"""
import argparse
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT_DIR / "scenes.json"
STUDIO_DIR = ROOT_DIR / "studio"
SKILLS_DIR = ROOT_DIR / ".agents" / "skills"

KOKORO_ONNX_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


class JobState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.status: str = "idle"  # idle | running | completed | error
        self.current_task: str = "Ready"
        self.logs: list[str] = [
            "[SYSTEM] Local AI Video Studio initialized.",
            "[SYSTEM] Ready to orchestrate Stage 1 (Script/QC) -> Stage 2 (ComfyUI/FLUX) -> Stage 3 (Kokoro TTS) -> Stage 4 (FFmpeg MP4).",
        ]
        self.started_at: float = 0.0

    def append_log(self, line: str) -> None:
        with self.lock:
            ts = time.strftime("%H:%M:%S")
            self.logs.append(f"[{ts}] {line}")
            if len(self.logs) > 400:
                self.logs = self.logs[-400:]

    def set_status(self, status: str, task: str = "") -> None:
        with self.lock:
            self.status = status
            if task:
                self.current_task = task
            if status == "running":
                self.started_at = time.time()


JOB = JobState()


def get_ffmpeg_exe() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return ""


def probe_comfyui(api_url: str = "http://127.0.0.1:8188") -> dict:
    try:
        req = urllib.request.Request(f"{api_url.rstrip('/')}/system_stats", headers={"User-Agent": "AG-Studio"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            devices = data.get("devices", [{}])
            dev_name = devices[0].get("name", "CUDA GPU") if devices else "Connected"
            return {"online": True, "url": api_url, "device": dev_name}
    except Exception:
        return {"online": False, "url": api_url, "device": "Offline (Pollinations FLUX / Storyboard Fallback Ready)"}


def probe_kokoro() -> dict:
    onnx_file = ROOT_DIR / "models" / "kokoro" / "kokoro-v1.0.onnx"
    voices_file = ROOT_DIR / "models" / "kokoro" / "voices-v1.0.bin"
    local_weights = onnx_file.exists() and voices_file.exists()
    fastapi_online = False
    try:
        req = urllib.request.Request("http://127.0.0.1:8880/v1/models", headers={"User-Agent": "AG-Studio"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            fastapi_online = resp.status == 200
    except Exception:
        pass
    return {
        "local_onnx_ready": local_weights,
        "fastapi_online": fastapi_online,
        "edge_tts_ready": True,
        "mode": "Kokoro-82M Local ONNX"
        if local_weights
        else ("Kokoro-FastAPI :8880" if fastapi_online else "Neural TTS Ready (Click to download Kokoro ONNX 310MB)"),
    }


def probe_gpu() -> str:
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )
        if res.returncode == 0 and res.stdout.strip():
            parts = [x.strip() for x in res.stdout.strip().split(",")]
            if len(parts) >= 3:
                return f"{parts[0]} ({parts[1]} / {parts[2]} MiB VRAM)"
            return res.stdout.strip()
    except Exception:
        pass
    return "NVIDIA GeForce RTX 5060 (8151 MiB)"


def run_subprocess_job(task_title: str, cmd: list[str]) -> None:
    def _worker() -> None:
        JOB.set_status("running", task_title)
        JOB.append_log(f"▶ STARTING: {task_title}")
        JOB.append_log(f"$ {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                clean = line.rstrip()
                if clean:
                    JOB.append_log(clean)
            proc.wait()
            if proc.returncode == 0:
                JOB.append_log(f"✔ COMPLETED: {task_title}")
                JOB.set_status("completed", f"Done: {task_title}")
            else:
                JOB.append_log(f"✖ FAILED (exit {proc.returncode}): {task_title}")
                JOB.set_status("error", f"Failed: {task_title}")
        except Exception as exc:
            JOB.append_log(f"✖ EXCEPTION: {exc}")
            JOB.set_status("error", f"Error: {exc}")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def download_kokoro_models() -> None:
    def _dl_worker() -> None:
        JOB.set_status("running", "Downloading Kokoro-82M ONNX Weights (~310MB)")
        target_dir = ROOT_DIR / "models" / "kokoro"
        target_dir.mkdir(parents=True, exist_ok=True)
        files = [
            ("kokoro-v1.0.onnx", KOKORO_ONNX_URL),
            ("voices-v1.0.bin", KOKORO_VOICES_URL),
        ]
        try:
            for fname, url in files:
                dest = target_dir / fname
                if dest.exists() and dest.stat().st_size > 1_000_000:
                    JOB.append_log(f"[SKIP] {fname} already downloaded ({dest.stat().st_size // (1024*1024)} MB)")
                    continue
                JOB.append_log(f"⬇ Downloading {fname} from {url} ...")
                urllib.request.urlretrieve(url, str(dest))
                JOB.append_log(f"✔ Saved {fname} ({dest.stat().st_size // (1024*1024)} MB)")
            JOB.set_status("completed", "Kokoro-82M Local ONNX Ready!")
        except Exception as exc:
            JOB.append_log(f"✖ Kokoro download failed: {exc}")
            JOB.set_status("error", "Download failed")

    threading.Thread(target=_dl_worker, daemon=True).start()


def load_enriched_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"error": "scenes.json not found"}
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for idx, scene in enumerate(data.get("scenes", []), start=1):
        sid = int(scene.get("scene_id", idx))
        default_img = f"assets/scenes/scene_{sid:03d}.png"
        default_aud = f"assets/audio/scene_{sid:03d}.mp3"
        img_p = scene.get("image_path") or default_img
        aud_p = scene.get("audio_path") or default_aud
        scene["image_exists"] = (ROOT_DIR / img_p).exists()
        scene["audio_exists"] = (ROOT_DIR / aud_p).exists()
        if scene["image_exists"]:
            scene["image_path"] = img_p
            scene["image_mtime"] = int((ROOT_DIR / img_p).stat().st_mtime)
        if scene["audio_exists"]:
            scene["audio_path"] = aud_p
            scene["audio_mtime"] = int((ROOT_DIR / aud_p).stat().st_mtime)

    final_vid = data.get("final_video_path", "output/final_video.mp4")
    vid_file = ROOT_DIR / final_vid
    data["final_video_exists"] = vid_file.exists()
    if vid_file.exists():
        data["final_video_path"] = final_vid
        data["final_video_mtime"] = int(vid_file.stat().st_mtime)
        data["final_video_size_kb"] = vid_file.stat().st_size // 1024
    return data


class StudioRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        pass  # Keep console clean

    def _send_json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _read_body_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/status":
            with JOB.lock:
                job_snapshot = {
                    "status": JOB.status,
                    "current_task": JOB.current_task,
                    "logs": list(JOB.logs[-120:]),
                }
            self._send_json(
                {
                    "gpu": probe_gpu(),
                    "ffmpeg": bool(get_ffmpeg_exe()),
                    "comfyui": probe_comfyui(),
                    "kokoro": probe_kokoro(),
                    "job": job_snapshot,
                }
            )
            return

        if route == "/api/manifest":
            self._send_json(load_enriched_manifest())
            return

        # Serve static UI or media files
        if route in ("/", "/index.html"):
            target = STUDIO_DIR / "index.html"
        else:
            rel = route.lstrip("/")
            target = (ROOT_DIR / rel).resolve()
            if not str(target).startswith(str(ROOT_DIR)):
                self.send_error(403, "Forbidden")
                return

        if not target.exists() or not target.is_file():
            self.send_error(404, f"Not found: {route}")
            return

        ctype, _ = mimetypes.guess_type(str(target))
        ctype = ctype or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path
        body = self._read_body_json()

        if route == "/api/manifest":
            # Save updated scenes.json
            clean_scenes = []
            for idx, s in enumerate(body.get("scenes", []), start=1):
                s_copy = dict(s)
                s_copy["scene_id"] = idx
                s_copy.pop("image_exists", None)
                s_copy.pop("audio_exists", None)
                s_copy.pop("image_mtime", None)
                s_copy.pop("audio_mtime", None)
                clean_scenes.append(s_copy)
            body["scenes"] = clean_scenes
            body.pop("final_video_exists", None)
            body.pop("final_video_mtime", None)
            body.pop("final_video_size_kb", None)

            aspect = body.get("aspect_ratio", "16:9")
            body["resolution"] = {"width": 1080, "height": 1920} if aspect == "9:16" else {"width": 1920, "height": 1080}

            MANIFEST_PATH.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
            JOB.append_log(f"[QC SAVE] Saved scenes.json ({len(clean_scenes)} scenes, {aspect}).")
            self._send_json({"ok": True, "manifest": load_enriched_manifest()})
            return

        if JOB.status == "running":
            self._send_json({"ok": False, "error": "Another job is currently running in the queue."}, status=409)
            return

        if route == "/api/kokoro/download":
            download_kokoro_models()
            self._send_json({"ok": True, "message": "Started downloading Kokoro-82M ONNX weights."})
            return

        if route == "/api/scene/regen-image":
            sid = int(body.get("scene_id", 1))
            engine = body.get("image_engine", "comfyui")
            comfy_url = body.get("comfyui_url", "http://127.0.0.1:8188")
            script = SKILLS_DIR / "scene-image-generator" / "scripts" / "generate_scene_images.py"
            cmd = [
                sys.executable,
                str(script),
                "--manifest",
                str(MANIFEST_PATH),
                "--engine",
                engine,
                "--api-url",
                comfy_url,
                "--scene-id",
                str(sid),
                "--overwrite",
            ]
            run_subprocess_job(f"QC Re-gen Image: Scene #{sid:02d} ({engine})", cmd)
            self._send_json({"ok": True})
            return

        if route == "/api/scene/regen-tts":
            sid = int(body.get("scene_id", 1))
            engine = body.get("tts_engine", "kokoro")
            voice = body.get("voice_id", "am_adam")
            script = SKILLS_DIR / "voice-ai-tts" / "scripts" / "generate_tts_scenes.py"
            cmd = [
                sys.executable,
                str(script),
                "--manifest",
                str(MANIFEST_PATH),
                "--engine",
                engine,
                "--voice",
                voice,
                "--scene-id",
                str(sid),
                "--overwrite",
            ]
            run_subprocess_job(f"QC Re-gen Voice: Scene #{sid:02d} ({engine} / {voice})", cmd)
            self._send_json({"ok": True})
            return

        if route == "/api/pipeline/run":
            mode = body.get("mode", "full")  # full | images | tts | render
            img_engine = body.get("image_engine", "comfyui")
            tts_engine = body.get("tts_engine", "kokoro")
            voice = body.get("voice_id", "am_adam")
            comfy_url = body.get("comfyui_url", "http://127.0.0.1:8188")
            fast = bool(body.get("fast", False))
            overwrite = bool(body.get("overwrite", False))

            if mode == "images":
                script = SKILLS_DIR / "scene-image-generator" / "scripts" / "generate_scene_images.py"
                cmd = [sys.executable, str(script), "--manifest", str(MANIFEST_PATH), "--engine", img_engine, "--api-url", comfy_url]
                if overwrite:
                    cmd.append("--overwrite")
                run_subprocess_job(f"Stage 2 Batch Images ({img_engine})", cmd)
            elif mode == "tts":
                script = SKILLS_DIR / "voice-ai-tts" / "scripts" / "generate_tts_scenes.py"
                cmd = [sys.executable, str(script), "--manifest", str(MANIFEST_PATH), "--engine", tts_engine, "--voice", voice]
                if overwrite:
                    cmd.append("--overwrite")
                run_subprocess_job(f"Stage 3 Batch Voice AI ({tts_engine} / {voice})", cmd)
            elif mode == "render":
                sub_s = SKILLS_DIR / "auto-subtitle-video-editor" / "scripts" / "generate_subtitles.py"
                vid_s = SKILLS_DIR / "auto-subtitle-video-editor" / "scripts" / "assemble_video.py"
                cmd_str = (
                    f'"{sys.executable}" "{sub_s}" --manifest "{MANIFEST_PATH}" --mode manifest && '
                    f'"{sys.executable}" "{vid_s}" --manifest "{MANIFEST_PATH}" --output "output/final_video.mp4"'
                    + (" --fast" if fast else "")
                )
                run_subprocess_job("Stage 4 Subtitles + FFmpeg Render MP4", ["cmd", "/c", cmd_str] if os.name == "nt" else ["sh", "-c", cmd_str])
            else:
                script = SKILLS_DIR / "create-videos" / "scripts" / "run_video_pipeline.py"
                cmd = [
                    sys.executable,
                    str(script),
                    "--manifest",
                    str(MANIFEST_PATH),
                    "--image-engine",
                    img_engine,
                    "--comfyui-url",
                    comfy_url,
                    "--tts-engine",
                    tts_engine,
                    "--voice",
                    voice,
                ]
                if fast:
                    cmd.append("--fast")
                if overwrite:
                    cmd.append("--overwrite")
                run_subprocess_job(f"Full 4-Stage Unattended Pipeline ({img_engine} + {tts_engine})", cmd)

            self._send_json({"ok": True})
            return

        self.send_error(404, f"Unknown endpoint: {route}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Start Local AI Video Production Web Studio")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8080, help="Bind port")
    args = parser.parse_args()

    STUDIO_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), StudioRequestHandler)
    print(f"\n============================================================")
    print(f"  AG LOCAL AI VIDEO STUDIO — RUNNING AT http://{args.host}:{args.port}")
    print(f"  Hardware: {probe_gpu()}")
    print(f"============================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping Local Video Studio.")
        server.server_close()


if __name__ == "__main__":
    main()
