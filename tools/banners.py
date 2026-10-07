#!/usr/bin/env python3
"""Course-name banners (advJ textures 0-15, 1024x64): erase the Japanese and draw the Chinese.

    python tools/banners.py <advJ texture PNGs directory> <output directory> [--preview]

Each banner is a coloured bar with the course name and a grey bar with the
grade (スタンダード／エキスパート), split by a slant near x = 520. The text is
found as what differs from the bar's own colour in that row, filled from the
bar on either side along the row, and the Chinese is drawn in the same style:
slanted heavy lettering, a light-to-dark fill, a dark outline and a shadow,
with the colours taken from the original lettering.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = 'C:/Windows/Fonts/NotoSansTC-VF.ttf'
COURSES = ['海豚度假村', '岩石山脊', '冰凍森林', '大都會高速公路', '熔岩裂谷', '遺忘古墓', '最終工廠', '金屬都市']
GRADES = ['標準', '專家']


def slant_of(rgba):
    """x of the colour/grey boundary in each row."""
    sat = rgba[..., :3].max(2) - rgba[..., :3].min(2)
    xs, ys = [], []
    for y in range(4, 48):
        row = sat[y, 470:640]
        hit = np.where((row[:-6] > 90) & (row[6:] < 60))[0]
        if len(hit):
            xs.append(470 + hit[-1] + 6)
            ys.append(y)
    k, c = np.polyfit(ys, xs, 1)
    return lambda y: int(round(k * y + c))


def erase(rgba, x0, x1, rows, ref):
    """Text between x0 and x1 in each row. Each row of a bar section is one
    colour (only its alpha fades at the ends), and the ends (ref, columns no
    text reaches) show it: everything else in the row is text, which takes
    the bar's colour and keeps its alpha."""
    out = rgba.copy()
    mask = np.zeros(rgba.shape[:2], bool)
    for y in rows:
        a, b = x0(y), x1(y)
        seg = rgba[y, a:b, :3].astype(np.int64)
        if len(seg) == 0:
            continue
        colour = np.median(rgba[y, ref, :3].astype(np.int64), 0).round().astype(np.int64)
        text = np.abs(seg - colour).sum(1) > 9
        mask[y, a:b] = text
        out[y, a:b, :3][text] = colour
    return out, mask


def text_colours(rgba, mask):
    px = rgba[mask][:, :3].astype(float)
    light = px.sum(1)
    order = np.argsort(light)
    dark = px[order[: len(order) // 6]].mean(0)
    bright = px[order[-len(order) // 4:]].mean(0)
    mid = px[order[len(order) // 2: len(order) * 3 // 4]].mean(0)
    return tuple(int(v) for v in dark), tuple(int(v) for v in bright), tuple(int(v) for v in mid)


def lettering(text, height, dark, top, bottom, width_limit):
    """The text as RGBA: gradient fill, outline, shadow, slanted."""
    size = height
    while True:
        font = ImageFont.truetype(FONT, size)
        font.set_variation_by_axes([900])
        box = font.getbbox(text)
        if box[2] - box[0] <= width_limit or size <= 12:
            break
        size -= 1
    w, h = box[2] - box[0] + 16, box[3] - box[1] + 12
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).text((8 - box[0], 6 - box[1]), text, font=font, fill=255)
    outline = m.filter(ImageFilter.MaxFilter(5))
    shadow = outline.filter(ImageFilter.MaxFilter(3))
    grad = np.linspace(0, 1, h)[:, None, None]
    fill = (np.array(top) * (1 - grad) + np.array(bottom) * grad) * np.ones((1, w, 1))
    img = np.zeros((h, w, 4), float)
    def over(colour, alpha, dx=0, dy=0):
        a = np.roll(np.roll(np.asarray(alpha, float) / 255, dy, 0), dx, 1)[..., None]
        img[..., :3] = colour * a + img[..., :3] * (1 - a)
        img[..., 3:] = a * 255 + img[..., 3:] * (1 - a)
    over(np.array((20, 20, 40)), np.asarray(shadow) * 0.6, 2, 2)
    over(np.array(dark), outline)
    over(fill, m)
    out = Image.fromarray(img.round().clip(0, 255).astype(np.uint8), 'RGBA')
    return out.transform(out.size, Image.AFFINE, (1, 0.22, -0.11 * h, 0, 1, 0), Image.BICUBIC)


def paste(base, layer, cx, cy):
    x, y = cx - layer.width // 2, cy - layer.height // 2
    canvas = Image.fromarray(base, 'RGBA')
    canvas.alpha_composite(layer, (max(0, x), max(0, y)))
    return np.asarray(canvas)


def banner(path, course, grade, slant):
    rgba = np.asarray(Image.open(path).convert('RGBA'))
    rows = range(1, 52)
    left, lmask = erase(rgba, lambda y: 58, lambda y: slant(y) - 6, rows, slice(48, 58))
    both, rmask = erase(left, lambda y: slant(y) + 6, lambda y: 740, rows, slice(742, 760))
    lys, lxs = np.where(lmask)
    rys, rxs = np.where(rmask)
    ldark, lbright, lmid = text_colours(rgba, lmask)
    rdark, rbright, rmid = text_colours(rgba, rmask)
    out = paste(both, lettering(course, 40, ldark, lbright, lmid, slant(26) - 110),
                (lxs.min() + lxs.max()) // 2, (lys.min() + lys.max()) // 2 + 1)
    out = paste(out, lettering(grade, 30, rdark, rbright, rmid, 200),
                (rxs.min() + rxs.max()) // 2, (rys.min() + rys.max()) // 2 + 1)
    return Image.fromarray(out, 'RGBA')


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    previews = []
    # Every banner has the same layout; the first one's colours show the slant best.
    slant = slant_of(np.asarray(Image.open(next(src.glob('advJ_00_1024x64.png'))).convert('RGBA')))
    for n in range(16):
        path = next(src.glob(f'advJ_{n:02d}_1024x64.png'))
        image = banner(path, COURSES[n % 8], GRADES[n // 8], slant)
        image.save(dst / f'advJ_{n:02d}.png')
        previews.append(image)
    if '--preview' in sys.argv:
        sheet = Image.new('RGBA', (1024, 64 * 16), (50, 50, 50, 255))
        for n, image in enumerate(previews):
            sheet.alpha_composite(image, (0, 64 * n))
        sheet.save(dst / 'preview.png')
    return 0


if __name__ == '__main__':
    sys.exit(main())
