from __future__ import annotations

import json
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "obsidian" / "Wibes_Exact_Product_20260415" / "338840769_nash_synochek_exact" / "source"
OUT_DIR = ROOT / "obsidian" / "Wibes_Exact_Product_20260415" / "338840769_nash_synochek_exact"
FRAMES_DIR = OUT_DIR / "frames"
OUT_MP4 = OUT_DIR / "wibes_exact_product_338840769_20260415.mp4"
OUT_POSTER = OUT_DIR / "wibes_exact_product_338840769_20260415_poster.png"
OUT_JSON = OUT_DIR / "wibes_exact_product_338840769_20260415.json"

W = 1080
H = 1920
FPS = 25
DURATION = 7.2
TOTAL_FRAMES = int(FPS * DURATION)

IMAGES = [
    SRC_DIR / "01.webp",
    SRC_DIR / "02.webp",
    SRC_DIR / "03.webp",
    SRC_DIR / "04.webp",
    SRC_DIR / "05.webp",
]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def ease_in_out(value: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * clamp(value, 0.0, 1.0))


def fit_cover(img: Image.Image, scale: float, anchor_x: float, anchor_y: float, rotate_deg: float = 0.0) -> Image.Image:
    canvas = Image.new("RGB", (W, H), (12, 11, 10))
    if rotate_deg:
        img = img.rotate(rotate_deg, resample=Image.Resampling.BICUBIC, expand=True)
    src_w, src_h = img.size
    base_scale = max(W / src_w, H / src_h)
    factor = base_scale * scale
    scaled = img.resize((int(src_w * factor), int(src_h * factor)), Image.Resampling.LANCZOS)
    left = int((W - scaled.width) * anchor_x)
    top = int((H - scaled.height) * anchor_y)
    canvas.paste(scaled, (left, top))
    return canvas


def fit_contain(img: Image.Image, scale: float, shift_x: float = 0.0, shift_y: float = 0.0) -> Image.Image:
    target_w = int(W * scale)
    target_h = int(H * scale)
    fg = img.copy()
    fg.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - fg.width) // 2 + int(shift_x)
    y = (H - fg.height) // 2 + int(shift_y)
    canvas.alpha_composite(fg.convert("RGBA"), (x, y))
    return canvas.convert("RGB")


def add_vignette(img: Image.Image, alpha: float = 0.2) -> Image.Image:
    mask = Image.new("L", (W, H), 255)
    inner = Image.new("L", (W - 180, H - 220), 0)
    mask.paste(inner, (90, 110))
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    shade = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(Image.blend(img, shade, alpha), img, ImageChops.invert(mask))


def add_light_sweep(img: Image.Image, t: float) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = int(-220 + (W + 440) * t)
    polygon = [(x - 120, -80), (x + 20, -80), (x + 280, H + 80), (x + 140, H + 80)]
    from PIL import ImageDraw

    draw = ImageDraw.Draw(overlay)
    draw.polygon(polygon, fill=(255, 228, 196, 34))
    overlay = overlay.filter(ImageFilter.GaussianBlur(60))
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def add_grain(img: Image.Image, seed: int) -> Image.Image:
    rng = random.Random(seed)
    noise = Image.new("L", (W, H))
    px = noise.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = rng.randint(118, 138)
    noise = noise.filter(ImageFilter.GaussianBlur(0.55))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, noise_rgb, 0.042)


def composite_focus(bg_img: Image.Image, fg_img: Image.Image, blur_bg: float, lift: float = 0.0) -> Image.Image:
    bg = fit_cover(bg_img, 1.08, 0.5, 0.5).filter(ImageFilter.GaussianBlur(blur_bg))
    bg = ImageEnhance.Brightness(bg).enhance(0.74)
    bg = ImageEnhance.Color(bg).enhance(0.9)

    fg = fit_contain(fg_img, 0.86, shift_y=lift)
    shadow = fit_contain(fg_img, 0.86, shift_y=lift + 34).filter(ImageFilter.GaussianBlur(28))
    shadow = ImageEnhance.Brightness(shadow).enhance(0.12)

    out = bg.convert("RGBA")
    out.alpha_composite(shadow.convert("RGBA"))
    out.alpha_composite(fg.convert("RGBA"))
    return out.convert("RGB")


SEGMENTS = [
    (0, 30, "hero"),
    (30, 70, "plate"),
    (70, 110, "strap"),
    (110, 145, "pack"),
    (145, TOTAL_FRAMES, "final"),
]


def render_frame(frame_idx: int, assets: list[Image.Image]) -> Image.Image:
    if frame_idx < SEGMENTS[0][1]:
        start, end = SEGMENTS[0][0], SEGMENTS[0][1]
        t = ease_in_out((frame_idx - start) / max(1, end - start - 1))
        base = fit_cover(assets[0], 1.28 - 0.06 * t, 0.56, 0.18, rotate_deg=-5.0 + 1.4 * t)
        base = ImageEnhance.Brightness(base).enhance(0.98)
        base = add_light_sweep(base, 0.08 + 0.18 * t)
        base = add_vignette(base, 0.16)
        return add_grain(base, frame_idx + 13)

    if frame_idx < SEGMENTS[1][1]:
        start, end = SEGMENTS[1][0], SEGMENTS[1][1]
        t = ease_in_out((frame_idx - start) / max(1, end - start - 1))
        focus = composite_focus(assets[1], assets[1], blur_bg=24, lift=-12 + 12 * t)
        focus = add_light_sweep(focus, 0.24 + 0.18 * t)
        focus = add_vignette(focus, 0.22)
        return add_grain(focus, frame_idx + 31)

    if frame_idx < SEGMENTS[2][1]:
        start, end = SEGMENTS[2][0], SEGMENTS[2][1]
        t = ease_in_out((frame_idx - start) / max(1, end - start - 1))
        focus = composite_focus(assets[2], assets[2], blur_bg=22, lift=8 - 10 * t)
        focus = add_light_sweep(focus, 0.44 + 0.16 * t)
        focus = add_vignette(focus, 0.18)
        return add_grain(focus, frame_idx + 59)

    if frame_idx < SEGMENTS[3][1]:
        start, end = SEGMENTS[3][0], SEGMENTS[3][1]
        t = ease_in_out((frame_idx - start) / max(1, end - start - 1))
        base = fit_cover(assets[3], 1.18 + 0.08 * t, 0.54, 0.16, rotate_deg=-4.0 + 1.5 * t)
        base = ImageEnhance.Brightness(base).enhance(0.95)
        base = add_light_sweep(base, 0.62 + 0.14 * t)
        base = add_vignette(base, 0.22)
        return add_grain(base, frame_idx + 83)

    start, end = SEGMENTS[4][0], SEGMENTS[4][1]
    t = ease_in_out((frame_idx - start) / max(1, end - start - 1))
    focus = composite_focus(assets[4], assets[4], blur_bg=20, lift=-8 + 8 * t)
    focus = add_light_sweep(focus, 0.8 + 0.1 * t)
    focus = add_vignette(focus, 0.16)
    return add_grain(focus, frame_idx + 109)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    missing = [str(path) for path in IMAGES if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing source images: {missing}")

    assets = [Image.open(path).convert("RGB") for path in IMAGES]

    for idx in range(TOTAL_FRAMES):
        frame_path = FRAMES_DIR / f"frame_{idx:04d}.png"
        if frame_path.exists():
            continue
        render_frame(idx, assets).save(frame_path, quality=95)

    render_frame(int(TOTAL_FRAMES * 0.84), assets).save(OUT_POSTER, quality=95)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(FRAMES_DIR / "frame_%04d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "slow",
            "-crf",
            "16",
            str(OUT_MP4),
        ],
        check=True,
    )

    report = {
        "sku": "338840769",
        "mode": "exact-product-motion",
        "duration_sec": DURATION,
        "fps": FPS,
        "frames": TOTAL_FRAMES,
        "source_images": [str(path) for path in IMAGES],
        "output_mp4": str(OUT_MP4),
        "output_poster": str(OUT_POSTER),
        "notes": [
            "Built from real WB card media",
            "No generative redraw",
            "No extra text overlays",
            "Prepared for Wibes posting queue",
        ],
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
