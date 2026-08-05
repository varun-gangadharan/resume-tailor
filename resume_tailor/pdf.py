from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PdfResult:
    pdf: Path
    pages: int | None
    engine: str


def _sanitize_for_tectonic(tex: str) -> str:
    # Tectonic runs XeTeX; these pdfTeX-only ATS lines break compilation.
    return tex.replace("\\input{glyphtounicode}\n", "").replace("\\pdfgentounicode=1\n", "")


def page_count(pdf: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    out = subprocess.check_output(["pdfinfo", str(pdf)], text=True, stderr=subprocess.STDOUT)
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    return None


def compile_pdf(tex_path: Path, pdf_path: Path) -> PdfResult:
    tex_path = tex_path.expanduser().resolve()
    pdf_path = pdf_path.expanduser().resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    if not shutil.which("tectonic"):
        raise RuntimeError("tectonic is not installed; run: brew install tectonic poppler")

    with tempfile.TemporaryDirectory(prefix="resume-tailor-") as tmp:
        tmpdir = Path(tmp)
        work_tex = tmpdir / tex_path.name
        work_tex.write_text(_sanitize_for_tectonic(tex_path.read_text()))
        subprocess.run(
            ["tectonic", "-X", "compile", str(work_tex), "--outdir", str(tmpdir)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        built = tmpdir / f"{work_tex.stem}.pdf"
        shutil.copyfile(built, pdf_path)

    return PdfResult(pdf=pdf_path, pages=page_count(pdf_path), engine="tectonic")
