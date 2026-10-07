#!/usr/bin/env python3
"""Make source/ and units/ from your own game files (they are not in this repository).

    python tools/prepare.py <decompressed Japanese files> <decompressed English files> <FreeRidersRecompiled checkout>

The two directories hold the decompressed font files of each language
(advJ, gxfJ, gxfrJ, pauseFJ, resiFJ, FNT_SJ, s08tfJ and the same with E), made
with the checkout's SFR_DUMP_DECOMPRESSED and scripts/unpack_assets.py (see
README). This exports their strings, writes source/<file>.json (id, Japanese,
English) and units/all.json, the distinct Japanese strings the translations
in zh/ are keyed by. The units come out in the same order every time, so
their ids match zh/.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# In this order: the ids of the units follow it.
FILES = ['adv', 'gxf', 'gxfr', 'pauseF', 'resiF', 'FNT_S', 's08tf']


def export(checkout, path, out):
    subprocess.run([sys.executable, str(checkout / 'scripts' / 'sfr_font_text.py'), 'export', str(path), str(out)],
                   check=True, stdout=subprocess.DEVNULL)
    return json.loads(out.read_text(encoding='utf-8'))


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    ja_dir, en_dir, checkout = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    (ROOT / 'source').mkdir(exist_ok=True)
    (ROOT / 'units').mkdir(exist_ok=True)
    units, by_ja = [], {}
    with tempfile.TemporaryDirectory() as tmp:
        for base in FILES:
            ja = export(checkout, ja_dir / f'{base}J', Path(tmp) / 'ja.json')
            en = export(checkout, en_dir / f'{base}E', Path(tmp) / 'en.json')
            if len(ja) != len(en):
                raise SystemExit(f'{base}: {len(ja)} Japanese strings, {len(en)} English')
            rows = [dict(id=i, ja=j, en=e) for i, (j, e) in enumerate(zip(ja, en))]
            (ROOT / 'source' / f'{base}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                                         encoding='utf-8')
            for row in rows:
                if base == 'FNT_S' and row['id'] == 0:
                    continue  # the name-entry character set, kept as it is
                unit = by_ja.get(row['ja'])
                if unit is None:
                    unit = by_ja[row['ja']] = dict(unit='u%04d' % (len(units) + 1), ja=row['ja'], en=[], where=[])
                    units.append(unit)
                if row['en'] not in unit['en']:
                    unit['en'].append(row['en'])
                unit['where'].append(f'{base}:{row["id"]}')
    (ROOT / 'units' / 'all.json').write_text(json.dumps(units, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(units)} units from {len(FILES)} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
