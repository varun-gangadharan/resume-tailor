# resume-tailor

Local tool for tailoring a one-page LaTeX SWE resume to a pasted job description.

## Goal

Keep the resume truthful and structurally stable while improving keyword match.

## Guardrails

- Do not invent experience.
- Prefer editing skills and existing technology phrasing.
- Keep bullet count unchanged unless explicitly approved.
- Preserve one-page output.
- Show a diff before the user accepts changes.

## CLI

Local personal files are ignored by git:

- `resume.tex` — your real LaTeX resume
- `job.txt` — pasted job description
- `approved.txt` — truthful extra skills the tool may add
- `tailored.tex` — generated output

Fast path:

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

## Test

```bash
python3 tests/run.py
```

## Current limits

- Edits the Technical Skills block only.
- Does not rewrite bullets yet.
- Does not compile PDFs yet.
