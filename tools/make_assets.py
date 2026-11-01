# -*- coding: utf-8 -*-
"""ساخت assets.js و questions.js  —  python tools/make_assets.py
نام جواب = نام فایل (بدون پسوند). پیشوند شماره مثل «01-» حذف و «_» به فاصله تبدیل می‌شود.
اگر questions.csv کنار index.html باشد، به questions.js تبدیل می‌شود."""
import os, re, json
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg')
SND = ('.mp3', '.wav', '.ogg', '.m4a', '.aac', '.webm')
def scan(folder, exts):
    out = []
    d = os.path.join(base, folder)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        stem, ext = os.path.splitext(f)
        if ext.lower() in exts:
            name = re.sub(r'^[0-9]+[-_ .]+', '', stem).replace('_', ' ').strip() or stem
            out.append({'file': folder + '/' + f, 'name': name})
    return out
def build_assets():
    assets = {'images': scan('images', IMG), 'sounds': scan('sounds', SND)}
    with open(os.path.join(base, 'assets.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.PARTY_ASSETS = ' + json.dumps(assets, ensure_ascii=False, indent=1) + ';\n')
    return assets
def build_questions():
    q = os.path.join(base, 'questions.csv')
    txt = open(q, encoding='utf-8-sig').read() if os.path.exists(q) else ''
    with open(os.path.join(base, 'questions.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.PARTY_QUESTIONS = ' + json.dumps(txt, ensure_ascii=False) + ';\n')
    return bool(txt)
if __name__ == '__main__':
    a = build_assets(); q = build_questions()
    print('images:', len(a['images']), '| sounds:', len(a['sounds']), '| questions.csv:', 'yes' if q else 'no')
