#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Animated Rap Battle & Duet Lyric MV Render Engine Template
Part of the `suno-battle-mv-architect` global skill.
Supports:
- 16:9 Full HD (1920x1080) & 9:16 YouTube Shorts Vertical (1080x1920)
- SIMD uint16 ROI Alpha Patch Blending
- Ken Burns Camera Movement + 1.2s Cross-Dissolve
- Audio-Reactive Bass Envelope + Bottom Spectrum Visualizer
- Speaker-Adaptive Theme Switching (cyan / crimson / gold / purple)
- Zero-Tofu Glyph Enforcement & Unicode-Safe OpenCV I/O
- Intel QuickSync (h264_qsv with -pix_fmt nv12) + libx264 Fallback
"""

import argparse
import json
import math
import os
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1920
HEIGHT = 1080
FPS = 30
TRANSITION_SEC = 1.2

FONT_BOLD_PATH = "C:/Windows/Fonts/msjhbd.ttc"
FONT_REG_PATH = "C:/Windows/Fonts/msjh.ttc"

DEFAULT_SCENES_CONFIG = [
    {"id": 1, "file": "scene_01.png", "start": 0.0,   "end": 14.64, "mode": "zoom_in",        "fx": "embers"},
    {"id": 2, "file": "scene_02.png", "start": 14.64, "end": 32.16, "mode": "pan_right",      "fx": "sparks"},
    {"id": 3, "file": "scene_03.png", "start": 32.16, "end": 46.72, "mode": "zoom_in_fast",   "fx": "cyan_orb"},
    {"id": 4, "file": "scene_04.png", "start": 46.72, "end": 60.76, "mode": "pan_left",       "fx": "cyan_orb"},
    {"id": 5, "file": "scene_05.png", "start": 60.76, "end": 74.64, "mode": "zoom_in",        "fx": "crimson"},
    {"id": 6, "file": "scene_06.png", "start": 74.64, "end": 89.48, "mode": "zoom_out",       "fx": "crimson"},
    {"id": 7, "file": "scene_07.png", "start": 89.48, "end": 109.80,"mode": "cosmic_breathe", "fx": "chorus"},
    {"id": 8, "file": "scene_08.png", "start": 109.80,"end": 128.70,"mode": "pan_up",         "fx": "embers"},
    {"id": 9, "file": "scene_09.png", "start": 128.70,"end": 148.80,"mode": "zoom_in_fast",   "fx": "sparks"},
    {"id": 10,"file": "scene_10.png", "start": 148.80,"end": 168.00,"mode": "zoom_out_slow",  "fx": "feathers"},
    {"id": 11,"file": "scene_11.png", "start": 168.00,"end": 189.20,"mode": "drift_finale",   "fx": "chorus"}
]

THEME_COLORS = {
    "cyan": {
        "border": (0, 240, 255, 255),
        "badge_bg": (0, 130, 175, 240),
        "glow": (0, 200, 255, 95),
        "line2_color": (140, 248, 255, 255)
    },
    "crimson": {
        "border": (255, 55, 95, 255),
        "badge_bg": (175, 20, 55, 240),
        "glow": (255, 45, 85, 95),
        "line2_color": (255, 165, 180, 255)
    },
    "gold": {
        "border": (255, 215, 70, 255),
        "badge_bg": (165, 115, 15, 240),
        "glow": (255, 195, 40, 95),
        "line2_color": (255, 232, 135, 255)
    },
    "amber": {
        "border": (255, 215, 70, 255),
        "badge_bg": (165, 115, 15, 240),
        "glow": (255, 195, 40, 95),
        "line2_color": (255, 232, 135, 255)
    },
    "purple": {
        "border": (217, 70, 239, 255),
        "badge_bg": (126, 34, 206, 240),
        "glow": (217, 70, 239, 95),
        "line2_color": (245, 208, 254, 255)
    }
}


def imread_unicode(path: Path) -> np.ndarray:
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def imwrite_unicode(path: Path, img: np.ndarray):
    ext = path.suffix if path.suffix else ".png"
    ok, buf = cv2.imencode(ext, img)
    if ok:
        buf.tofile(str(path))


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def probe_audio_duration(audio_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        return float(out)
    except Exception:
        return 180.0


def ensure_composite_fallback(assets_dir: Path, target_name: str = "scene_10.png"):
    """Synthesize a diagonal spotlight composite if a scene image is missing due to rate limits."""
    target = assets_dir / target_name
    if target.exists() and target.stat().st_size > 50000:
        test_im = imread_unicode(target)
        if test_im is not None and np.mean(test_im) > 5.0:
            return

    s3 = imread_unicode(assets_dir / "scene_03.png")
    s6 = imread_unicode(assets_dir / "scene_06.png")
    if s3 is None or s6 is None:
        return

    s3 = cv2.resize(s3, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
    s6 = cv2.resize(s6, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
    xx, yy = np.meshgrid(np.linspace(0, 1, WIDTH), np.linspace(0, 1, HEIGHT))
    diag = np.clip((xx - 0.5 + (yy - 0.5) * 0.18) * 6.0 + 0.5, 0.0, 1.0)[..., None]
    comp = (s3.astype(np.float32) * (1.0 - diag) + s6.astype(np.float32) * diag)

    dist = np.sqrt(((xx - 0.5) * 1.3) ** 2 + ((yy - 0.25) * 1.1) ** 2)
    vignette = np.clip(1.15 - dist * 0.75, 0.25, 1.0)[..., None]
    comp = np.clip(comp * vignette, 0, 255).astype(np.uint8)

    for r in range(HEIGHT):
        cx = int(WIDTH * 0.5 - (r - HEIGHT * 0.5) * 0.18)
        cv2.circle(comp, (cx, r), 3, (120, 230, 255), -1)

    imwrite_unicode(target, comp)


def extract_audio_envelope(audio_path: Path, total_frames: int) -> np.ndarray:
    env_rate = FPS * 4
    cmd = [
        "ffmpeg", "-v", "quiet",
        "-i", str(audio_path),
        "-ac", "1", "-ar", str(env_rate),
        "-f", "f32le", "-"
    ]
    try:
        raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        samples = np.frombuffer(raw, dtype=np.float32)
        rms = np.zeros(total_frames, dtype=np.float32)
        spf = 4
        for i in range(total_frames):
            chunk = samples[i * spf:(i + 1) * spf]
            if len(chunk) > 0:
                rms[i] = float(np.sqrt(np.mean(chunk ** 2)))
        p95 = np.percentile(rms, 95) if len(rms) > 0 else 1.0
        if p95 > 1e-6:
            rms = np.clip(rms / p95, 0.0, 1.0)
        return rms
    except Exception:
        return np.zeros(total_frames, dtype=np.float32)


def pil_rgba_to_roi_patch(im: Image.Image, x1: int, y1: int):
    arr = np.array(im, dtype=np.uint16)
    rgb = arr[:, :, :3]
    bgr = rgb[:, :, ::-1].copy()
    alpha_u16 = arr[:, :, 3:4].copy()
    inv_alpha_u16 = (255 - alpha_u16).copy()
    premul_bgr_u16 = (bgr * alpha_u16).copy()
    h, w = bgr.shape[:2]
    return {
        "premul_u16": premul_bgr_u16,
        "inv_a_u16": inv_alpha_u16,
        "bgr_f32": bgr.astype(np.float32),
        "alpha_f32": (alpha_u16.astype(np.float32) / 255.0),
        "bbox": (x1, y1, x1 + w, y1 + h)
    }


def blend_roi_patch(frame_bgr: np.ndarray, patch: dict, opacity: float = 1.0):
    if opacity <= 0.01:
        return
    x1, y1, x2, y2 = patch["bbox"]
    if opacity >= 0.995:
        roi = frame_bgr[y1:y2, x1:x2].astype(np.uint16)
        frame_bgr[y1:y2, x1:x2] = ((roi * patch["inv_a_u16"] + patch["premul_u16"]) // 255).astype(np.uint8)
    else:
        roi = frame_bgr[y1:y2, x1:x2].astype(np.float32)
        a = patch["alpha_f32"] * opacity
        frame_bgr[y1:y2, x1:x2] = np.clip(roi * (1.0 - a) + patch["bgr_f32"] * a, 0, 255).astype(np.uint8)


def prerender_subtitle_patches(timeline: list) -> list:
    font_speaker = load_font(FONT_BOLD_PATH, 24)
    font_line1 = load_font(FONT_BOLD_PATH, 42)
    font_line2 = load_font(FONT_BOLD_PATH, 36)

    patch_w = 1480
    patch_h = 215
    x1 = (WIDTH - patch_w) // 2
    y1 = HEIGHT - 85 - patch_h + 35

    rendered = []
    for item in timeline:
        theme = THEME_COLORS.get(item.get("theme", "gold"), THEME_COLORS["gold"])
        im = Image.new("RGBA", (patch_w, patch_h), (0, 0, 0, 0))
        glow_im = Image.new("RGBA", (patch_w, patch_h), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_im)
        gdraw.rounded_rectangle([24, 46, patch_w - 24, patch_h - 14], radius=34, fill=theme["glow"])
        glow_im = glow_im.filter(ImageFilter.GaussianBlur(radius=10))
        im = Image.alpha_composite(im, glow_im)
        draw = ImageDraw.Draw(im)

        draw.rounded_rectangle(
            [28, 50, patch_w - 28, patch_h - 18],
            radius=30,
            fill=(18, 14, 28, 222),
            outline=theme["border"],
            width=3
        )

        speaker_text = f"◆ {item.get('speaker', 'MC')}"
        sb_bbox = draw.textbbox((0, 0), speaker_text, font=font_speaker)
        sb_w = (sb_bbox[2] - sb_bbox[0]) + 44
        sb_h = 42
        sb_x = 70
        sb_y = 24
        draw.rounded_rectangle(
            [sb_x, sb_y, sb_x + sb_w, sb_y + sb_h],
            radius=18,
            fill=theme["badge_bg"],
            outline=(255, 255, 255, 220),
            width=2
        )
        draw.text((sb_x + 22, sb_y + 6), speaker_text, font=font_speaker, fill=(255, 255, 255, 255))

        line1 = item.get("line1", "")
        b1 = draw.textbbox((0, 0), line1, font=font_line1)
        tx1 = (patch_w - (b1[2] - b1[0])) // 2
        draw.text((tx1, 72), line1, font=font_line1, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(10, 10, 18, 255))

        line2 = item.get("line2", "")
        if line2:
            b2 = draw.textbbox((0, 0), line2, font=font_line2)
            tx2 = (patch_w - (b2[2] - b2[0])) // 2
            draw.text((tx2, 132), line2, font=font_line2, fill=theme["line2_color"], stroke_width=3, stroke_fill=(10, 10, 18, 255))

        patch_data = pil_rgba_to_roi_patch(im, x1, y1)
        patch_data["start"] = float(item["start"])
        patch_data["end"] = float(item["end"])
        patch_data["theme"] = item.get("theme", "gold")
        rendered.append(patch_data)

    return rendered


def prerender_top_hud_patches(title_text: str, left_label: str, right_label: str):
    font_hud = load_font(FONT_BOLD_PATH, 22)
    font_vs = load_font(FONT_BOLD_PATH, 28)
    hud_w = 1800
    hud_h = 74
    x1 = (WIDTH - hud_w) // 2
    y1 = 22

    hud_patches = {}
    for active in ["gold", "amber", "cyan", "crimson", "purple"]:
        im = Image.new("RGBA", (hud_w, hud_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)

        p1_alpha = 235 if active in ("cyan", "gold", "amber", "purple") else 135
        p1_outline = (0, 245, 255, 255) if active == "cyan" else (120, 180, 200, 160)
        draw.rounded_rectangle([10, 10, 560, 62], radius=22, fill=(12, 32, 48, p1_alpha), outline=p1_outline, width=2)
        draw.text((34, 21), f"◆ {left_label}", font=font_hud, fill=(180, 250, 255, 255))

        draw.rounded_rectangle([680, 8, 1120, 64], radius=24, fill=(24, 18, 36, 220), outline=(255, 210, 80, 230), width=2)
        vs_txt = f"【 {title_text} 】"
        vb = draw.textbbox((0, 0), vs_txt, font=font_vs)
        draw.text((900 - (vb[2] - vb[0]) // 2, 18), vs_txt, font=font_vs, fill=(255, 225, 110, 255))

        p2_alpha = 235 if active in ("crimson", "gold", "amber", "purple") else 135
        p2_outline = (255, 60, 100, 255) if active == "crimson" else (180, 110, 130, 160)
        draw.rounded_rectangle([1240, 10, 1790, 62], radius=22, fill=(48, 12, 24, p2_alpha), outline=p2_outline, width=2)
        p2_txt = f"{right_label} ◆"
        pb = draw.textbbox((0, 0), p2_txt, font=font_hud)
        draw.text((1766 - (pb[2] - pb[0]), 21), p2_txt, font=font_hud, fill=(255, 190, 205, 255))

        hud_patches[active] = pil_rgba_to_roi_patch(im, x1, y1)

    return hud_patches


class KenBurnsPreloader:
    def __init__(self, assets_dir: Path, scenes_cfg: list):
        self.scenes = {}
        self.pad_w = int(WIDTH * 1.18)
        self.pad_h = int(HEIGHT * 1.18)
        for sc in scenes_cfg:
            p = assets_dir / sc["file"]
            img = imread_unicode(p)
            if img is None:
                img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            self.scenes[sc["id"]] = cv2.resize(img, (self.pad_w, self.pad_h), interpolation=cv2.INTER_LANCZOS4)

    def sample_scene(self, scene_cfg: dict, t: float, bass: float) -> np.ndarray:
        img_pad = self.scenes[scene_cfg["id"]]
        dur = max(0.1, scene_cfg["end"] - scene_cfg["start"])
        prog = np.clip((t - scene_cfg["start"]) / dur, 0.0, 1.0)
        mode = scene_cfg["mode"]
        ease = 0.5 - 0.5 * math.cos(prog * math.pi)
        bass_zoom = bass * 0.018

        scale, cx_ratio, cy_ratio = 1.0, 0.5, 0.5
        if mode == "zoom_in":
            scale = 1.0 + 0.12 * ease + bass_zoom
        elif mode == "zoom_in_fast":
            scale = 1.0 + 0.15 * prog + bass_zoom * 1.3
        elif mode == "zoom_out":
            scale = 1.14 - 0.12 * ease + bass_zoom
        elif mode == "zoom_out_slow":
            scale = 1.12 - 0.09 * ease
        elif mode == "pan_right":
            scale = 1.08 + bass_zoom
            cx_ratio = 0.35 + 0.30 * ease
        elif mode == "pan_left":
            scale = 1.08 + bass_zoom
            cx_ratio = 0.65 - 0.30 * ease
        elif mode == "pan_up":
            scale = 1.10 + bass_zoom
            cy_ratio = 0.68 - 0.35 * ease
        elif mode == "cosmic_breathe":
            scale = 1.06 + 0.05 * math.sin(t * 2.8) + bass_zoom * 1.5
        elif mode == "drift_finale":
            scale = 1.05 + 0.03 * math.sin(t * 1.5)
            cx_ratio = 0.5 + 0.08 * math.sin(t * 0.9)

        crop_w = min(self.pad_w, max(WIDTH, int(WIDTH / scale * 1.14)))
        crop_h = min(self.pad_h, max(HEIGHT, int(HEIGHT / scale * 1.14)))
        x0 = int((self.pad_w - crop_w) * cx_ratio)
        y0 = int((self.pad_h - crop_h) * cy_ratio)
        cropped = img_pad[y0:y0 + crop_h, x0:x0 + crop_w]
        return cv2.resize(cropped, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)


class ParticleSystem:
    def __init__(self, count: int = 85):
        rng = np.random.default_rng(42)
        self.count = count
        self.x = rng.uniform(0, WIDTH, count)
        self.y = rng.uniform(0, HEIGHT, count)
        self.vx = rng.uniform(-25, 25, count)
        self.vy = rng.uniform(-90, -30, count)
        self.size = rng.integers(2, 6, count)
        self.phase = rng.uniform(0, 2 * math.pi, count)
        self.color_idx = rng.integers(0, 3, count)

    def render(self, frame: np.ndarray, t: float, fx_mode: str, bass: float):
        palettes = {
            "embers":   [(60, 170, 255), (90, 220, 255), (40, 110, 255)],
            "sparks":   [(255, 230, 90), (90, 90, 255), (255, 255, 200)],
            "cyan_orb": [(255, 240, 110), (255, 200, 40), (220, 255, 180)],
            "crimson":  [(95, 50, 255), (160, 70, 255), (110, 180, 255)],
            "chorus":   [(80, 220, 255), (255, 230, 80), (140, 90, 255)],
            "feathers": [(210, 240, 255), (170, 220, 255), (255, 245, 220)]
        }
        pal = palettes.get(fx_mode, palettes["embers"])
        dir_y = 1.0 if fx_mode == "feathers" else -1.0

        for i in range(self.count):
            px = int((self.x[i] + self.vx[i] * t + math.sin(t * 2.0 + self.phase[i]) * 18) % WIDTH)
            py = int((self.y[i] + dir_y * abs(self.vy[i]) * t) % (HEIGHT - 140))
            col = pal[int(self.color_idx[i])]
            r = int(self.size[i] + (2 if bass > 0.65 else 0))
            cv2.circle(frame, (px, py), r, col, -1, lineType=cv2.LINE_AA)

        bar_count = 36
        bar_w = 10
        gap = 8
        total_bw = bar_count * (bar_w + gap)
        bx0 = (WIDTH - total_bw) // 2
        by_base = HEIGHT - 236
        for b in range(bar_count):
            wave = abs(math.sin(t * 8.0 + b * 0.45)) * (0.35 + 0.65 * bass)
            bh = int(6 + wave * 28)
            bx = bx0 + b * (bar_w + gap)
            bcol = (255, 220, 60) if b < bar_count // 2 else (95, 70, 255)
            cv2.rectangle(frame, (bx, by_base - bh), (bx + bar_w, by_base), bcol, -1)


def get_scene_for_time(t: float, scenes_cfg: list):
    for idx, sc in enumerate(scenes_cfg):
        if sc["start"] <= t <= sc["end"] or idx == len(scenes_cfg) - 1:
            rem = sc["end"] - t
            if rem < TRANSITION_SEC / 2.0 and idx + 1 < len(scenes_cfg):
                alpha = 0.5 * (1.0 - rem / (TRANSITION_SEC / 2.0))
                return sc, scenes_cfg[idx + 1], alpha
            elapsed = t - sc["start"]
            if elapsed < TRANSITION_SEC / 2.0 and idx > 0:
                alpha = 0.5 * (1.0 - elapsed / (TRANSITION_SEC / 2.0))
                return sc, scenes_cfg[idx - 1], alpha
            return sc, None, 0.0
    return scenes_cfg[-1], None, 0.0


def convert_frame_to_vertical_9x16(frame_16x9: np.ndarray) -> np.ndarray:
    """Convert a 1920x1080 landscape frame into a 1080x1920 vertical Shorts frame with blurred backdrop."""
    out_w, out_h = 1080, 1920
    bg_crop = frame_16x9[:, 420:1500]
    bg = cv2.resize(bg_crop, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
    bg = cv2.GaussianBlur(bg, (45, 45), 0)
    bg = (bg.astype(np.float32) * 0.45).astype(np.uint8)

    fg_h = 608
    fg = cv2.resize(frame_16x9, (out_w, fg_h), interpolation=cv2.INTER_AREA)
    y_offset = (out_h - fg_h) // 2
    bg[y_offset:y_offset + fg_h, :] = fg
    cv2.line(bg, (0, y_offset), (out_w, y_offset), (90, 210, 255), 2)
    cv2.line(bg, (0, y_offset + fg_h), (out_w, y_offset + fg_h), (255, 80, 120), 2)
    return bg


def detect_qsv_support() -> bool:
    cmd = [
        "ffmpeg", "-v", "quiet",
        "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.1",
        "-pix_fmt", "nv12", "-c:v", "h264_qsv", "-f", "null", "-"
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Render Animated Rap Battle & Duet Lyric MV")
    parser.add_argument("--mode", choices=["preview", "full"], default="preview")
    parser.add_argument("--aspect", choices=["16:9", "9:16"], default="16:9")
    parser.add_argument("--encoder", choices=["auto", "qsv", "x264"], default="auto")
    parser.add_argument("--audio", required=True, help="Input audio file path")
    parser.add_argument("--timeline", default="lyrics_timeline.json", help="Lyrics timeline JSON file")
    parser.add_argument("--title", default="五丈原巔峰饒舌對決", help="Top center battle HUD title")
    parser.add_argument("--left-player", default="蜀漢丞相｜臥龍・諸葛孔明", help="Top left player HUD label")
    parser.add_argument("--right-player", default="曹魏太傅｜塚虎・司馬仲達", help="Top right player HUD label")
    parser.add_argument("--output", required=True, help="Output MP4 file path")
    args = parser.parse_args()

    base_dir = Path.cwd()
    audio_path = Path(args.audio) if os.path.isabs(args.audio) else (base_dir / args.audio)
    timeline_path = Path(args.timeline) if os.path.isabs(args.timeline) else (base_dir / args.timeline)
    output_path = Path(args.output) if os.path.isabs(args.output) else (base_dir / args.output)
    assets_dir = base_dir / "assets"
    qc_dir = base_dir / "qc_frames"
    qc_dir.mkdir(parents=True, exist_ok=True)

    ensure_composite_fallback(assets_dir, "scene_10.png")

    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    full_dur = probe_audio_duration(audio_path)
    total_duration = 15.0 if args.mode == "preview" else full_dur
    total_frames = int(total_duration * FPS)

    sub_patches = prerender_subtitle_patches(timeline)
    hud_patches = prerender_top_hud_patches(args.title, args.left_player, args.right_player)
    preloader = KenBurnsPreloader(assets_dir, DEFAULT_SCENES_CONFIG)
    particles = ParticleSystem(count=85)
    envelope = extract_audio_envelope(audio_path, total_frames)

    use_qsv = (args.encoder in ("auto", "qsv")) and detect_qsv_support()
    vcodec_args = (
        ["-c:v", "h264_qsv", "-b:v", "7000k", "-pix_fmt", "nv12"]
        if use_qsv
        else ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "0"]
    )

    out_dim = "1080x1920" if args.aspect == "9:16" else f"{WIDTH}x{HEIGHT}"
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", out_dim, "-pix_fmt", "bgr24", "-r", str(FPS),
        "-i", "-",
        "-i", str(audio_path),
        "-t", f"{total_duration:.2f}",
        *vcodec_args,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]

    log_path = base_dir / f"ffmpeg_{args.mode}.log"
    qc_times = [2.0, 5.0, 8.0, 14.0] if args.mode == "preview" else [10.0, 35.0, 68.0, 95.0, 140.0]
    qc_frames_set = {int(ts * FPS): ts for ts in qc_times if ts < total_duration}

    start_ts = time.time()
    with open(log_path, "wb") as log_file:
        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=log_file, stderr=log_file, bufsize=10**7)
        try:
            for f_idx in range(total_frames):
                t = f_idx / FPS
                bass = float(envelope[f_idx]) if f_idx < len(envelope) else 0.0
                sc1, sc2, cross_alpha = get_scene_for_time(t, DEFAULT_SCENES_CONFIG)
                frame = preloader.sample_scene(sc1, t, bass)
                if sc2 is not None and cross_alpha > 0.01:
                    frame2 = preloader.sample_scene(sc2, t, bass)
                    frame = cv2.addWeighted(frame, 1.0 - cross_alpha, frame2, cross_alpha, 0)

                particles.render(frame, t, sc1["fx"], bass)

                active_theme = "gold"
                for sp in sub_patches:
                    if sp["start"] <= t <= sp["end"]:
                        active_theme = sp["theme"]
                        fade = min(1.0, (t - sp["start"]) / 0.18, (sp["end"] - t) / 0.18)
                        blend_roi_patch(frame, sp, max(0.0, fade))
                        break

                blend_roi_patch(frame, hud_patches.get(active_theme, hud_patches["gold"]), 1.0)

                out_frame = convert_frame_to_vertical_9x16(frame) if args.aspect == "9:16" else frame
                if f_idx in qc_frames_set:
                    ts_val = qc_frames_set[f_idx]
                    imwrite_unicode(qc_dir / f"qc_{args.mode}_{int(ts_val):03d}s.png", out_frame)

                proc.stdin.write(out_frame.tobytes())
        finally:
            if proc.stdin:
                proc.stdin.close()
            proc.wait()

    print(f"Success! Video written to: {output_path} ({time.time() - start_ts:.1f}s)")


if __name__ == "__main__":
    main()
