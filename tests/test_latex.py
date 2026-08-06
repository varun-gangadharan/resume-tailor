from pathlib import Path

from resume_tailor.latex import parse_skills, sections, update_bullet_tech, update_skills
from resume_tailor.tailor import bullet_suggestions, tailor

ROOT = Path(__file__).resolve().parents[1]
RESUME = (ROOT / "examples" / "current_resume.tex").read_text()
JOB = (ROOT / "examples" / "job.txt").read_text()
APPROVED = (ROOT / "examples" / "approved.txt").read_text()


def test_detects_sections():
    assert sections(RESUME) == ["Technical Skills", "Experience", "Education", "Projects"]


def test_parse_skills():
    skills = parse_skills(RESUME)
    assert "Go" in skills["Languages"]
    assert "Docker" in skills["Tech"]


def test_update_skills_only_changes_skills_block():
    updated = update_skills(RESUME, {"Tech": ["PostgreSQL", "CI/CD"]})
    assert "PostgreSQL" in updated
    assert updated.count("\\resumeItem{") == RESUME.count("\\resumeItem{")
    assert updated.count("\\section{") == RESUME.count("\\section{")


def test_tailor_adds_only_truthful_approved_terms():
    result = tailor(RESUME, JOB, APPROVED)
    assert result.additions == {"Tech": ["REST", "CI/CD", "PostgreSQL"]}
    assert "Redis" not in result.tex
    assert result.tex.count("\\resumeItem{") == RESUME.count("\\resumeItem{")


def test_update_bullet_tech_keeps_action_same():
    tex = r"\resumeItem{Modernized a legacy API backend, improving response time by 26\%.}"
    updated = update_bullet_tech(tex, {"REST"})
    assert "Modernized a legacy REST API backend" in updated
    assert updated.count("\\resumeItem{") == 1


def test_bullet_suggestions_are_advisory_only():
    suggestions = bullet_suggestions("Redis GraphQL", RESUME)
    assert "If truthful, weave 'GraphQL' into an existing relevant bullet; do not add a new bullet just for ATS." in suggestions
    assert "If truthful, weave 'Redis' into an existing relevant bullet; do not add a new bullet just for ATS." in suggestions
