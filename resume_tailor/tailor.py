from __future__ import annotations

import difflib
from dataclasses import dataclass

from .keywords import flatten, report
from .latex import parse_skills, update_skills


@dataclass(frozen=True)
class TailorResult:
    tex: str
    diff: str
    job_terms: dict[str, list[str]]
    resume_terms: dict[str, list[str]]
    additions: dict[str, list[str]]


def _skill_line(category: str) -> str:
    return "Languages" if category == "Languages" else "Tech"


def tailor(resume_tex: str, job_text: str, approved_text: str = "") -> TailorResult:
    keyword_report = report(job_text, resume_tex, approved_text)
    skills = parse_skills(resume_tex)
    present = {value.lower() for values in skills.values() for value in values}

    additions: dict[str, list[str]] = {}
    for category, terms in keyword_report.safe_additions.items():
        line = _skill_line(category)
        for term in terms:
            if term.lower() not in present:
                additions.setdefault(line, []).append(term)
                present.add(term.lower())

    tailored = update_skills(resume_tex, additions)
    diff = "".join(
        difflib.unified_diff(
            resume_tex.splitlines(keepends=True),
            tailored.splitlines(keepends=True),
            fromfile="resume.tex",
            tofile="tailored.tex",
        )
    )
    return TailorResult(
        tex=tailored,
        diff=diff,
        job_terms=keyword_report.job_terms,
        resume_terms=keyword_report.resume_terms,
        additions=additions,
    )


def missing_job_terms(job_text: str, resume_tex: str) -> list[str]:
    keyword_report = report(job_text, resume_tex)
    return sorted(flatten(keyword_report.job_terms) - flatten(keyword_report.resume_terms))
