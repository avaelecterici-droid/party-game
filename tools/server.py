# -*- coding: utf-8 -*-
"""سرور محلی بازی: پوشه را سرو می‌کند و عکس/صدای اضافه‌شده از داخل بازی را مستقیم در images/ و sounds/ ذخیره می‌کند.
اجرا:  python tools/server.py   (یا start-server را دوبار کلیک کنید)"""
import os, sys, re, json, socket, mimetypes, threading, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_assets as MA
BASE = MA.base
EXT = {'images': {'jpg', 'jpeg', 'png', 'webp', 'gif', 'svg'}, 'sounds': {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'webm'}}
MAXB = 60 * 1024 * 1024
for t, e in (('audio/mp4', '.m4a'), ('audio/aac', '.aac'), ('audio/webm', '.webm'), ('image/webp', '.webp'), ('image/svg+xml', '.svg'), ('text/javascript', '.js')):
    mimetypes.add_type(t, e)
def clean(n):
    return re.sub(r'[\\/:*?"<>|\x00-\x1f]', '', n).strip(' .')[:80] or 'untitled'
class H(SimpleHTTPRequestHandler):
    def __init__(s, *a, **k):
        super().__init__(*a, directory=BASE, **k)
    def end_headers(s):
        s.send_header('Cache-Control', 'no-store'); super().end_headers()
    def log_message(s, *a): pass
    def _json(s, o, c=200):
        b = json.dumps(o, ensure_ascii=False).encode('utf-8')
        s.send_response(c); s.send_header('Content-Type', 'application/json; charset=utf-8')
        s.send_header('Content-Length', str(len(b))); s.end_headers(); s.wfile.write(b)
    def do_GET(s):
        if urlparse(s.path).path == '/api/ping':
            return s._json({'ok': 1, 'assets': MA.build_assets()})
        super().do_GET()
    def do_POST(s):
        u = urlparse(s.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        kind = q.get('kind')
        if kind not in EXT: return s._json({'ok': 0, 'error': 'bad kind'}, 400)
        folder = os.path.join(BASE, kind); os.makedirs(folder, exist_ok=True)
        try:
            if u.path == '/api/upload':
                ext = re.sub(r'[^a-z0-9]', '', q.get('ext', '').lower())
                if ext not in EXT[kind]: return s._json({'ok': 0, 'error': 'فرمت پشتیبانی نمی‌شود: ' + ext}, 400)
                n = int(s.headers.get('Content-Length', 0))
                if n <= 0 or n > MAXB: return s._json({'ok': 0, 'error': 'حجم فایل نامعتبر است'}, 413)
                data = s.rfile.read(n); name = clean(q.get('name', ''))
                fn = f'{name}.{ext}'; i = 2
                while os.path.exists(os.path.join(folder, fn)): fn = f'{name} ({i}).{ext}'; i += 1
                with open(os.path.join(folder, fn), 'wb') as f: f.write(data)
                return s._json({'ok': 1, 'assets': MA.build_assets()})
            if u.path == '/api/delete':
                fn = os.path.basename(q.get('file', '')); p = os.path.join(folder, fn)
                if fn.rsplit('.', 1)[-1].lower() in EXT[kind] and os.path.isfile(p): os.remove(p)
                return s._json({'ok': 1, 'assets': MA.build_assets()})
        except Exception as e:
            return s._json({'ok': 0, 'error': str(e)}, 500)
        s._json({'ok': 0, 'error': 'not found'}, 404)
def lan():
    try:
        so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); so.connect(('8.8.8.8', 80)); ip = so.getsockname()[0]; so.close(); return ip
    except Exception: return '127.0.0.1'
if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    MA.build_assets(); MA.build_questions()
    print('\n  Party game server is running. Press Ctrl+C to stop.')
    print('  On this computer :  http://localhost:%d' % port)
    print('  On phone/TV (same Wi-Fi):  http://%s:%d\n' % (lan(), port))
    threading.Timer(1.0, lambda: webbrowser.open('http://localhost:%d' % port)).start()
    try: ThreadingHTTPServer(('0.0.0.0', port), H).serve_forever()
    except KeyboardInterrupt: print('bye')
