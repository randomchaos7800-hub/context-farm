# Context Farm

Domain-specific knowledge infrastructure for AI agent RAG pipelines.

Generic document stores return chunks of text. Agents need structured domain knowledge — the relationships, constraints, and facts that define a specific field or operation. Context Farm ingests raw material and produces a queryable knowledge graph agents can actually use.

Research by [Boundary Labs](https://boundarylabs.org/context-farm.html). Production system running on cha0tikhome. Code open-sourcing in progress.

---

## The Problem With Generic RAG

Most RAG pipelines split documents into chunks, embed them, and retrieve by similarity. This answers "what does this document say about X?" It does not answer "what is true about X in the context of this operation?"

The difference matters for agents. An agent querying a finance knowledge base needs to know not just that a document mentions a constraint — it needs to know the constraint applies, to which accounts, under what conditions, and what exceptions exist. Vector similarity retrieval returns the right chunks. It does not build the domain model.

Context Farm was built because every agent deployment at Boundary Labs hit the same wall: retrieval was returning relevant documents but the agent was still making domain errors. The chunks were there. The domain model was not.

---

## Architecture

```
INGESTION
─────────────────────────────────────────────────

  raw input       PDF / URL / text paste / plain-language seed
      ↓
  extractor       strip layout noise, identify structure
      ↓
  domain seeder   map content against domain schema
      ↓
  fact extractor  LLM pass: discrete facts with provenance tags
      ↓
  conflict        flag contradictions, assign authority weights
  resolver
      ↓
  dual store      ChromaDB (semantic) + SQLite (structured)

─────────────────────────────────────────────────
RETRIEVAL

  agent query → /retrieve   ranked facts with provenance
              → /query      structured SQLite filter
              → /seed       ingest new material at runtime
```

---

## The Four Stages

**1. Extract** — Any raw text becomes an input: PDFs, URLs, pasted text, or a plain-language domain description. The extractor strips layout noise, identifies structure, and prepares content for the LLM passes.

**2. Compile** — Two-pass LLM pipeline. Pass 1 (Plan): read source, return a JSON plan of which articles to create or update. Pass 2 (Write): generate each article — 300-500 word overview, sourced key claims, typed cross-reference links. Quality gate rejects orphaned articles, dead links, and unsourced claims.

**3. Link** — Every article cross-links to related articles using typed relationships: `depends_on`, `extends`, `contradicts`, `references`, `related`. Reciprocal backlinks are injected automatically. This graph structure lets agents traverse related context rather than retrieving isolated documents.

**4. Retrieve** — Two modes:
- **Semantic search**: hybrid BM25 + vector (all-MiniLM-L6-v2) with Reciprocal Rank Fusion. Returns ranked articles in under 1 second.
- **Grounded Q&A**: natural language question → retrieve top-N articles → LLM answers using only wiki content → answer cited and traceable.

---

## Domain Seeding

The key differentiator. Before ingestion, you describe the domain in plain English:

> "This is a personal finance system for a single operator. Relevant entities are accounts, transactions, bills, income events, and projections. Constraints include never overdrawing the OPS account, always maintaining a $500 float in SAVINGS, and flagging any unrecognized transaction over $200."

Context Farm generates a domain schema from that description — the entities, relationships, and constraints that define what facts matter and how they relate. All subsequent ingestion is mapped against this schema. Seeding a new domain takes under 30 minutes.

---

## Ingestion Sources

| Source | Status |
|--------|--------|
| PDF (PyPDF2, page-level provenance) | live |
| URL (requests + BeautifulSoup4) | live |
| Text paste | live |
| Plain-language domain seed | live |
| Structured data (CSV, JSON) | planned |

---

## Production Use

Context Farm runs in production on cha0tikhome powering three active knowledge bases:

**Finance domain** — Account rules, bill schedules, income events, constraint definitions. The finance agent queries this for every decision. Prevents the agent from recommending a transfer that violates the OPS float constraint.

**Research domain** — Inference optimization findings, benchmark results, hardware characterization notes accumulated across 130+ experiments. Source-of-truth for all inference numbers published on boundarylabs.org.

**Infrastructure domain** — Service topology, port assignments, startup dependencies, recovery procedures. Agents query this before taking any action touching the stack.

All ingestion runs against local inference via the proxy at `tower:8010`. No external API calls for fact extraction, schema generation, or conflict resolution. A full ingestion of a 50-page PDF takes 40–90 seconds at 117 t/s.

---

## Open Research Questions

**Conflict resolution at scale** — The current resolver flags contradictions and assigns authority weights by source type (policy PDF > URL > text paste). This breaks down when the contradiction is contextual: fact A is true for one subset of cases, fact B for another, both sources equally authoritative.

**Schema drift** — Domain schemas are generated at seeding time. As content is ingested, the schema becomes stale. Detecting and resolving schema drift without a full re-seed is unsolved.

**Cross-domain retrieval** — The three production knowledge bases are queried independently. A unified query interface spanning domain boundaries does not exist yet.

**Decay and staleness** — Facts have provenance but not timestamps-as-decay. A policy fact from six months ago may be obsolete. Adam Selene implements fact decay for agent memory; the same mechanism needs to be ported to Context Farm's knowledge graph.

---

## Relation to Orchestra

[Orchestra](https://github.com/randomchaos7800-hub/orchestra) and [Orchestra Knowledge Capture](https://github.com/randomchaos7800-hub/orchestra-knowledge-capture) are the open-source reference implementations of the compile pipeline and ingestion layer. They share the same wiki format: `wiki/concepts/`, `wiki/entities/`, `wiki/research/`, YAML frontmatter, `[[type:slug]]` cross-references.

Context Farm is the research system built on that foundation — adding domain schemas, dual storage (ChromaDB + SQLite), conflict resolution, and the production agent integration layer. Orchestra is the tool. Context Farm is what you build with it when the domain model matters.

---

## Status

Research infrastructure. Core compile pipeline stable and in production. Conflict resolver, dual storage, and FastAPI retrieval interface in active development. Code open-sourcing in progress as components stabilize.

---

## Contact

Research partnerships, infrastructure sponsorship, collaboration on agent knowledge grounding or RAG evaluation:

- **Email**: research@cha0tik.com
- **X**: [@cha0tikdino](https://x.com/cha0tikdino)
- **Site**: [boundarylabs.org/context-farm.html](https://boundarylabs.org/context-farm.html)

---

MIT License
