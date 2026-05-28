#!/usr/bin/env python3
"""Build a local SQLite demo database for the service-dispatch domain."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from demo_store import apply_schema, connect, load_json, normalize_json


def upsert_domain(conn: sqlite3.Connection, domain_seed: dict) -> int:
    domain = domain_seed["domain"]
    authority_policy = domain_seed["authority_policy"]
    schema = domain_seed["schema"]
    now = "2026-05-28T12:00:00Z"

    conn.execute(
        """
        INSERT INTO domains (slug, title, description, authority_policy_json, schema_json, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            authority_policy_json = excluded.authority_policy_json,
            schema_json = excluded.schema_json,
            updated_at = excluded.updated_at
        """,
        (
            domain["slug"],
            domain["title"],
            domain["description"],
            normalize_json(authority_policy),
            normalize_json(schema),
            now,
            now,
        ),
    )
    domain_id = conn.execute("SELECT id FROM domains WHERE slug = ?", (domain["slug"],)).fetchone()[0]

    for rule in authority_policy:
        conn.execute(
            """
            INSERT INTO authority_rules (domain_id, authority_class, rank_order, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(domain_id, authority_class) DO UPDATE SET
                rank_order = excluded.rank_order,
                description = excluded.description,
                updated_at = excluded.updated_at
            """,
            (
                domain_id,
                rule["authority_class"],
                rule["rank_order"],
                rule["description"],
                now,
                now,
            ),
        )

    return int(domain_id)


def insert_sources(conn: sqlite3.Connection, domain_id: int, manual: dict) -> dict[str, int]:
    source_ids: dict[str, int] = {}
    for source in manual["sources"]:
        conn.execute(
            """
            INSERT INTO sources (
                source_uid, domain_id, source_type, title, original_uri, raw_path, checksum,
                authority_class, authority_assignment_method, ingested_by, ingested_at,
                metadata_json, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_uid) DO UPDATE SET
                title = excluded.title,
                original_uri = excluded.original_uri,
                raw_path = excluded.raw_path,
                checksum = excluded.checksum,
                authority_class = excluded.authority_class,
                authority_assignment_method = excluded.authority_assignment_method,
                ingested_by = excluded.ingested_by,
                ingested_at = excluded.ingested_at,
                metadata_json = excluded.metadata_json,
                updated_at = excluded.updated_at
            """,
            (
                source["source_uid"],
                domain_id,
                source["source_type"],
                source["title"],
                source.get("original_uri", ""),
                source.get("raw_path", ""),
                source.get("checksum", ""),
                source.get("authority_class", "unknown"),
                source.get("authority_assignment_method", "declared"),
                source.get("ingested_by", ""),
                source["ingested_at"],
                normalize_json(source.get("metadata_json", {})),
                source["ingested_at"],
                source["ingested_at"],
            ),
        )
        source_ids[source["source_uid"]] = int(
            conn.execute("SELECT id FROM sources WHERE source_uid = ?", (source["source_uid"],)).fetchone()[0]
        )
    return source_ids


def insert_ingestion_run(conn: sqlite3.Connection, domain_id: int, count: int) -> int:
    run_uid = "run.service-dispatch.demo-seed"
    now = "2026-05-28T12:15:00Z"
    conn.execute(
        """
        INSERT INTO ingestion_runs (
            run_uid, domain_id, run_type, status, trigger_source, input_count, output_count,
            notes, started_at, finished_at, created_at, updated_at
        )
        VALUES (?, ?, 'extract', 'succeeded', 'manual-demo-seed', ?, ?, 'manual demo object set', ?, ?, ?, ?)
        ON CONFLICT(run_uid) DO UPDATE SET
            input_count = excluded.input_count,
            output_count = excluded.output_count,
            finished_at = excluded.finished_at,
            updated_at = excluded.updated_at
        """,
        (run_uid, domain_id, count, count, now, now, now, now),
    )
    return int(conn.execute("SELECT id FROM ingestion_runs WHERE run_uid = ?", (run_uid,)).fetchone()[0])


def insert_objects(conn: sqlite3.Connection, domain_id: int, run_id: int, manual: dict) -> dict[str, int]:
    object_ids: dict[str, int] = {}
    now = "2026-05-28T12:20:00Z"
    for obj in manual["objects"]:
        conn.execute(
            """
            INSERT INTO knowledge_objects (
                object_uid, domain_id, object_type, title, canonical_statement, body_json,
                status, freshness_state, confidence_score, authority_class, review_priority,
                source_count, extracted_from_run_id, created_at, updated_at, reviewed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(object_uid) DO UPDATE SET
                title = excluded.title,
                canonical_statement = excluded.canonical_statement,
                body_json = excluded.body_json,
                status = excluded.status,
                freshness_state = excluded.freshness_state,
                confidence_score = excluded.confidence_score,
                authority_class = excluded.authority_class,
                review_priority = excluded.review_priority,
                source_count = excluded.source_count,
                updated_at = excluded.updated_at,
                reviewed_at = excluded.reviewed_at
            """,
            (
                obj["object_uid"],
                domain_id,
                obj["object_type"],
                obj["title"],
                obj["canonical_statement"],
                normalize_json(obj.get("body_json", {})),
                obj["status"],
                obj["freshness_state"],
                obj["confidence_score"],
                obj["authority_class"],
                obj["review_priority"],
                obj["source_count"],
                run_id,
                now,
                now,
                now if obj["status"] == "approved" else "",
            ),
        )
        object_ids[obj["object_uid"]] = int(
            conn.execute("SELECT id FROM knowledge_objects WHERE object_uid = ?", (obj["object_uid"],)).fetchone()[0]
        )
    return object_ids


def insert_links(conn: sqlite3.Connection, object_ids: dict[str, int], manual: dict) -> None:
    now = "2026-05-28T12:22:00Z"
    for link in manual.get("links", []):
        conn.execute(
            """
            INSERT INTO knowledge_links (from_object_id, to_object_id, link_type, metadata_json, created_at)
            VALUES (?, ?, ?, '{}', ?)
            ON CONFLICT(from_object_id, to_object_id, link_type) DO NOTHING
            """,
            (
                object_ids[link["from_object_uid"]],
                object_ids[link["to_object_uid"]],
                link["link_type"],
                now,
            ),
        )


def insert_object_sources(conn: sqlite3.Connection, object_ids: dict[str, int], source_ids: dict[str, int], manual: dict) -> None:
    now = "2026-05-28T12:24:00Z"
    for item in manual.get("object_sources", []):
        conn.execute(
            """
            INSERT INTO knowledge_object_sources (
                knowledge_object_id, source_id, evidence_text, evidence_location, extraction_notes, created_at
            )
            VALUES (?, ?, ?, ?, '', ?)
            ON CONFLICT(knowledge_object_id, source_id, evidence_location) DO UPDATE SET
                evidence_text = excluded.evidence_text
            """,
            (
                object_ids[item["object_uid"]],
                source_ids[item["source_uid"]],
                item.get("evidence_text", ""),
                item.get("evidence_location", ""),
                now,
            ),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="demo/context_farm_demo.db", help="SQLite database path")
    parser.add_argument("--domain-seed", default="examples/domain-service-dispatch.json", help="Domain seed JSON")
    parser.add_argument("--manual-objects", default="examples/service-dispatch-manual-objects.json", help="Manual object set JSON")
    args = parser.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    domain_seed = load_json(Path(args.domain_seed))
    manual = load_json(Path(args.manual_objects))

    conn = connect(db_path)
    try:
        apply_schema(conn)
        domain_id = upsert_domain(conn, domain_seed)
        source_ids = insert_sources(conn, domain_id, manual)
        run_id = insert_ingestion_run(conn, domain_id, len(manual["objects"]))
        object_ids = insert_objects(conn, domain_id, run_id, manual)
        insert_links(conn, object_ids, manual)
        insert_object_sources(conn, object_ids, source_ids, manual)
        conn.commit()
        print(f"Built demo database at {db_path}")
        print(f"Domain: {domain_seed['domain']['slug']}")
        print(f"Sources: {len(source_ids)}")
        print(f"Objects: {len(object_ids)}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
