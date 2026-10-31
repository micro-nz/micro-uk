#!/usr/bin/env python3
"""Serve dist/ the way GitHub Pages will: under /micro-uk/, with 404.html for missing paths.

    python3 tools/serve.py [port]
"""
import http.server, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist")
BASE = os.environ.get("SITE_BASE", "/micro-uk")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def send_head(self):
        path = self.path.split("?")[0].split("#")[0]
        if path in ("", "/"):
            self.send_response(302); self.send_header("Location", BASE + "/"); self.end_headers(); return None
        if not path.startswith(BASE + "/") and path != BASE:
            return self._not_found()
        self.path = self.path[len(BASE):] or "/"
        local = self.translate_path(self.path)
        if os.path.isdir(local) and not os.path.exists(os.path.join(local, "index.html")):
            return self._not_found()
        if not os.path.exists(local):
            return self._not_found()
        return super().send_head()

    def _not_found(self):
        body = open(os.path.join(ROOT, "404.html"), "rb").read()
        self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers()
        return __import__("io").BytesIO(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/__selftest.js":  # the browser self-test, served outside the site
            body = open(os.path.join(ROOT, "..", "tests", "selftest.js"), "rb").read()
            self.send_response(200); self.send_header("Content-Type", "text/javascript"); self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body); return
        return super().do_GET()

    def do_POST(self):
        if self.path != "/__selftest":
            self.send_error(404); return
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        os.makedirs(os.path.join(ROOT, "..", "reports"), exist_ok=True)
        with open(os.path.join(ROOT, "..", "reports", "runtime.json"), "wb") as f:
            f.write(data)
        self.send_response(204); self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
