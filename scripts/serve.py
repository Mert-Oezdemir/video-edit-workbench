#!/usr/bin/env python3
"""Static file server with HTTP Range support (browsers need it to seek inside video files).

usage: python3 scripts/serve.py --project . [--port 5600]   ->  http://127.0.0.1:5600/scene/
"""
import argparse
import http.server
import os
import re


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def send_head(self):
        rng = self.headers.get('Range')
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r'bytes=(\d*)-(\d*)', rng)
        size = os.path.getsize(path)
        if not m:
            return super().send_head()
        start = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2) or 0))
        end = int(m.group(2)) if m.group(1) and m.group(2) else size - 1
        if start >= size:
            self.send_error(416)
            return None
        end = min(end, size - 1)
        f = open(path, 'rb')
        f.seek(start)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, '_remaining', None)
        if left is None:
            return super().copyfile(source, outputfile)
        try:
            while left > 0:
                buf = source.read(min(1 << 16, left))
                if not buf:
                    break
                outputfile.write(buf)
                left -= len(buf)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self._remaining = None

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', default='.')
    ap.add_argument('--port', type=int, default=5600)
    a = ap.parse_args()
    os.chdir(os.path.abspath(a.project))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', a.port), RangeHandler)
    print(f'serving {os.getcwd()} on http://127.0.0.1:{a.port}/scene/')
    srv.serve_forever()
