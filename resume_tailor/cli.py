from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .keywords import extract_terms
from .latex import sections
from .tailor import tailor


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

    if args.out:
        Path(args.out).expanduser().write_text(result.tex)
    print(json.dumps({"job_terms": result.job_terms, "resume_terms": result.resume_terms, "additions": result.additions}, indent=2))
    if result.diff:
        print("\n--- diff ---")
        print(result.diff, end="")
    else:
        print("\nNo safe edits made. Add an --approved profile if the missing terms are truthful.")
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
    tailor_p.add_argument("--approved", help="optional text file of truthful extra skills")
    tailor_p.set_defaults(func=cmd_tailor)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
