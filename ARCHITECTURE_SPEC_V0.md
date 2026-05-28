# Context Farm Architecture Spec v0

Status: draft  
Date: 2026-05-28

## Purpose

This document defines the technical architecture for Context Farm v0.

It is written to answer four questions:

1. what exists already
2. what Context Farm adds on top
3. how the system should be structured
4. what needs to be built first

This is an architecture spec, not pitch copy. It distinguishes between:
- proven current components
- components that can be built directly from existing code
- components that are still new design work

---

## System Definition

Context Farm is a domain knowledge compiler for small teams and AI fleets.

It ingests messy operational material, compiles it into typed domain knowledge, and serves grounded context to humans and agents.

The architecture is layered:

1. ingestion
2. compilation
3. domain modeling
4. fact storage and retrieval
5. governance
6. human and agent interfaces

---

## Architectural Goals

The system should:

- capture knowledge from real operational inputs
- preserve source provenance
- separate raw inputs from compiled knowledge
- support both semantic and structured retrieval
- model constraints, exceptions, and decisions explicitly
- keep human review in the loop for high-impact knowledge
- serve both humans and multi-agent systems

The system should not:

- depend on one brittle database as the only source of truth
- expose ontology complexity to end users
- require enterprise-grade setup to be useful

---

## Current Foundation

Context Farm does not start from scratch.

### Proven existing components

From Orchestra and Orchestra Knowledge Capture:

- raw content ingestion from `PDF`, `URL`, and `text`
- topic/domain seeding flow
- two-pass LLM compile pipeline
- wiki article generation with YAML frontmatter
- typed wiki links
- backlink injection
- hybrid BM25 + vector search over compiled articles
- grounded Q&A over compiled wiki content
- FastAPI service layer

### Important current limitation

The current system is article-centric.

It compiles knowledge into wiki pages and retrieves those pages. That is useful, but it is not yet a true fact- and constraint-centric operational memory system.

Context Farm v0 should preserve the wiki layer while adding a structured knowledge layer above and alongside it.

---

## High-Level Architecture

```text
INPUTS
  PDFs / URLs / text / transcripts / chat exports / operator seed
      |
      v
INGESTION LAYER
  extractors, normalization, raw source preservation
      |
      v
COMPILE LAYER
  plan -> write -> link -> index
  article-oriented knowledge artifacts
      |
      +------------------------+
      |                        |
      v                        v
DOMAIN MODEL LAYER        SEARCH INDEX LAYER
  entities, procedures,   BM25 + vector article retrieval
  constraints, exceptions,
  decisions, authority
      |
      v
FACT STORE LAYER
  structured knowledge objects
  provenance, confidence, freshness
      |
      v
GOVERNANCE LAYER
  review queue, contradiction handling,
  authority rules, staleness
      |
      v
SERVING LAYER
  search / ask / brief / structured query / agent APIs
```

---

## Core Layers

## 1. Ingestion Layer

### Responsibility

Accept raw operational material and normalize it into a stable internal source format.

### Inputs

- PDF
- URL
- pasted text
- meeting transcript
- AI conversation export
- domain seed entered by a human operator

### Requirements

- preserve raw input exactly or near-exactly
- assign source metadata at ingest time
- support batch and single-item ingestion
- allow replay and recompile from raw sources

### Current implementation status

Mostly exists in Orchestra Knowledge Capture for:
- PDF
- URL
- text
- topic/domain seed

### Required v0 additions

- transcript ingestion path
- AI conversation export ingestion path
- richer source metadata model

### Source metadata should include

- source id
- source type
- ingestion timestamp
- original title or label
- operator or uploader
- authority class
- domain assignment
- checksum or content hash

---

## 2. Compile Layer

### Responsibility

Transform raw sources into structured domain artifacts that are readable, linked, and useful for later extraction and retrieval.

### Current implementation

Already present:
- pass 1: plan article creation/update
- pass 2: write article content
- inject links and backlinks
- rebuild wiki index

### v0 role

Keep this layer.

The compile layer remains the readable and inspectable narrative layer of the system. It gives operators a human-legible knowledge base and provides useful intermediate structure even before fact extraction is perfect.

### Output artifacts

- wiki articles
- article frontmatter
- link graph
- search index inputs

### Architectural note

The compile layer should not be the final truth model.

It is an intermediate and human-facing representation. The structured fact layer below is where operational retrieval should increasingly anchor.

For v0, the wiki layer has four explicit jobs:
- human-readable audit trail
- intermediate normalization before structured extraction
- fallback retrieval surface while structured extraction is incomplete
- debugging surface for extraction failures

If it cannot justify those jobs in the product, it should be reduced later rather than preserved by habit.

---

## 3. Domain Model Layer

### Responsibility

Represent what kinds of things matter in a domain and how they relate.

This is the key differentiator layer.

### Input

- plain-English domain seed
- previously compiled knowledge
- operator review edits

### Output

- domain schema
- entity types
- relationship types
- constraint classes
- authority rules
- extraction hints

### Example domain schema output

For an operations domain:
- entities: client, job, invoice, approval, service window
- procedures: intake, scheduling, escalation, closeout
- constraints: approval thresholds, response windows, payment rules
- exceptions: VIP client handling, emergency overrides
- sources of authority: signed contract > internal SOP > notes

### v0 design choice

Do not overbuild this into a complex ontology editor.

For v0, the schema can remain lightweight:
- typed objects
- typed relationships
- a simple authority hierarchy
- domain-specific extraction guidance

### Required v0 components

- schema representation format
- schema generation from seed prompt
- schema update/reseed flow
- domain-specific extraction prompt templates

---

## 4. Fact Store Layer

### Responsibility

Store the operational knowledge units that agents and humans actually need to query.

This layer is the architectural leap from wiki-centric retrieval to domain-grounded retrieval.

### Knowledge object types

- `Fact`
- `Procedure`
- `Constraint`
- `Exception`
- `Decision`
- `Entity`
- `Source`

### Suggested object shape

```json
{
  "id": "constraint.ops-float-minimum",
  "type": "Constraint",
  "domain": "finance",
  "title": "OPS float minimum",
  "statement": "OPS account must remain above $500.",
  "applies_to": ["account.ops"],
  "exceptions": ["exception.manual-emergency-override"],
  "source_ids": ["source.pdf.policy-2026-05"],
  "authority": "policy",
  "confidence": 0.94,
  "status": "approved",
  "reviewed_at": "2026-05-28T10:00:00Z",
  "updated_at": "2026-05-28T09:40:00Z"
}
```

### Storage design

For v0, use a dual-store approach:

- `SQLite` for structured facts, filters, statuses, and relationships
- `ChromaDB` for semantic/article retrieval

SQLite is enough for v0 because:
- the target market is SMB
- deployments are likely single-tenant and modest scale
- operational simplicity matters more than theoretical graph elegance

### Suggested SQLite tables

- `domains`
- `sources`
- `knowledge_objects`
- `knowledge_links`
- `reviews`
- `authority_rules`
- `ingestion_runs`

### Suggested fields for knowledge_objects

- id
- domain_id
- type
- title
- canonical_statement
- body_json
- status
- confidence
- authority_class
- freshness_state
- created_at
- updated_at
- reviewed_at

### Relationship storage

Use a link table:
- from_id
- to_id
- link_type

This is sufficient for typed graph traversal without introducing a graph database yet.

---

## 5. Search and Retrieval Layer

### Responsibility

Return useful operational knowledge to humans and agents.

This layer should support multiple retrieval modes because one mode is not enough.

### Retrieval modes

1. article search  
Hybrid BM25 + vector retrieval over compiled wiki content.

2. fact search  
Semantic and filtered retrieval over structured knowledge objects.

3. structured query  
Filter by domain, type, status, authority, entity, or freshness.

4. briefing  
Assemble a compact operational summary for a topic, entity, process, or account.

5. grounded Q&A  
Answer using article + fact context with citations and source references.

### Current implementation status

Exists today:
- article search
- grounded Q&A over article retrieval

### Required v0 additions

- fact-aware retrieval
- merged context builder for Q&A
- briefing assembly logic
- status/authority-aware filtering

Important sequencing note:
- retrieval and briefing should first be proven on a manually seeded demo object set
- full automation should follow after the demo interaction is validated

### Retrieval policy

High-impact answers should prioritize:
- approved knowledge objects
- higher-authority sources
- fresher items
- explicit constraints and exceptions

This is one of the most important product behaviors.

---

## 6. Governance Layer

### Responsibility

Make the knowledge trustworthy enough to use operationally.

Without governance, Context Farm becomes an attractive but unreliable archive.

### Key functions

- contradiction detection
- authority weighting
- approval workflow
- freshness review
- stale or superseded marking
- audit trail of changes

### Governance model for v0

Keep it lightweight.

Not every item needs review. Only:
- constraints
- exceptions
- decisions
- contradictions
- low-confidence extractions

Governance load must be constrained.

If the system routes every meaningful extracted item into review, the target user will abandon it. The review queue must batch related objects and auto-approve low-risk cases where possible.

### Required governance states

- draft
- approved
- disputed
- stale
- superseded

### Authority model

Each domain should define a simple source hierarchy, for example:
- signed policy
- official SOP
- manager note
- meeting transcript
- informal text paste

Contradictions should be flagged against this hierarchy rather than silently merged.

---

## 7. Serving Layer

### Responsibility

Expose Context Farm to humans and agents.

### Human-facing surfaces

- ingest screen
- domain setup screen
- review queue
- search
- ask
- brief
- object detail pages

### Agent-facing APIs

Core v0 endpoints:

- `POST /seed`
- `POST /ingest`
- `GET /search`
- `POST /ask`
- `POST /brief`
- `POST /facts/query`

Useful later endpoints:

- `POST /facts/approve`
- `POST /facts/reject`
- `POST /facts/expire`
- `POST /domains/reseed`
- `GET /sources/{id}`

### Response design principle

Every high-value response should be able to expose:
- answer
- supporting knowledge objects
- source ids
- authority level
- freshness status

Agents need machine-readable grounding, not just prose.

---

## Data Flow

### Ingestion and compile flow

```text
raw input
  -> source record created
  -> content normalized
  -> raw artifact stored
  -> compile pipeline generates/updates wiki articles
  -> article index refreshed
  -> domain extraction pass creates or updates structured knowledge objects
  -> contradictions and low-confidence items sent to review queue
```

### Query flow

```text
question or request
  -> domain resolution
  -> retrieve article context
  -> retrieve structured fact context
  -> apply authority/freshness filters
  -> assemble context packet
  -> generate answer or briefing
  -> return citations, sources, and supporting objects
```

---

## Canonical Stores

Context Farm should maintain explicit separation between stores.

### 1. Raw source store

Purpose:
- replay
- audit
- recompile

Format:
- flat files on disk

### 2. Wiki store

Purpose:
- human-legible compiled knowledge
- link graph
- search index source

Format:
- markdown files with YAML frontmatter

### 3. Structured fact store

Purpose:
- operational retrieval
- governance
- agent grounding

Format:
- SQLite

### 4. Semantic search store

Purpose:
- semantic recall over article content and possibly fact summaries

Format:
- ChromaDB

This multi-store design is acceptable because each store has a clear role and the system remains inspectable.

---

## Deployment Model

For v0, optimize for simple self-hosted deployment.

### Recommended deployment shape

- FastAPI app
- local disk for raw and wiki stores
- SQLite for structured knowledge
- ChromaDB local persistence
- OpenAI-compatible inference backend

### Why this fits the target market

- low infrastructure overhead
- easy backup
- easy portability
- understandable failure modes

This matches the SMB market much better than a cloud-native microservice architecture.

---

## Security and Tenancy

### v0 assumption

Single-tenant workspaces.

### Requirements

- workspace separation at the application level
- source and object audit trail
- API authentication
- exportable raw and compiled data

### Later needs

- per-user roles
- approval permissions
- domain-level access policies
- external source auth and sync permissions

---

## Observability

The system should expose:

- ingestion run status
- compile success/failure
- extraction confidence distribution
- contradiction counts
- review queue size
- source freshness metrics
- query latency
- answer/source coverage

This matters because trust is partly operational.

---

## What Must Be Built New

These are the real net-new components for Context Farm v0:

- structured knowledge object schema
- SQLite fact store
- extraction pass from compiled/raw content into typed objects
- contradiction and authority handling
- review queue
- fact-aware retrieval
- briefing endpoint
- freshness and staleness model

These are the pieces that turn Orchestra-derived tooling into a product.

---

## What Can Be Reused Directly

These pieces can be reused with limited changes:

- FastAPI service shell
- ingest handlers for PDF/URL/text
- domain seeding concept and partial implementation
- compile pipeline
- article storage model
- hybrid article search
- grounded Q&A skeleton

---

## Non-Goals for v0

Do not do these first:

- graph database migration
- complex ontology editor
- enterprise-wide permissions matrix
- full Slack/Google/Notion sync on day one
- autonomous agent write-back without review

These may come later, but they are not the first hill to climb.

---

## Build Order

### Phase 1

- define structured knowledge schema
- implement SQLite store
- write object extraction pass
- persist provenance and authority metadata

### Phase 2

- implement review queue
- detect contradictions
- add approval and status fields
- support fact queries

### Phase 3

- merge article and fact retrieval for Q&A
- add briefing endpoint
- expose governance in the UI

### Phase 4

- add freshness policies
- add schema drift detection
- add richer ingest sources

---

## Architecture Summary

Context Farm v0 should be built as a layered extension of Orchestra, not a rewrite.

The important move is:
- keep the proven ingestion and article compile pipeline
- add a structured domain knowledge layer beside it
- serve both humans and agents from that grounded operational layer

That preserves the real work already done while moving toward the actual product.
