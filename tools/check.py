#!/usr/bin/env python3
"""Check translations: python tools/check.py zh/<batch>.json [more ...]

Each file maps unit ids (u0001...) to Traditional Chinese. For each unit the
translation must
- have as many lines ("\\n") as the Japanese;
- fit each line in the Japanese line's width (+2), counting a full-width
  character as 1 and a half-width one as 0.5 (readings [base|reading] count
  as their base only);
- have no kana and no reading markup;
- keep {xx} control codes, and leading or trailing spaces, as the Japanese has them.
Prints the problems; exits 1 when there are any.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
units = {u['unit']: u for u in json.loads((ROOT / 'units' / 'all.json').read_text(encoding='utf-8'))}
KANA = re.compile(r'[ぁ-ゟ゠-ヺー-ヿｦ-ﾟ]')  # ・ (U+30FB) is allowed


def plain(s):
    return re.sub(r'\[([^|\]]*)\|[^\]]*\]', r'\1', s)


def width(s):
    return sum(1 if unicodedata.east_asian_width(c) in 'WF' else 0.5 for c in s)


def problems(unit, zh):
    ja = plain(unit['ja'])
    out = []
    if not isinstance(zh, str) or not zh.strip() and ja.strip():
        return ['empty']
    if zh.count('\n') != ja.count('\n'):
        out.append(f'{zh.count(chr(10)) + 1} lines, Japanese has {ja.count(chr(10)) + 1}')
    for a, b in zip(zh.split('\n'), ja.split('\n')):
        if width(a) > width(b) + 2:
            out.append(f'line too wide ({width(a)} > {width(b)} + 2): {a}')
    if KANA.search(zh):
        out.append('kana: ' + ''.join(KANA.findall(zh)))
    if '[' in zh and '|' in zh:
        out.append('reading markup')
    if re.findall(r'\{[0-9a-f]+\}', zh) != re.findall(r'\{[0-9a-f]+\}', ja):
        out.append('control codes differ')
    return out


def main():
    bad = 0
    for path in sys.argv[1:]:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        for uid, zh in data.items():
            if uid not in units:
                print(f'{path}: {uid}: unknown unit')
                bad += 1
                continue
            for p in problems(units[uid], zh):
                print(f'{path}: {uid}: {p}')
                bad += 1
    print(f'{bad} problems')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
