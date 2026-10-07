#!/usr/bin/env python3
"""The title logo's katakana strip (advJ texture 17, 1024x1024): ソニック フリーライダーズ -> 索尼克 自由滑板競速.

    python tools/logo.py <advJ_17 PNG> <output PNG> [title]

Rows 320-399 hold the strip: a navy double spike with white slanted letters
outlined in navy; rows 400-469 a white blurred silhouette of it, the glow
drawn behind. The spikes are kept, the lettering is drawn again (spaced out
to span the same plate) and the glow is made from the new strip.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = 'C:/Windows/Fonts/NotoSansTC-VF.ttf'
TEXT = '索尼克 自由滑板競速'
STRIP = (320, 400)
GLOW = (400, 470)
PLATE = (100, 700)   # the letters and their plate, between the spike tips


def main():
    src, dst = sys.argv[1], sys.argv[2]
    text = sys.argv[3] if len(sys.argv) > 3 else TEXT
    img = np.asarray(Image.open(src).convert('RGBA')).copy()
    y0, y1 = STRIP
    strip = img[y0:y1].copy()
    navy = np.median(strip[(strip[..., 3] > 200) & (strip[..., :3].sum(-1) < 200)][:, :3], 0).astype(int)
    # Keep the spikes: the plate's columns become the spine the spikes run along.
    alpha = strip[..., 3]
    spine_rows = np.where(alpha[:, PLATE[0] - 20] > 128)[0]
    strip[:, PLATE[0]:PLATE[1]] = 0
    if len(spine_rows):
        strip[spine_rows.min():spine_rows.max() + 1, PLATE[0] - 30:PLATE[1] + 30, :3] = navy
        strip[spine_rows.min():spine_rows.max() + 1, PLATE[0] - 30:PLATE[1] + 30, 3] = 255

    # The letters: heavy, slanted, spread over the plate.
    font = ImageFont.truetype(FONT, 54)
    font.set_variation_by_axes([900])
    layer = Image.new('L', (PLATE[1] - PLATE[0] + 80, y1 - y0), 0)
    draw = ImageDraw.Draw(layer)
    chars = list(text)
    widths = [font.getlength(c) if c != ' ' else 22 for c in chars]
    gap = (PLATE[1] - PLATE[0] - sum(widths)) / (len(chars) - 1)
    x = 40.0
    for c, w in zip(chars, widths):
        if c != ' ':
            draw.text((x, (y1 - y0) // 2), c, font=font, fill=255, anchor='lm')
        x += w + gap
    # One navy band behind them all, as the katakana's touching outlines made.
    band = Image.new('L', layer.size, 0)
    mid = layer.height // 2
    ImageDraw.Draw(band).rectangle((30, mid - 19, layer.width - 30, mid + 19), fill=255)
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0.3, -0.15 * layer.height, 0, 1, 0), Image.BICUBIC)
    band = band.transform(band.size, Image.AFFINE, (1, 0.3, -0.15 * band.height, 0, 1, 0), Image.BICUBIC)
    letters = np.asarray(layer).astype(float) / 255
    plate = np.maximum(np.asarray(layer.filter(ImageFilter.MaxFilter(11))), np.asarray(band)).astype(float) / 255
    x0 = PLATE[0] - 40
    region = strip[:, x0:x0 + layer.width].astype(float)
    a = plate[..., None]
    region[..., :3] = navy * a + region[..., :3] * (1 - a)
    region[..., 3] = np.maximum(region[..., 3], plate * 255)
    a = letters[..., None]
    region[..., :3] = 255 * a + region[..., :3] * (1 - a)
    strip[:, x0:x0 + layer.width] = region.round().clip(0, 255).astype(np.uint8)
    img[y0:y1] = strip

    # The glow: the new strip's silhouette, white and soft, where the old one was.
    g0, g1 = GLOW
    shape = Image.fromarray(strip[..., 3]).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(4))
    glow = np.zeros((g1 - g0, img.shape[1], 4), np.uint8)
    glow[..., :3] = 255
    h = min(g1 - g0, shape.height)
    glow[:h, :, 3] = np.asarray(shape)[(shape.height - h) // 2:(shape.height - h) // 2 + h]
    img[g0:g1] = glow
    Image.fromarray(img, 'RGBA').save(dst)
    return 0


if __name__ == '__main__':
    sys.exit(main())
