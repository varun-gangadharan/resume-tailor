from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .keywords import extract_terms
from .latex import sections
from .pdf import compile_pdf
from .tailor import bullet_suggestions, tailor


def _read(path: str | None) -> str:
    if path and path != "-":
        return Path(path).expanduser().read_text()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Paste job description, then press Ctrl-D:", file=sys.stderr)
    return sys.stdin.read()


def cmd_inspect(args: argparse.Namespace) -> int:
    tex = Path(args.resume).expanduser().read_text()
    print(json.dumps({"sections": sections(tex), "terms": extract_terms(tex)}, indent=2))
    return 0


def cmd_keywords(args: argparse.Namespace) -> int:
    print(json.dumps(extract_terms(_read(args.job)), indent=2))
    return 0


def cmd_tailor(args: argparse.Namespace) -> int:
    resume_path = Path(args.resume).expanduser()
    resume_tex = resume_path.read_text()
    job_text = _read(args.job)
    approved_path = Path(args.approved).expanduser() if args.approved else Path("approved.txt")
    approved = approved_path.read_text() if approved_path.exists() else ""
    result = tailor(resume_tex, job_text, approved)

    out = Path(args.out).expanduser()
    out.write_text(result.tex)
    if args.diff:
        Path(args.diff).expanduser().write_text(result.diff or "")
    print(json.dumps({"job_terms": result.job_terms, "resume_terms": result.resume_terms, "additions": result.additions}, indent=2))
    if result.diff:
        print("\n--- diff ---")
        print(result.diff, end="")
    else:
        print("\nNo safe skills edits made. Add an --approved profile if the missing terms are truthful.")

    suggestions = bullet_suggestions(job_text, result.tex)
    if args.suggestions:
        Path(args.suggestions).expanduser().write_text("\n".join(suggestions) + ("\n" if suggestions else ""))
    if suggestions:
        print("\n--- safe bullet suggestions ---")
        for item in suggestions:
            print(f"- {item}")

    print(f"\nTEX: {out.resolve()}")
    if args.diff:
        print(f"DIFF: {Path(args.diff).expanduser().resolve()}")
    if args.suggestions:
        print(f"SUGGESTIONS: {Path(args.suggestions).expanduser().resolve()}")

    if args.pdf:
        pdf = compile_pdf(out, Path(args.pdf))
        page_text = "unknown" if pdf.pages is None else str(pdf.pages)
        print(f"PDF: {pdf.pdf} ({page_text} page{'s' if pdf.pages != 1 else ''}, {pdf.engine})")
        if pdf.pages and pdf.pages > 1:
            print("WARNING: PDF is over one page.")
        if args.open_pdf:
            subprocess.run(["open", str(pdf.pdf)], check=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="resume-tailor")
    sub = parser.add_subparsers(required=True)

    inspect_p = sub.add_parser("inspect")
    inspect_p.add_argument("--resume", default="resume.tex")
    inspect_p.set_defaults(func=cmd_inspect)

    keywords_p = sub.add_parser("keywords")
    keywords_p.add_argument("--job", default="job.txt", help="job description text file")
    keywords_p.set_defaults(func=cmd_keywords)

    tailor_p = sub.add_parser("tailor")
    tailor_p.add_argument("--resume", default="resume.tex")
    tailor_p.add_argument("--job", default="job.txt")
    tailor_p.add_argument("--out", default="tailored.tex")
    tailor_p.add_argument("--pdf", default="tailored.pdf", help="compiled PDF output; pass empty string to skip")
    tailor_p.add_argument("--diff", default="tailored.diff")
    tailor_p.add_argument("--suggestions", default="suggestions.txt")
    tailor_p.add_argument("--open", dest="open_pdf", action="store_true", help="open the PDF after compiling")
    tailor_p.set_defaults(open_pdf=False)
    tailor_p.add_argument("--approved", help="optional text file of truthful extra skills")
    tailor_p.set_defaults(func=cmd_tailor)

    paste_p = sub.add_parser("paste", help="paste a JD in the terminal and output tailored.pdf")
    paste_p.add_argument("--resume", default="resume.tex")
    paste_p.add_argument("--out", default="tailored.tex")
    paste_p.add_argument("--pdf", default="tailored.pdf")
    paste_p.add_argument("--diff", default="tailored.diff")
    paste_p.add_argument("--suggestions", default="suggestions.txt")
    paste_p.add_argument("--no-open", dest="open_pdf", action="store_false", help="do not open the PDF after compiling")
    paste_p.add_argument("--approved", help="optional text file of truthful extra skills")
    paste_p.set_defaults(func=cmd_tailor, job="-", open_pdf=True)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
