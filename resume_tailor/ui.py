from __future__ import annotations

import html
import json
import mimetypes
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .library import ResumeLibrary, SavedResume, suggested_name
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
    suggested_name: str = ""


def run_tailor(job_text: str, root: Path = ROOT) -> UiResult:
    resume = root / "resume.tex"
    approved = root / "approved.txt"
    out = root / "tailored.tex"
    diff = root / "tailored.diff"
    suggestions_path = root / "suggestions.txt"
    pdf = root / "tailored.pdf"

    (root / "job.txt").write_text(job_text)
    result = tailor(resume.read_text(), job_text, approved.read_text() if approved.exists() else "")
    out.write_text(result.tex)
    diff.write_text(result.diff or "")
    suggestions = bullet_suggestions(job_text, result.tex)
    suggestions_path.write_text("\n".join(suggestions) + ("\n" if suggestions else ""))
    pdf_result = compile_pdf(out, pdf)
    return UiResult(result.additions, suggestions, pdf_result.pages, result.diff, suggested_name(job_text, result.tex))


def library_matches(job_text: str, root: Path = ROOT) -> list[SavedResume]:
    return ResumeLibrary(root).match(job_text)


def _page(body: str) -> bytes:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Resume Tailor</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f1eb;
      --ink: #191713;
      --muted: #70685d;
      --line: #ddd4c6;
      --panel: #fffaf1;
      --panel-strong: #ffffff;
      --accent: #245c4f;
      --accent-ink: #ffffff;
      --warn: #9a5b00;
      --ok: #1f6b45;
      --shadow: 0 24px 70px rgba(50, 42, 28, .12);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100dvh;
      color: var(--ink);
      font: 16px/1.5 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(36, 92, 79, .16), transparent 32rem),
        linear-gradient(135deg, #fbf7ef 0%, var(--bg) 54%, #ebe3d6 100%);
    }}
    a {{ color: var(--accent); font-weight: 750; text-decoration-thickness: .08em; text-underline-offset: .22em; }}
    .shell {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }}
    .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 28px; }}
    .brand {{ display: flex; align-items: center; gap: 12px; color: inherit; text-decoration: none; }}
    .mark {{ display: grid; place-items: center; width: 42px; height: 42px; border-radius: 14px; background: var(--ink); color: #fffaf1; font-weight: 900; letter-spacing: -.04em; box-shadow: var(--shadow); }}
    h1 {{ margin: 0; font-size: clamp(1.8rem, 4vw, 3.7rem); line-height: .94; letter-spacing: -.07em; max-width: 720px; }}
    h2 {{ margin: 0 0 14px; font-size: clamp(1.25rem, 2vw, 1.65rem); letter-spacing: -.035em; }}
    p {{ margin: 0 0 16px; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 0; }}
    .nav a {{ padding: 10px 14px; border: 1px solid var(--line); border-radius: 999px; background: rgba(255, 250, 241, .72); color: var(--ink); text-decoration: none; }}
    .hero {{ display: grid; grid-template-columns: minmax(0, 1.08fr) minmax(280px, .92fr); gap: 24px; align-items: stretch; margin-bottom: 24px; }}
    .intro, .panel {{ border: 1px solid rgba(221, 212, 198, .9); border-radius: var(--radius); background: rgba(255, 250, 241, .82); box-shadow: var(--shadow); }}
    .intro {{ padding: clamp(24px, 5vw, 52px); display: flex; flex-direction: column; justify-content: space-between; min-height: 360px; }}
    .kicker {{ display: inline-flex; width: fit-content; margin-bottom: 24px; padding: 7px 10px; border: 1px solid var(--line); border-radius: 999px; color: var(--accent); font-size: .78rem; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }}
    .lede {{ margin-top: 18px; max-width: 58ch; font-size: 1.05rem; }}
    .panel {{ padding: clamp(18px, 3vw, 28px); }}
    .stack {{ display: grid; gap: 18px; }}
    label, .label {{ display: block; margin-bottom: 8px; color: var(--ink); font-weight: 800; }}
    textarea, input {{ width: 100%; border: 1px solid var(--line); border-radius: 16px; background: rgba(255, 255, 255, .76); color: var(--ink); font: inherit; box-shadow: inset 0 1px 0 rgba(255, 255, 255, .75); }}
    textarea {{ min-height: 320px; padding: 16px; resize: vertical; font: 14px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace; }}
    input {{ max-width: 340px; padding: 12px 14px; }}
    textarea:focus, input:focus {{ outline: 3px solid rgba(36, 92, 79, .18); border-color: var(--accent); }}
    .actions, .links {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
    button, .button {{ appearance: none; border: 1px solid var(--ink); border-radius: 999px; padding: 12px 17px; background: var(--ink); color: var(--accent-ink); font: inherit; font-weight: 850; cursor: pointer; text-decoration: none; transition: transform .16s ease, box-shadow .16s ease, background .16s ease; }}
    button:hover, .button:hover {{ transform: translateY(-1px); box-shadow: 0 14px 30px rgba(25, 23, 19, .16); }}
    button:active, .button:active {{ transform: translateY(1px); box-shadow: none; }}
    button.secondary, .button.secondary {{ background: transparent; color: var(--ink); border-color: var(--line); }}
    .note {{ margin-top: 14px; font-size: .94rem; }}
    .ok, .warn {{ padding: 12px 14px; border-radius: 16px; font-weight: 850; }}
    .ok {{ color: var(--ok); background: rgba(31, 107, 69, .09); }}
    .warn {{ color: var(--warn); background: rgba(154, 91, 0, .1); }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 18px; }}
    pre {{ margin: 0; max-height: 360px; overflow: auto; padding: 16px; border: 1px solid var(--line); border-radius: 18px; background: #191713; color: #f8f0df; font: 13px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre-wrap; }}
    table {{ width: 100%; border-collapse: separate; border-spacing: 0; overflow: hidden; border: 1px solid var(--line); border-radius: 18px; background: rgba(255, 255, 255, .55); }}
    th, td {{ padding: 14px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }}
    th {{ color: var(--muted); font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{ padding: 2px 6px; border-radius: 8px; background: rgba(36, 92, 79, .1); color: var(--accent); }}
    @media (max-width: 760px) {{
      .shell {{ width: min(100% - 20px, 1120px); padding-top: 14px; }}
      .topbar, .hero, .grid {{ grid-template-columns: 1fr; display: grid; }}
      .topbar {{ gap: 14px; }}
      .nav {{ justify-content: start; }}
      .intro {{ min-height: auto; }}
      input {{ max-width: none; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <a class="brand" href="/"><span class="mark">RT</span><strong>Resume Tailor</strong></a>
      <nav class="nav" aria-label="Primary"><a href="/">Tailor</a><a href="/library">Library</a></nav>
    </header>
    {body}
  </main>
</body>
</html>""".encode()


def form(message: str = "") -> bytes:
    safe_message = f"<p class='ok'>{html.escape(message)}</p>" if message else ""
    return _page(f"""
{safe_message}
<section class="hero">
  <div class="intro">
    <div>
      <span class="kicker">Local resume lab</span>
      <h1>Tailor one resume without making anything up.</h1>
      <p class="lede">Paste a role, compare saved versions, then generate a one-page PDF from your local LaTeX resume.</p>
    </div>
    <p class="note">Uses local <code>resume.tex</code> and optional <code>approved.txt</code>. Nothing leaves your computer.</p>
  </div>
  <form class="panel stack" method="post">
    <div>
      <label for="job">Paste job description</label>
      <textarea id="job" name="job" autofocus></textarea>
    </div>
    <div class="actions">
      <button class="secondary" formaction="/match" type="submit">Find Existing Resume</button>
      <button formaction="/tailor" type="submit">Generate New PDF</button>
    </div>
  </form>
</section>
""")


def _links() -> str:
    return """
<div class="links">
  <a class="button" href="/files/tailored.pdf">Open PDF</a>
  <a class="button secondary" href="/files/tailored.tex">LaTeX</a>
  <a class="button secondary" href="/files/tailored.diff">Diff</a>
  <a class="button secondary" href="/files/suggestions.txt">Suggestions</a>
  <a class="button secondary" href="/">Tailor another</a>
</div>
"""


def result_page(result: UiResult) -> bytes:
    pages = "unknown" if result.pages is None else str(result.pages)
    page_class = "ok" if result.pages == 1 else "warn"
    additions = html.escape(json.dumps(result.additions, indent=2))
    suggestions = "\n".join(f"- {s}" for s in result.suggestions) or "No missing truthful bullet keywords found."
    diff = html.escape(result.diff or "No safe skills edits made.")
    return _page(f"""
<section class="panel stack">
  <p class="{page_class}">PDF generated: {pages} page{'s' if result.pages != 1 else ''}</p>
  {_links()}
  <form class="actions" method="post" action="/save">
    <input name="name" value="{html.escape(result.suggested_name)}" placeholder="backend-go-vault" aria-label="Library name">
    <button type="submit">Save to Library</button>
  </form>
  <div class="grid">
    <section class="stack"><h2>Added skills</h2><pre>{additions}</pre></section>
    <section class="stack"><h2>Safe bullet suggestions</h2><pre>{html.escape(suggestions)}</pre></section>
  </div>
  <section class="stack"><h2>Diff</h2><pre>{diff}</pre></section>
</section>
""")


def matches_page(matches: list[SavedResume], job_text: str) -> bytes:
    rows = []
    for m in matches:
        rows.append(
            f"<tr><td><strong>{html.escape(m.name)}</strong><br><small>{html.escape(m.slug)}</small></td><td>{int(m.score * 100)}%</td>"
            f"<td>{html.escape(', '.join(m.matched[:10]))}</td>"
            f"<td>{html.escape(', '.join(m.missing[:10]))}</td>"
            f"<td><a class='button secondary' href='/saved/{html.escape(m.slug)}/resume.pdf'>Open PDF</a></td></tr>"
        )
    table = "".join(rows) or "<tr><td colspan='5'>No saved resumes yet.</td></tr>"
    return _page(f"""
<section class="panel stack">
  <h1>Existing resume matches</h1>
  <table><tr><th>Name</th><th>Score</th><th>Matched</th><th>Missing</th><th>PDF</th></tr>{table}</table>
  <form method="post" action="/tailor">
    <input type="hidden" name="job" value="{html.escape(job_text)}">
    <div class="actions"><button type="submit">Generate New PDF Instead</button></div>
  </form>
</section>
""")


def library_page(root: Path = ROOT, message: str = "") -> bytes:
    safe_message = f"<p class='ok'>{html.escape(message)}</p>" if message else ""
    rows = []
    for r in ResumeLibrary(root).list_resumes():
        tags = ", ".join(r.keywords[:12])
        date = r.created_at[:10] if r.created_at else ""
        rows.append(
            f"<tr><td><strong>{html.escape(r.name)}</strong><br><small>{html.escape(date)} · folder: {html.escape(r.slug)}</small></td>"
            f"<td>{html.escape(tags)}</td>"
            f"<td class='actions'><a class='button secondary' href='/saved/{html.escape(r.slug)}/resume.pdf'>Open PDF</a>"
            f"<form method='post' action='/delete' style='display:inline'><input type='hidden' name='id' value='{r.id}'><button class='secondary' type='submit'>Delete</button></form></td></tr>"
        )
    table = "".join(rows) or "<tr><td colspan='3'>No saved resumes yet.</td></tr>"
    return _page(f"""
{safe_message}
<section class="panel stack">
  <h1>Resume Library</h1>
  <p>Saved local versions, sorted newest first. Use folders only as storage IDs; names and keywords are what matter.</p>
  <table><tr><th>Resume</th><th>Keywords</th><th>Actions</th></tr>{table}</table>
</section>
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
        if parsed.path == "/library":
            self._send(200, library_page())
            return
        if parsed.path.startswith("/saved/"):
            parts = parsed.path.strip("/").split("/")
            if len(parts) == 3 and parts[2] == "resume.pdf":
                path = ROOT / "library" / "resumes" / parts[1] / "resume.pdf"
                if path.exists():
                    self._send(200, path.read_bytes(), "application/pdf")
                    return
            self._send(404, b"not found", "text/plain")
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

    def _form(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        return parse_qs(self.rfile.read(length).decode())

    def _job(self) -> str:
        return self._form().get("job", [""])[0].strip()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/save":
            data = self._form()
            name = data.get("name", [""])[0].strip()
            try:
                saved = ResumeLibrary(ROOT).save_resume(name, ROOT / "tailored.tex", ROOT / "tailored.pdf", (ROOT / "job.txt").read_text() if (ROOT / "job.txt").exists() else "")
                self._send(200, library_page(message=f"Saved {saved.name}."))
            except Exception as exc:  # noqa: BLE001
                self._send(500, _page(f"<p class='warn'>Failed:</p><pre>{html.escape(str(exc))}</pre><p><a href='/'>Back</a></p>"))
            return
        if self.path == "/delete":
            data = self._form()
            resume_id = int(data.get("id", ["0"])[0])
            ResumeLibrary(ROOT).delete_resume(resume_id)
            self._send(200, library_page(message="Deleted resume."))
            return
        if self.path in {"/tailor", "/match"}:
            job = self._job()
            if not job:
                self._send(400, form("Paste a job description first."))
                return
            try:
                if self.path == "/match":
                    (ROOT / "job.txt").write_text(job)
                    self._send(200, matches_page(library_matches(job), job))
                else:
                    self._send(200, result_page(run_tailor(job)))
            except Exception as exc:  # noqa: BLE001
                self._send(500, _page(f"<p class='warn'>Failed:</p><pre>{html.escape(str(exc))}</pre><p><a href='/'>Back</a></p>"))
            return
        self._send(404, b"not found", "text/plain")

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> int:
    url = "http://127.0.0.1:8765"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    except OSError:
        print(f"Resume Tailor already running at {url}")
        webbrowser.open(url)
        return 0
    print(f"Resume Tailor running at {url}")
    webbrowser.open(url)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
