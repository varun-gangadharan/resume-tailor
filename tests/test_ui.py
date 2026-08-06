from resume_tailor.library import SavedResume
from resume_tailor.ui import UiResult, form, matches_page, result_page


def test_form_mentions_local_privacy():
    assert b"Nothing leaves your computer" in form()


def test_result_page_links_outputs():
    page = result_page(UiResult({"Tech": ["REST"]}, ["If truthful, weave 'Redis' into an existing relevant bullet; do not add a new bullet just for ATS."], 1, "diff", "go-react"))
    assert b"Open PDF" in page
    assert b"tailored.diff" in page
    assert b"Redis" in page
    assert b"Save to Library" in page


def test_matches_page_shows_existing_resume():
    page = matches_page([SavedResume(1, "Backend", "backend", "library/resumes/backend/resume.pdf", keywords=("Go",), score=0.75, matched=("Go",), missing=("Redis",))], "Go Redis")
    assert b"Backend" in page
    assert b"75%" in page
    assert b"Generate New PDF Instead" in page
