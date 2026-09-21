from __future__ import annotations

import html
import shutil
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

from .pdf import compile_pdf
from .tailor import bullet_suggestions, tailor

APP_DIR = Path(__file__).resolve().parent.parent
EXAMPLES = APP_DIR / "examples"
SESSIONS = Path("/tmp/resume-tailor-sessions")
SESSIONS.mkdir(parents=True, exist_ok=True)
SESSION_TTL_SECONDS = 3600

DEMO_RESUME = (EXAMPLES / "current_resume.tex").read_text()
DEMO_APPROVED = (EXAMPLES / "approved.txt").read_text() if (EXAMPLES / "approved.txt").exists() else ""

app = FastAPI(title="Resume Tailor (demo)")


def _shell(body: str) -> str:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Resume Tailor — demo</title>
  <style>
    :root {{ color-scheme: light; --bg:#f4f1eb; --ink:#191713; --muted:#70685d; --line:#ddd4c6;
      --panel:#fffaf1; --accent:#245c4f; --ok:#1f6b45; --warn:#9a5b00; --radius:20px; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; min-height:100dvh; color:var(--ink); font:16px/1.5 ui-sans-serif,-apple-system,sans-serif;
      background: linear-gradient(135deg,#fbf7ef 0%,var(--bg) 54%,#ebe3d6 100%); }}
    .shell {{ width:min(880px, calc(100% - 32px)); margin:0 auto; padding:32px 0 60px; }}
    a {{ color:var(--accent); font-weight:700; }}
    h1 {{ font-size:2rem; letter-spacing:-.03em; margin:0 0 6px; }}
    .banner {{ border:1px solid var(--line); border-radius:14px; background:rgba(255,250,241,.8);
      padding:12px 16px; margin-bottom:22px; font-size:.92rem; color:var(--muted); }}
    .panel {{ border:1px solid var(--line); border-radius:var(--radius); background:var(--panel);
      padding:22px; box-shadow:0 18px 50px rgba(50,42,28,.1); margin-bottom:18px; }}
    textarea {{ width:100%; min-height:260px; border:1px solid var(--line); border-radius:14px;
      padding:14px; font:14px/1.5 ui-monospace,Menlo,monospace; }}
    button {{ appearance:none; border:1px solid var(--ink); border-radius:999px; padding:11px 18px;
      background:var(--ink); color:#fffaf1; font-weight:800; cursor:pointer; margin-top:12px; }}
    pre {{ background:#191713; color:#f8f0df; padding:14px; border-radius:14px; overflow:auto;
      font:12.5px/1.5 ui-monospace,Menlo,monospace; white-space:pre-wrap; max-height:340px; }}
    .ok {{ color:var(--ok); font-weight:800; }}
    .warn {{ color:var(--warn); font-weight:800; }}
    .links a {{ margin-right:14px; }}
  </style>
</head>
<body><main class="shell">
  <h1><a href="/" style="text-decoration:none;color:inherit;">Resume Tailor</a></h1>
  <p class="banner">Public demo mode. Runs against a sample resume checked into the repo — not my
    real one — so the keyword-matching, diff, and PDF pipeline are exactly what runs locally,
    without publishing my actual resume. Source: <a href="https://github.com/varun-gangadharan/resume-tailor">GitHub</a>.</p>
  {body}
</main></body></html>"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _shell("""
<div class="panel">
  <form method="post" action="/tailor">
    <label for="job"><strong>Paste a job description</strong></label><br><br>
    <textarea id="job" name="job" placeholder="Paste a job posting here..."></textarea>
    <br><button type="submit">Tailor resume</button>
  </form>
</div>
""")


@app.get("/health", response_class=PlainTextResponse)
def health() -> str:
    return "ok"


def _cleanup_old_sessions() -> None:
    cutoff = time.time() - SESSION_TTL_SECONDS
    for child in SESSIONS.iterdir():
        try:
            if child.is_dir() and child.stat().st_mtime < cutoff:
                shutil.rmtree(child, ignore_errors=True)
        except FileNotFoundError:
            pass


@app.post("/tailor", response_class=HTMLResponse)
def tailor_endpoint(job: str = Form(...)) -> str:
    _cleanup_old_sessions()
    job = job.strip()
    if not job:
        return _shell('<div class="panel"><p class="warn">Paste a job description first.</p><p><a href="/">Back</a></p></div>')

    sid = uuid.uuid4().hex[:12]
    session_dir = SESSIONS / sid
    session_dir.mkdir(parents=True, exist_ok=True)

    result = tailor(DEMO_RESUME, job, DEMO_APPROVED)
    suggestions = bullet_suggestions(job, result.tex)

    tex_path = session_dir / "tailored.tex"
    tex_path.write_text(result.tex)

    pdf_note = ""
    pdf_link = ""
    try:
        pdf_result = compile_pdf(tex_path, session_dir / "tailored.pdf")
        pages = pdf_result.pages if pdf_result.pages is not None else "?"
        pdf_note = f'<p class="ok">PDF generated ({pages} page(s)).</p>'
        pdf_link = f'<a href="/result/{sid}/tailored.pdf">Open PDF</a>'
    except Exception as exc:  # noqa: BLE001
        pdf_note = f'<p class="warn">PDF compile failed on this instance:</p><pre>{html.escape(str(exc))}</pre>'

    additions = "\n".join(f"{k}: {', '.join(v)}" for k, v in result.additions.items()) or "No safe skill additions found for this JD."
    suggestions_txt = "\n".join(f"- {s}" for s in suggestions) or "No missing truthful bullet keywords found."
    diff = result.diff or "No skills-line edits made."

    return _shell(f"""
<div class="panel">
  {pdf_note}
  <div class="links">
    {pdf_link}
    <a href="/result/{sid}/tailored.tex">LaTeX</a>
    <a href="/">Tailor another</a>
  </div>
</div>
<div class="panel">
  <h3>Skill additions (from allow-listed terms already true of the sample resume)</h3>
  <pre>{html.escape(additions)}</pre>
</div>
<div class="panel">
  <h3>Bullet suggestions (not auto-applied — truthfulness stays a human call)</h3>
  <pre>{html.escape(suggestions_txt)}</pre>
</div>
<div class="panel">
  <h3>Diff</h3>
  <pre>{html.escape(diff)}</pre>
</div>
""")


@app.get("/result/{sid}/{filename}")
def result_file(sid: str, filename: str):
    if filename not in {"tailored.pdf", "tailored.tex"}:
        return PlainTextResponse("not found", status_code=404)
    if any(c in sid for c in "./\\"):
        return PlainTextResponse("bad session id", status_code=400)
    path = SESSIONS / sid / filename
    if not path.exists():
        return PlainTextResponse("not found or expired", status_code=404)
    media = "application/pdf" if filename.endswith(".pdf") else "text/plain"
    return FileResponse(path, media_type=media, filename=filename)
