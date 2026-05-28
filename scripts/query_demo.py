#!/usr/bin/env python3
"""Query the manual Context Farm demo dataset with simple rule/exception retrieval."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from demo_store import connect, score_text


AUTHORITY_BONUS = {
    "signed-policy": 2.0,
    "official-sop": 1.5,
    "manager-note": 1.0,
    "operator-interview": 0.8,
    "meeting-transcript": 0.5,
    "informal-note": 0.2,
    "unknown": 0.0,
}

TYPE_BONUS = {
    "Constraint": 2.0,
    "Exception": 1.7,
    "Procedure": 1.2,
    "Decision": 1.0,
    "Fact": 0.4,
    "Entity": 0.1,
}

STATUS_BONUS = {
    "approved": 1.0,
    "draft": 0.2,
    "disputed": -1.0,
    "stale": -0.5,
    "superseded": -1.0,
}


def fetch_objects(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, object_uid, object_type, title, canonical_statement, body_json,
               status, freshness_state, confidence_score, authority_class, review_priority
        FROM knowledge_objects
        ORDER BY object_type, title
        """
    ).fetchall()


def fetch_sources(conn: sqlite3.Connection, object_id: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT s.source_uid, s.title, s.authority_class, s.authority_assignment_method,
               kos.evidence_text, kos.evidence_location
        FROM knowledge_object_sources kos
        JOIN sources s ON s.id = kos.source_id
        WHERE kos.knowledge_object_id = ?
        ORDER BY s.authority_class, s.title
        """,
        (object_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def fetch_linked(conn: sqlite3.Connection, object_id: int, link_type: str, reverse: bool = False) -> list[dict]:
    if reverse:
        sql = """
            SELECT ko.object_uid, ko.object_type, ko.title, ko.canonical_statement, kl.link_type
            FROM knowledge_links kl
            JOIN knowledge_objects ko ON ko.id = kl.from_object_id
            WHERE kl.to_object_id = ? AND kl.link_type = ?
            ORDER BY ko.title
        """
    else:
        sql = """
            SELECT ko.object_uid, ko.object_type, ko.title, ko.canonical_statement, kl.link_type
            FROM knowledge_links kl
            JOIN knowledge_objects ko ON ko.id = kl.to_object_id
            WHERE kl.from_object_id = ? AND kl.link_type = ?
            ORDER BY ko.title
        """
    rows = conn.execute(sql, (object_id, link_type)).fetchall()
    return [dict(row) for row in rows]


def rank(question: str, row: sqlite3.Row) -> float:
    text_score = score_text(question, [row["title"], row["canonical_statement"], row["body_json"]])
    authority_bonus = AUTHORITY_BONUS.get(row["authority_class"], 0.0)
    status_bonus = STATUS_BONUS.get(row["status"], 0.0)
    confidence_bonus = float(row["confidence_score"]) * 1.5
    type_bonus = TYPE_BONUS.get(row["object_type"], 0.0)
    return text_score + authority_bonus + status_bonus + confidence_bonus + type_bonus


def choose_primary(matches: list[tuple[float, sqlite3.Row]]) -> sqlite3.Row:
    if not matches:
        raise ValueError("No matches available")

    top_score = matches[0][0]
    for score, row in matches:
        if score < top_score - 2.0:
            break
        if row["object_type"] in {"Constraint", "Exception", "Procedure", "Decision"}:
            return row
    return matches[0][1]


def build_answer(conn: sqlite3.Connection, top: sqlite3.Row) -> dict:
    payload = {
        "object_uid": top["object_uid"],
        "object_type": top["object_type"],
        "title": top["title"],
        "canonical_statement": top["canonical_statement"],
        "status": top["status"],
        "authority_class": top["authority_class"],
        "confidence_score": top["confidence_score"],
        "sources": fetch_sources(conn, int(top["id"])),
        "exceptions": [],
        "references": [],
    }

    if top["object_type"] == "Constraint":
        payload["exceptions"] = fetch_linked(conn, int(top["id"]), "exception_to", reverse=True)
    elif top["object_type"] == "Exception":
        payload["references"] = fetch_linked(conn, int(top["id"]), "exception_to")
    else:
        payload["references"] = fetch_linked(conn, int(top["id"]), "references")

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="demo/context_farm_demo.db", help="SQLite database path")
    parser.add_argument("--question", required=True, help="Question to retrieve against the demo domain")
    parser.add_argument("--top", type=int, default=3, help="Number of matches to show")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    conn = connect(Path(args.db))
    try:
        ranked = sorted(
            ((rank(args.question, row), row) for row in fetch_objects(conn)),
            key=lambda item: item[0],
            reverse=True,
        )
        matches = [(score, row) for score, row in ranked if score > 0][: args.top]
        if not matches:
            raise SystemExit("No relevant demo objects found.")

        primary = choose_primary(matches)
        payload = {
            "question": args.question,
            "top_match": build_answer(conn, primary),
            "matches": [
                {
                    "score": round(score, 2),
                    "object_uid": row["object_uid"],
                    "object_type": row["object_type"],
                    "title": row["title"],
                    "canonical_statement": row["canonical_statement"],
                }
                for score, row in matches
            ],
        }

        if args.json:
            print(json.dumps(payload, indent=2))
            return

        top = payload["top_match"]
        print(f"Question: {args.question}")
        print()
        print(f"Top match: {top['title']} [{top['object_type']}]")
        print(top["canonical_statement"])
        print(f"Status: {top['status']} | Authority: {top['authority_class']} | Confidence: {top['confidence_score']}")
        if top["exceptions"]:
            print()
            print("Exceptions:")
            for item in top["exceptions"]:
                print(f"- {item['title']}: {item['canonical_statement']}")
        if top["references"]:
            print()
            print("Linked context:")
            for item in top["references"]:
                print(f"- {item['title']} [{item['object_type']}]")
        print()
        print("Sources:")
        for source in top["sources"]:
            print(
                f"- {source['title']} ({source['authority_class']}, {source['authority_assignment_method']}): "
                f"{source['evidence_text']}"
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
