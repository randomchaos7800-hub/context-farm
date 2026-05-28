#!/usr/bin/env python3
"""Generate a compact briefing from the manual Context Farm demo dataset."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from demo_store import connect, score_text


SECTION_ORDER = ["Constraint", "Exception", "Procedure", "Decision", "Fact", "Entity"]


def fetch_candidates(conn, topic: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, object_uid, object_type, title, canonical_statement, body_json,
               status, freshness_state, confidence_score, authority_class
        FROM knowledge_objects
        ORDER BY title
        """
    ).fetchall()
    scored = []
    for row in rows:
        score = score_text(topic, [row["title"], row["canonical_statement"], row["body_json"]])
        if score <= 0:
            continue
        score += float(row["confidence_score"])
        if row["status"] == "approved":
            score += 0.75
        scored.append((score, dict(row)))
    return [row for _, row in sorted(scored, key=lambda item: item[0], reverse=True)]


def fetch_sources(conn, object_id: int) -> list[str]:
    rows = conn.execute(
        """
        SELECT s.title
        FROM knowledge_object_sources kos
        JOIN sources s ON s.id = kos.source_id
        WHERE kos.knowledge_object_id = ?
        ORDER BY s.title
        """,
        (object_id,),
    ).fetchall()
    return [row[0] for row in rows]


def build_brief(conn, topic: str, limit: int) -> dict:
    candidates = fetch_candidates(conn, topic)[:limit]
    grouped: dict[str, list[dict]] = {key: [] for key in SECTION_ORDER}
    for row in candidates:
        row["sources"] = fetch_sources(conn, int(row["id"]))
        grouped[row["object_type"]].append(row)

    highlights = []
    for group in ("Constraint", "Exception", "Procedure"):
        for item in grouped[group][:1]:
            highlights.append(item["canonical_statement"])

    return {
        "topic": topic,
        "highlights": highlights,
        "sections": grouped,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="demo/context_farm_demo.db", help="SQLite database path")
    parser.add_argument("--topic", required=True, help="Briefing topic")
    parser.add_argument("--limit", type=int, default=6, help="Max matching objects to include")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    conn = connect(Path(args.db))
    try:
        brief = build_brief(conn, args.topic, args.limit)
        if args.json:
            print(json.dumps(brief, indent=2))
            return

        print(f"Briefing: {args.topic}")
        print()
        if brief["highlights"]:
            print("Highlights:")
            for item in brief["highlights"]:
                print(f"- {item}")
            print()

        for section in SECTION_ORDER:
            rows = brief["sections"][section]
            if not rows:
                continue
            print(f"{section}s:")
            for row in rows:
                print(f"- {row['title']}: {row['canonical_statement']}")
                if row["sources"]:
                    print(f"  Sources: {', '.join(row['sources'])}")
            print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
