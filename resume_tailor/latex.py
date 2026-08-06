from __future__ import annotations

import re


SKILLS_RE = re.compile(
    r"(?P<head>\\section\{Technical Skills\}.*?\\small\{\\item\{)(?P<body>.*?)(?P<tail>\n\}\}\n\\end\{itemize\})",
    re.S,
)
LINE_RE = re.compile(r"\\textbf\{(?P<name>[^:]+):\}\s*(?P<values>.*?)(?:\\\\)?\s*$")
ITEM_RE = re.compile(r"\\resumeItem\{(?P<body>.*?)\}", re.S)


def sections(tex: str) -> list[str]:
    return re.findall(r"\\section\{([^}]+)\}", tex)


def skills_block(tex: str) -> str:
    match = SKILLS_RE.search(tex)
    if not match:
        raise ValueError("Could not find Technical Skills block")
    return match.group("body")


def parse_skills(tex: str) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {}
    for raw in skills_block(tex).splitlines():
        line = raw.strip()
        if not line:
            continue
        match = LINE_RE.match(line)
        if not match:
            continue
        parsed[match.group("name")] = [value.strip() for value in match.group("values").split(",") if value.strip()]
    return parsed


def update_skills(tex: str, additions: dict[str, list[str]]) -> str:
    if not additions:
        return tex
    match = SKILLS_RE.search(tex)
    if not match:
        raise ValueError("Could not find Technical Skills block")

    lines = match.group("body").splitlines()
    new_lines = []
    for raw in lines:
        line = raw.strip()
        parsed = LINE_RE.match(line)
        if not parsed:
            new_lines.append(raw)
            continue
        name = parsed.group("name")
        values = [value.strip() for value in parsed.group("values").split(",") if value.strip()]
        existing = {value.lower() for value in values}
        for value in additions.get(name, []):
            if value.lower() not in existing:
                values.append(value)
                existing.add(value.lower())
        slash = " \\\\" if raw.rstrip().endswith("\\\\") else ""
        new_lines.append(f"\\textbf{{{name}:}} {', '.join(values)}{slash}")

    return tex[: match.start("body")] + "\n".join(new_lines) + tex[match.end("body") :]


def update_bullet_tech(tex: str, job_terms: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        body = match.group("body")
        updated = body

        if "REST" in job_terms and "REST API" not in updated and "REST APIs" not in updated:
            updated = re.sub(r"\bAPI backend\b", "REST API backend", updated, count=1)
            updated = re.sub(r"\bAPI requests\b", "REST API requests", updated, count=1)
            updated = re.sub(r"\bAPIs\b", "REST APIs", updated, count=1)
            if updated == body:
                updated = re.sub(r"\bAPI\b", "REST API", updated, count=1)

        if "Distributed Systems" in job_terms:
            updated = re.sub(r"\blarge-scale full-stack product\b", "large-scale distributed full-stack product", updated, count=1)
            updated = re.sub(r"\bbackend services in Go\b", "distributed backend services in Go", updated, count=1)

        if "Kubernetes" in job_terms and "Kubernetes" in tex:
            with_k8s = re.sub(r"\bdistributed backend services in Go\b", "Kubernetes-backed distributed backend services in Go", updated, count=1)
            updated = with_k8s if with_k8s != updated else re.sub(r"\bbackend services in Go\b", "Kubernetes-backed backend services in Go", updated, count=1)

        if "CI/CD" in job_terms and "Azure DevOps" in tex:
            updated = re.sub(r"\bShipped well-tested full-stack features\b", "Shipped CI/CD-ready, well-tested full-stack features", updated, count=1)

        if "Automation" in job_terms:
            updated = re.sub(r"\bdeveloper tooling with\b", "developer tooling and automation with", updated, count=1)

        return match.group(0) if updated == body else f"\\resumeItem{{{updated}}}"

    return ITEM_RE.sub(replace, tex)
