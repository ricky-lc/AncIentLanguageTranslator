import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from backend.translator import translate_to_ancient_language

MAX_REQUEST_SIZE = 1_000_000
INDEX_HTML = Path(__file__).resolve().parent.parent.joinpath("index.html")


class TranslatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        content = INDEX_HTML.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path != "/api/translate":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > MAX_REQUEST_SIZE:
            self.send_response(413)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Payload too large"}).encode("utf-8"))
            return

        raw_body = self.rfile.read(content_length)
        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            body = {}

        result = translate_to_ancient_language(body.get("text", ""))
        payload = json.dumps(result, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def run_server():
    port = int(os.getenv("PORT", "3000"))
    server = ThreadingHTTPServer(("", port), TranslatorHandler)
    print(f"Translator running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
