# resume-tailor

Local tool for tailoring a one-page LaTeX SWE resume to a pasted job description.

## Goal

Keep the resume truthful and structurally stable while improving keyword match.

## Guardrails

- Do not invent experience.
- Prefer editing skills and existing technology phrasing in bullets.
- Keep bullet count unchanged unless explicitly approved.
- Preserve one-page output.
- Show a diff before the user accepts changes.

## CLI

Local personal files are ignored by git:

- `resume.tex` — your real LaTeX resume
- `job.txt` — pasted job description
- `approved.txt` — truthful extra skills the tool may add
- `tailored.tex` — generated LaTeX output
- `tailored.pdf` — generated PDF output
- `tailored.diff` — exact LaTeX diff
- `suggestions.txt` — safe bullet suggestions only
- `library/` — local SQLite DB plus saved resume folders

Fast path:

```bash
python3 -m resume_tailor paste
# paste JD, then press Ctrl-D
# writes tailored.tex, tailored.pdf, tailored.diff, suggestions.txt
# opens tailored.pdf automatically
```

File path:

```bash
pbpaste > job.txt
python3 -m resume_tailor inspect
python3 -m resume_tailor tailor
```

Explicit example path:

```bash
python3 -m resume_tailor tailor \
  --resume examples/current_resume.tex \
  --job examples/job.txt \
  --approved examples/approved.txt \
  --out tailored.tex
```

`--approved` is optional. If omitted, the CLI uses `approved.txt` when it exists.

## Local browser UI

```bash
cd ~/resume-tailor
python3 -m resume_tailor.ui
```

Then paste a JD in the browser and either:

- click `Find Existing Resume` to search your saved local library
- click `Generate New PDF` to tailor a new one

Generated resumes get an editable suggested name like `kubernetes-aws-go-typescript`, then save into the library with keywords, date, PDF link, and delete action. The folder slug is shown only as a storage ID.

## Clickable Mac app

Build/install once:

```bash
cd ~/resume-tailor
python3 scripts/build_mac_app.py
open "$HOME/Applications/Resume Tailor.app"
```

You can drag `$HOME/Applications/Resume Tailor.app` to the Dock. It launches the local browser UI.

## Test

```bash
python3 tests/run.py
```

## Current limits

- Edits the Technical Skills block.
- Safely updates bullet technology phrasing when the underlying work stays the same, e.g. `APIs` → `REST APIs`, `backend services in Go` → `Kubernetes-backed backend services in Go` only when those technologies already appear in your resume.
- Bullet edits that would add new claims remain suggestions only.
- PDF compile uses Tectonic; it strips pdfTeX-only ATS lines from the temporary compile copy only.
