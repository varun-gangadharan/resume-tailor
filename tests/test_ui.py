from resume_tailor.ui import UiResult, form, result_page


def test_form_mentions_local_privacy():
    assert b"Nothing leaves your computer" in form()


def test_result_page_links_outputs():
    page = result_page(UiResult({"Tech": ["REST"]}, ["If truthful, weave 'Redis' into an existing relevant bullet; do not add a new bullet just for ATS."], 1, "diff"))
    assert b"Open PDF" in page
    assert b"tailored.diff" in page
    assert b"Redis" in page
