#!/usr/bin/env python3
"""Build the mod: python tools/build.py <decompressed Japanese files> <FreeRidersRecompiled checkout> [out]

Reads every zh/*.json (unit id -> Chinese), puts each translation where its
unit is used (source/<file>.json), keeps the Japanese where a unit has none,
and builds <file>J with the checkout's scripts/sfr_font_text.py into
<out>/zh_tw (default: build/). The decompressed files come from
scripts/unpack_assets.py; they are the player's own, never committed here.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = 'C:/Windows/Fonts/NotoSansTC-VF.ttf'


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    originals, checkout = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[sys.argv.index('--title') + 1] if '--title' in sys.argv else None
    args = [a for i, a in enumerate(sys.argv) if a != '--title' and (i == 0 or sys.argv[i - 1] != '--title')]
    out = Path(args[3]) if len(args) > 3 else ROOT / 'build'
    zh = {}
    for path in sorted((ROOT / 'zh').glob('*.json')):
        zh.update(json.loads(path.read_text(encoding='utf-8')))
    units = json.loads((ROOT / 'units' / 'all.json').read_text(encoding='utf-8'))
    by_place = {}
    for u in units:
        if u['unit'] in zh:
            for place in u['where']:
                by_place[place] = zh[u['unit']]
    mod = out / 'zh_tw'
    mod.mkdir(parents=True, exist_ok=True)
    (mod / 'mod.ini').write_text(
        '[Desc]\nTitle="繁體中文化"\nAuthor="FreeRidersRecompiled-zhTW"\nVersion="0.3"\n'
        'Description="選單、劇情字幕與訊息的繁體中文翻譯。請在啟動器把遊戲語言設為日文。"\n\n'
        '[Main]\nIncludeDirCount=1\nIncludeDir0="."\n', encoding='utf-8')
    work = out / 'strings'
    work.mkdir(parents=True, exist_ok=True)
    total = done = 0
    for source in sorted((ROOT / 'source').glob('*.json')):
        base = source.stem
        rows = json.loads(source.read_text(encoding='utf-8'))
        texts = []
        for row in rows:
            text = by_place.get(f'{base}:{row["id"]}')
            total += 1
            done += text is not None
            texts.append(text if text is not None else row['ja'])
        strings = work / f'{base}J.json'
        strings.write_text(json.dumps(texts, ensure_ascii=False, indent=1), encoding='utf-8')
        subprocess.run([sys.executable, str(checkout / 'scripts' / 'sfr_font_text.py'), 'build',
                        str(originals / f'{base}J'), str(strings), FONT, str(mod / f'{base}J'), '--size', '20'],
                       check=True)
    print(f'translated {done} of {total} strings into {mod}')
    pictures(originals, checkout, out, mod, title)
    return 0


def pictures(originals, checkout, out, mod, title=None):
    """Text drawn in textures: the course banners and the logo's katakana
    (advJ), the tutorial's labels (s08tsuiJ). Each is drawn again from the
    original texture and written over it in place."""
    texture = [sys.executable, str(checkout / 'scripts' / 'sfr_texture.py')]
    tex, img = out / 'textures', out / 'pictures'
    for name in ('advJ', 's08tsuiJ'):
        subprocess.run(texture + ['extract', str(originals / name), str(tex)], check=True)
    tools = ROOT / 'tools'
    subprocess.run([sys.executable, str(tools / 'banners.py'), str(tex), str(img)], check=True)
    subprocess.run([sys.executable, str(tools / 'logo.py'), str(tex / 'advJ_17_1024x1024.png'),
                    str(img / 'advJ_17.png')] + ([title] if title else []), check=True)
    subprocess.run([sys.executable, str(tools / 'labels.py'), str(tex), str(img)], check=True)
    adv = [f'{n}={img / f"advJ_{n:02d}.png"}' for n in range(16)] + [f'17={img / "advJ_17.png"}']
    subprocess.run(texture + ['replace', str(mod / 'advJ')] + adv + ['-o', str(mod / 'advJ')], check=True)
    labels = [f'{n}={img / f"s08tsuiJ_{n:02d}.png"}' for n in (13, 14, 15, 16)]
    subprocess.run(texture + ['replace', str(originals / 's08tsuiJ')] + labels + ['-o', str(mod / 's08tsuiJ')],
                   check=True)


if __name__ == '__main__':
    sys.exit(main())
