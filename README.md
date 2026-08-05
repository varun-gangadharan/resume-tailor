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

```bash
python3 -m resume_tailor inspect --resume examples/current_resume.tex
python3 -m resume_tailor keywords --job examples/job.txt
python3 -m resume_tailor tailor \
  --resume examples/current_resume.tex \
  --job examples/job.txt \
  --approved examples/approved.txt \
  --out tailored.tex
```

`--approved` is optional. Use it for truthful extra skills that are not already in the resume text.

## Test

```bash
python3 tests/run.py
```

## Current limits

- Edits the Technical Skills block only.
- Does not rewrite bullets yet.
- Does not compile PDFs yet.
