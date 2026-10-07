#!/usr/bin/env python3
"""Tutorial labels (s08tsuiJ textures 13-16, 512x128): チュートリアル／基本／バイク／応用.

    python tools/labels.py <s08tsuiJ texture PNGs directory> <output directory>

Each is slanted lettering on nothing: a gradient fill (its colours taken
from the original's top, middle and bottom) and a thin pale outline. The
label is cleared and the Chinese drawn in the same box.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = 'C:/Windows/Fonts/NotoSansTC-VF.ttf'
LABELS = {13: '教學', 14: '基礎', 15: '機車', 16: '進階'}


def draw_label(original, text, heavy):
    rgba = np.asarray(original.convert('RGBA'))
    ys, xs = np.where(rgba[..., 3] > 40)
    top, bottom = ys.min(), ys.max()
    solid = rgba[..., 3] > 200
    def band(lo, hi):
        rows = (ys >= lo) & (ys <= hi)
        sel = solid[ys[rows], xs[rows]]
        return rgba[ys[rows][sel], xs[rows][sel], :3].mean(0)
    h = bottom - top
    stops = [band(top, top + h * 0.3), band(top + h * 0.4, top + h * 0.6), band(top + h * 0.7, bottom)]
    edge = rgba[(rgba[..., 3] > 60) & (rgba[..., 3] < 200)][:, :3].mean(0)
    if heavy:  # 基本／バイク／応用: a dark outline and a shadow
        lum = rgba[..., :3].sum(-1)
        dark = solid & (lum < np.percentile(lum[solid], 15))
        edge = rgba[dark][:, :3].mean(0)

    size = int(h * (0.95 if heavy else 1.15))
    font = ImageFont.truetype(FONT, size)
    font.set_variation_by_axes([900])
    box = font.getbbox(text)
    w, hh = box[2] - box[0] + 20, box[3] - box[1] + 16
    m = Image.new('L', (w, hh), 0)
    ImageDraw.Draw(m).text((10 - box[0], 8 - box[1]), text, font=font, fill=255)
    outline = m.filter(ImageFilter.MaxFilter(5 if heavy else 3))
    t = np.linspace(0, 1, hh)[:, None, None]
    fill = np.where(t < 0.5, stops[0] * (1 - 2 * t) + stops[1] * 2 * t, stops[1] * (2 - 2 * t) + stops[2] * (2 * t - 1))
    fill = fill * np.ones((1, w, 1))
    img = np.zeros((hh, w, 4), float)
    if heavy:
        shadow = np.roll(np.roll(np.asarray(outline.filter(ImageFilter.MaxFilter(3)), float), 3, 0), 3, 1)[..., None] / 255
        img[..., :3] = np.array((10, 15, 40)) * shadow
        img[..., 3:] = shadow * 200
    a = np.asarray(outline, float)[..., None] / 255
    img[..., :3] = edge * a + img[..., :3] * (1 - a)
    img[..., 3:] = a * 255 + img[..., 3:] * (1 - a)
    a = np.asarray(m, float)[..., None] / 255
    img[..., :3] = fill * a + img[..., :3] * (1 - a)
    layer = Image.fromarray(img.round().clip(0, 255).astype(np.uint8), 'RGBA')
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0.25, -0.125 * hh, 0, 1, 0), Image.BICUBIC)
    out = Image.new('RGBA', original.size, (0, 0, 0, 0))
    cx, cy = (xs.min() + xs.max()) // 2, (top + bottom) // 2
    out.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))
    return out


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for n, text in LABELS.items():
        original = Image.open(next(src.glob(f's08tsuiJ_{n:02d}_512x128.png')))
        draw_label(original, text, n != 13).save(dst / f's08tsuiJ_{n:02d}.png')
    return 0


if __name__ == '__main__':
    sys.exit(main())
