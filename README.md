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

## Planned CLI

```bash
resume-tailor tailor --resume ~/Desktop/current_resume.tex --job job.txt --out tailored.tex
resume-tailor diff --before resume.tex --after tailored.tex
```

## Build phases

1. Inspect the Desktop and Downloads resume LaTeX files.
2. Detect resume sections and existing technology claims.
3. Extract SWE keywords from a job description.
4. Apply safe LaTeX edits to skills and existing bullets.
5. Validate with tests, diff output, and optional PDF compile/page count.
