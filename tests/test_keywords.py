from resume_tailor.keywords import extract_terms, report


def test_extracts_swe_terms():
    terms = extract_terms("Python Go React AWS Kubernetes Postgres LLM")
    assert terms["Languages"] == ["Go", "Python"]
    assert "React" in terms["Frontend"]
    assert "AWS" in terms["Cloud/DevOps"]
    assert terms["Data"] == ["PostgreSQL"]
    assert terms["AI"] == ["LLM"]


def test_only_approved_missing_terms_are_safe_additions():
    result = report("PostgreSQL Redis", "Python SQL", "PostgreSQL")
    assert result.safe_additions == {"Data": ["PostgreSQL"]}
