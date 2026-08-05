# Local UI Plan

## Goal

A tiny local app where you paste a job description, click one button, and get the tailored PDF.

## Simplest architecture

Use Python's standard library HTTP server. No React, no database, no accounts.

```text
browser form -> localhost Python server -> existing resume_tailor code -> tailored.pdf
```

## UX

1. Run:

   ```bash
   python3 -m resume_tailor.ui
   ```

2. Browser opens `http://127.0.0.1:8765`.
3. Paste JD into textarea.
4. Click `Tailor Resume`.
5. Page shows:
   - added skills
   - safe bullet suggestions
   - one-page PDF validation
   - links to `tailored.pdf`, `tailored.tex`, `tailored.diff`

## Files

```text
resume_tailor/ui.py       # local-only server
resume_tailor/web.py      # tiny HTML strings if ui.py gets too long
```

## Guardrails

- Bind only to `127.0.0.1`.
- Never upload resume or JD anywhere.
- Reuse existing CLI tailoring/compile code.
- Keep personal files gitignored.

## Build steps

1. Add `resume_tailor/ui.py` with a GET form and POST handler.
2. POST writes JD to `job.txt`, runs existing `tailor()` + `compile_pdf()`.
3. Render results as plain HTML.
4. Add one smoke test for the handler helper, not browser automation.
5. Commit and push.

## Deferred

- Drag/drop resume upload.
- Live PDF preview.
- Saved job history.
- LLM bullet rewrite approval flow.

Add those only after the one-button local form is useful.
