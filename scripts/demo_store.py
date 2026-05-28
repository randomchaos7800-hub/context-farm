#!/usr/bin/env python3
"""Shared helpers for the Context Farm demo domain prototype."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "sql" / "0001_init_structured_store.sql"


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def utc_now() -> str:
    return "2026-05-28T12:30:00Z"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def normalize_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_domain_id(conn: sqlite3.Connection, slug: str) -> int:
    row = conn.execute("SELECT id FROM domains WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        raise KeyError(f"Unknown domain slug: {slug}")
    return int(row["id"])


def score_text(question: str, fields: Iterable[str]) -> float:
    query_terms = tokenize(question)
    if not query_terms:
        return 0.0

    haystack = " ".join(fields).lower()
    score = 0.0
    for term in query_terms:
        if term in haystack:
            score += 1.0
        if f" {term} " in f" {haystack} ":
            score += 0.5
    return score
