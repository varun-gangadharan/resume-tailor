from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .keywords import extract_terms, flatten


@dataclass(frozen=True)
class SavedResume:
    id: int
    name: str
    slug: str
    pdf_path: str
    score: float = 0.0
    matched: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


def slugify(name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "resume"


class ResumeLibrary:
    def __init__(self, root: Path):
        self.root = root / "library"
        self.db = self.root / "resume_tailor.db"
        self.resumes = self.root / "resumes"
        self.root.mkdir(exist_ok=True)
        self.resumes.mkdir(exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                create table if not exists resumes (
                  id integer primary key,
                  name text not null,
                  slug text not null unique,
                  tex_path text not null,
                  pdf_path text not null,
                  notes text not null default '',
                  created_at text not null
                );
                create table if not exists resume_keywords (
                  resume_id integer not null,
                  keyword text not null,
                  unique(resume_id, keyword),
                  foreign key(resume_id) references resumes(id) on delete cascade
                );
                create table if not exists jobs (
                  id integer primary key,
                  raw_jd text not null,
                  created_at text not null
                );
                create table if not exists matches (
                  job_id integer not null,
                  resume_id integer not null,
                  score real not null,
                  unique(job_id, resume_id)
                );
                """
            )

    def save_resume(self, name: str, tex: Path, pdf: Path, job_text: str = "", notes: str = "") -> SavedResume:
        base = slugify(name)
        slug = base
        n = 2
        with self.connect() as conn:
            while conn.execute("select 1 from resumes where slug = ?", (slug,)).fetchone():
                slug = f"{base}-{n}"
                n += 1
            dest = self.resumes / slug
            dest.mkdir(parents=True)
            tex_dest = dest / "resume.tex"
            pdf_dest = dest / "resume.pdf"
            shutil.copyfile(tex, tex_dest)
            shutil.copyfile(pdf, pdf_dest)
            created_at = datetime.now(timezone.utc).isoformat()
            cur = conn.execute(
                "insert into resumes(name, slug, tex_path, pdf_path, notes, created_at) values (?, ?, ?, ?, ?, ?)",
                (name, slug, str(tex_dest), str(pdf_dest), notes, created_at),
            )
            resume_id = int(cur.lastrowid)
            keywords = sorted(flatten(extract_terms(tex_dest.read_text() + "\n" + job_text)))
            conn.executemany(
                "insert or ignore into resume_keywords(resume_id, keyword) values (?, ?)",
                [(resume_id, k) for k in keywords],
            )
        return SavedResume(resume_id, name, slug, str(pdf_dest))

    def list_resumes(self) -> list[SavedResume]:
        with self.connect() as conn:
            rows = conn.execute("select id, name, slug, pdf_path from resumes order by created_at desc").fetchall()
        return [SavedResume(row["id"], row["name"], row["slug"], row["pdf_path"]) for row in rows]

    def match(self, job_text: str, limit: int = 5) -> list[SavedResume]:
        job_keywords = flatten(extract_terms(job_text))
        if not job_keywords:
            return []
        with self.connect() as conn:
            job_id = conn.execute(
                "insert into jobs(raw_jd, created_at) values (?, ?)",
                (job_text, datetime.now(timezone.utc).isoformat()),
            ).lastrowid
            rows = conn.execute(
                """
                select r.id, r.name, r.slug, r.pdf_path, group_concat(k.keyword) as keywords
                from resumes r
                left join resume_keywords k on k.resume_id = r.id
                group by r.id
                """
            ).fetchall()
            scored: list[SavedResume] = []
            for row in rows:
                resume_keywords = set((row["keywords"] or "").split(",")) - {""}
                matched = tuple(sorted(job_keywords & resume_keywords))
                missing = tuple(sorted(job_keywords - resume_keywords))
                score = round(len(matched) / len(job_keywords), 3)
                conn.execute(
                    "insert or replace into matches(job_id, resume_id, score) values (?, ?, ?)",
                    (job_id, row["id"], score),
                )
                scored.append(SavedResume(row["id"], row["name"], row["slug"], row["pdf_path"], score, matched, missing))
        return sorted(scored, key=lambda r: r.score, reverse=True)[:limit]
