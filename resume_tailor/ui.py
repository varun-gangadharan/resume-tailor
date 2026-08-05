from __future__ import annotations

import html
import json
import mimetypes
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .pdf import compile_pdf
from .tailor import bullet_suggestions, tailor

ROOT = Path.cwd()
FILES = {
    "tailored.pdf": "tailored.pdf",
    "tailored.tex": "tailored.tex",
    "tailored.diff": "tailored.diff",
    "suggestions.txt": "suggestions.txt",
}


@dataclass(frozen=True)
class UiResult:
    additions: dict[str, list[str]]
    suggestions: list[str]
    pages: int | None
    diff: str


def run_tailor(job_text: str, root: Path = ROOT) -> UiResult:
    resume = root / "resume.tex"
    approved = root / "approved.txt"
    out = root / "tailored.tex"
    diff = root / "tailored.diff"
    suggestions_path = root / "suggestions.txt"
    pdf = root / "tailored.pdf"

    result = tailor(resume.read_text(), job_text, approved.read_text() if approved.exists() else "")
    out.write_text(result.tex)
    diff.write_text(result.diff or "")
    suggestions = bullet_suggestions(job_text, result.tex)
    suggestions_path.write_text("\n".join(suggestions) + ("\n" if suggestions else ""))
    pdf_result = compile_pdf(out, pdf)
    return UiResult(result.additions, suggestions, pdf_result.pages, result.diff)


def _page(body: str) -> bytes:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Resume Tailor</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px auto; max-width: 900px; line-height: 1.4; }}
    textarea {{ width: 100%; height: 320px; font: 14px ui-monospace, SFMono-Regular, Menlo, monospace; }}
    button {{ font-size: 16px; padding: 10px 14px; }}
    pre {{ background: #f6f6f6; padding: 12px; overflow: auto; }}
    .ok {{ color: #067d17; font-weight: 700; }}
    .warn {{ color: #9a6700; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Resume Tailor</h1>
  {body}
</body>
</html>""".encode()


def form(message: str = "") -> bytes:
    safe_message = f"<p class='ok'>{html.escape(message)}</p>" if message else ""
    return _page(f"""
{safe_message}
<form method="post" action="/tailor">
  <p>Paste job description:</p>
  <textarea name="job" autofocus></textarea>
  <p><button type="submit">Tailor Resume → PDF</button></p>
</form>
<p>Uses local <code>resume.tex</code> and optional <code>approved.txt</code>. Nothing leaves your computer.</p>
""")


def result_page(result: UiResult) -> bytes:
    pages = "unknown" if result.pages is None else str(result.pages)
    page_class = "ok" if result.pages == 1 else "warn"
    additions = html.escape(json.dumps(result.additions, indent=2))
    suggestions = "\n".join(f"- {s}" for s in result.suggestions) or "No missing truthful bullet keywords found."
    diff = html.escape(result.diff or "No safe skills edits made.")
    return _page(f"""
<p class="{page_class}">PDF generated: {pages} page{'s' if result.pages != 1 else ''}</p>
<p>
  <a href="/files/tailored.pdf">Open PDF</a> |
  <a href="/files/tailored.tex">LaTeX</a> |
  <a href="/files/tailored.diff">Diff</a> |
  <a href="/files/suggestions.txt">Suggestions</a> |
  <a href="/">Tailor another</a>
</p>
<h2>Added skills</h2>
<pre>{additions}</pre>
<h2>Safe bullet suggestions</h2>
<pre>{html.escape(suggestions)}</pre>
<h2>Diff</h2>
<pre>{diff}</pre>
""")


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(200, form())
            return
        if parsed.path.startswith("/files/"):
            name = Path(parsed.path).name
            if name not in FILES:
                self._send(404, b"not found", "text/plain")
                return
            path = ROOT / FILES[name]
            if not path.exists():
                self._send(404, b"not generated yet", "text/plain")
                return
            self._send(200, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            return
        self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/tailor":
            self._send(404, b"not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length", "0"))
        data = parse_qs(self.rfile.read(length).decode())
        job = data.get("job", [""])[0].strip()
        if not job:
            self._send(400, form("Paste a job description first."))
            return
        try:
            self._send(200, result_page(run_tailor(job)))
        except Exception as exc:  # noqa: BLE001 - show local failure in browser
            self._send(500, _page(f"<p class='warn'>Failed:</p><pre>{html.escape(str(exc))}</pre><p><a href='/'>Back</a></p>"))

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    url = "http://127.0.0.1:8765"
    print(f"Resume Tailor running at {url}")
    webbrowser.open(url)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
