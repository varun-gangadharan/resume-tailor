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
    if "REST" not in job_terms:
        return tex

    def replace(match: re.Match[str]) -> str:
        body = match.group("body")
        if "REST API" in body or "REST APIs" in body:
            return match.group(0)
        updated = re.sub(r"\bAPI backend\b", "REST API backend", body, count=1)
        updated = re.sub(r"\bAPI requests\b", "REST API requests", updated, count=1)
        updated = re.sub(r"\bAPIs\b", "REST APIs", updated, count=1)
        if updated == body:
            updated = re.sub(r"\bAPI\b", "REST API", updated, count=1)
        return f"\\resumeItem{{{updated}}}"

    return ITEM_RE.sub(replace, tex)
