from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .models import instruction_catalog, load_defaults
from .package_builder import PackageBuildError, build_package


class OnboardingHandler(BaseHTTPRequestHandler):
    project_root: Path
    web_root: Path

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_file(self.web_root / "index.html")
            return
        if parsed.path == "/api/defaults":
            payload = {
                "defaults": load_defaults(self.project_root),
                "instructions": instruction_catalog(),
            }
            self._send_json(payload)
            return
        if parsed.path.startswith("/web/"):
            relative = unquote(parsed.path.removeprefix("/web/"))
            self._send_file(self.web_root / relative)
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/generate":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = build_package(self.project_root, payload)
        except PackageBuildError as error:
            self._send_json({"ok": False, "errors": error.errors}, status=422)
            return
        except Exception as error:  # pragma: no cover - defensive server boundary
            self._send_json({"ok": False, "errors": [str(error)]}, status=500)
            return
        self._send_json({"ok": True, **result})

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send_file(self, path: Path) -> None:
        try:
            resolved = path.resolve()
            resolved.relative_to(self.web_root.resolve())
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        if not resolved.is_file():
            self.send_error(404, "Not found")
            return
        content_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
        body = resolved.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Onboarding Agent")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    project_root = Path.cwd().resolve()
    web_root = project_root / "src" / "onboarding_app" / "web"
    OnboardingHandler.project_root = project_root
    OnboardingHandler.web_root = web_root

    server = ThreadingHTTPServer((args.host, args.port), OnboardingHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Onboarding Agent: {url}")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Onboarding Agent")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
