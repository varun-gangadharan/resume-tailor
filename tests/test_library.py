from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from resume_tailor.library import ResumeLibrary, slugify

ROOT = Path(__file__).resolve().parents[1]


def test_slugify():
    assert slugify("Backend Go / Vault") == "backend-go-vault"


def test_save_and_match_resume_library():
    with TemporaryDirectory() as d:
        tmp = Path(d)
        tex = tmp / "resume.tex"
        pdf = tmp / "resume.pdf"
        copyfile(ROOT / "examples" / "current_resume.tex", tex)
        pdf.write_bytes(b"%PDF-1.4 fake")
        lib = ResumeLibrary(tmp)
        saved = lib.save_resume("Backend Go Vault", tex, pdf, "Go Kubernetes Vault REST")
        assert saved.slug == "backend-go-vault"
        matches = lib.match("Go Kubernetes Redis REST")
        assert matches[0].name == "Backend Go Vault"
        assert matches[0].score > 0
        assert "Go" in matches[0].matched
        assert "Redis" in matches[0].missing
