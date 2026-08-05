from __future__ import annotations

import re
from dataclasses import dataclass


TERMS: dict[str, list[str]] = {
    "Languages": ["Go", "Python", "JavaScript", "TypeScript", "C++", "Java", "C", "SQL", "Bash"],
    "Frontend": ["React", "Next.js", "HTML", "CSS"],
    "Backend": ["Node.js", "Django", "REST", "API", "Microservices"],
    "Cloud/DevOps": ["AWS", "Azure", "Azure DevOps", "Docker", "Kubernetes", "CI/CD", "Git"],
    "Data": ["PostgreSQL", "MongoDB", "Supabase", "Redis"],
    "Security": ["OIDC", "JWT", "HashiCorp Vault", "Secrets", "Audit", "Compliance"],
    "AI": ["LLM", "MCP", "AI"],
}

ALIASES = {
    "ReactJS": "React",
    "Node": "Node.js",
    "K8s": "Kubernetes",
    "Kubernetes": "Kubernetes",
    "Vault": "HashiCorp Vault",
    "Postgres": "PostgreSQL",
    "GenAI": "AI",
}


@dataclass(frozen=True)
class KeywordReport:
    job_terms: dict[str, list[str]]
    resume_terms: dict[str, list[str]]
    safe_additions: dict[str, list[str]]


def _has(text: str, term: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9+#.]){re.escape(term)}(?![A-Za-z0-9+#.])", text, re.I) is not None


def extract_terms(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    haystack = text.replace("\\/", "/")
    for category, terms in TERMS.items():
        hits = []
        for term in terms:
            if _has(haystack, term) or any(canonical == term and _has(haystack, alias) for alias, canonical in ALIASES.items()):
                hits.append(term)
        if hits:
            found[category] = hits
    return found


def flatten(terms: dict[str, list[str]]) -> set[str]:
    return {term for values in terms.values() for term in values}


def report(job_text: str, resume_text: str, approved_text: str = "") -> KeywordReport:
    job_terms = extract_terms(job_text)
    resume_terms = extract_terms(resume_text)
    approved_terms = flatten(resume_terms) | flatten(extract_terms(approved_text))
    safe: dict[str, list[str]] = {}
    for category, terms in job_terms.items():
        keep = [term for term in terms if term in approved_terms and term not in flatten(resume_terms)]
        if keep:
            safe[category] = keep
    return KeywordReport(job_terms, resume_terms, safe)
