PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    authority_policy_json TEXT NOT NULL DEFAULT '{}',
    schema_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_uid TEXT NOT NULL UNIQUE,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (
        source_type IN ('pdf', 'url', 'text', 'transcript', 'chat_export', 'operator_interview', 'seed')
    ),
    title TEXT NOT NULL,
    original_uri TEXT NOT NULL DEFAULT '',
    raw_path TEXT NOT NULL DEFAULT '',
    checksum TEXT NOT NULL DEFAULT '',
    authority_class TEXT NOT NULL DEFAULT 'unknown',
    ingested_by TEXT NOT NULL DEFAULT '',
    ingested_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_uid TEXT NOT NULL UNIQUE,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    run_type TEXT NOT NULL CHECK (
        run_type IN ('ingest', 'compile', 'extract', 'reextract', 'reseed')
    ),
    status TEXT NOT NULL CHECK (
        status IN ('queued', 'running', 'succeeded', 'failed', 'partial')
    ),
    trigger_source TEXT NOT NULL DEFAULT 'manual',
    input_count INTEGER NOT NULL DEFAULT 0,
    output_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_uid TEXT NOT NULL UNIQUE,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    object_type TEXT NOT NULL CHECK (
        object_type IN ('Fact', 'Procedure', 'Constraint', 'Exception', 'Decision', 'Entity')
    ),
    title TEXT NOT NULL,
    canonical_statement TEXT NOT NULL,
    body_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (
        status IN ('draft', 'approved', 'disputed', 'stale', 'superseded')
    ),
    freshness_state TEXT NOT NULL DEFAULT 'unknown' CHECK (
        freshness_state IN ('current', 'needs_review', 'stale', 'unknown')
    ),
    confidence_score REAL NOT NULL DEFAULT 0.0 CHECK (
        confidence_score >= 0.0 AND confidence_score <= 1.0
    ),
    authority_class TEXT NOT NULL DEFAULT 'unknown',
    review_priority TEXT NOT NULL DEFAULT 'medium' CHECK (
        review_priority IN ('high', 'medium', 'low')
    ),
    source_count INTEGER NOT NULL DEFAULT 0,
    extracted_from_run_id INTEGER REFERENCES ingestion_runs(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    reviewed_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS knowledge_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_object_id INTEGER NOT NULL REFERENCES knowledge_objects(id) ON DELETE CASCADE,
    to_object_id INTEGER NOT NULL REFERENCES knowledge_objects(id) ON DELETE CASCADE,
    link_type TEXT NOT NULL CHECK (
        link_type IN ('applies_to', 'depends_on', 'references', 'contradicts', 'supersedes', 'exception_to', 'approved_by')
    ),
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE (from_object_id, to_object_id, link_type)
);

CREATE TABLE IF NOT EXISTS knowledge_object_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_object_id INTEGER NOT NULL REFERENCES knowledge_objects(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    evidence_text TEXT NOT NULL DEFAULT '',
    evidence_location TEXT NOT NULL DEFAULT '',
    extraction_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (knowledge_object_id, source_id, evidence_location)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_object_id INTEGER NOT NULL REFERENCES knowledge_objects(id) ON DELETE CASCADE,
    reviewer TEXT NOT NULL,
    review_action TEXT NOT NULL CHECK (
        review_action IN ('approve', 'reject', 'mark_stale', 'mark_disputed', 'supersede')
    ),
    review_note TEXT NOT NULL DEFAULT '',
    previous_status TEXT NOT NULL DEFAULT '',
    new_status TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS authority_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    authority_class TEXT NOT NULL,
    rank_order INTEGER NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (domain_id, authority_class),
    UNIQUE (domain_id, rank_order)
);

CREATE INDEX IF NOT EXISTS idx_sources_domain_id ON sources(domain_id);
CREATE INDEX IF NOT EXISTS idx_sources_authority_class ON sources(authority_class);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_domain_id ON knowledge_objects(domain_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_type ON knowledge_objects(object_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_status ON knowledge_objects(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_freshness ON knowledge_objects(freshness_state);
CREATE INDEX IF NOT EXISTS idx_knowledge_objects_review_priority ON knowledge_objects(review_priority);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_from_object_id ON knowledge_links(from_object_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_to_object_id ON knowledge_links(to_object_id);
CREATE INDEX IF NOT EXISTS idx_object_sources_object_id ON knowledge_object_sources(knowledge_object_id);
CREATE INDEX IF NOT EXISTS idx_object_sources_source_id ON knowledge_object_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_reviews_object_id ON reviews(knowledge_object_id);
CREATE INDEX IF NOT EXISTS idx_authority_rules_domain_id ON authority_rules(domain_id);
