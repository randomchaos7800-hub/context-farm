# Context Farm

Operational memory for small teams and AI fleets.

Context Farm captures tribal business knowledge, structures it into grounded domain context, and makes it available to both humans and agents through search, Q&A, and structured retrieval.

The target is not enterprise search. The target is the small team where one operator, department head, or founder carries too much of the company in their head.

Research by [Boundary Labs](https://boundarylabs.org/context-farm.html). Built from the Orchestra extraction pipeline and months of real internal use.

## What It Is

Most knowledge tools store documents.

Context Farm is meant to compile operational knowledge:
- procedures
- constraints
- exceptions
- decisions
- source-backed facts

The goal is to answer:
- what is true here
- what rule applies
- what exceptions exist
- where that guidance came from

## Why It Exists

Small teams usually do not have a knowledge shortage. They have a knowledge concentration problem.

One person knows:
- how the work actually gets done
- which exceptions matter
- which documents are authoritative
- what thresholds trigger action
- what new people always get wrong

That creates:
- repeated interruptions
- slow onboarding
- inconsistent execution
- weak AI automation

Context Farm is designed to reduce that key-person dependency.

## Product Direction

The system is being designed around five jobs:

1. ingest messy operational inputs
2. seed a domain from plain-English operator knowledge
3. compile sources into readable and structured knowledge
4. serve grounded answers to humans and agents
5. keep the knowledge trustworthy through provenance and review

## Current Foundation

The product direction grows out of working infrastructure that already exists:

- PDF, URL, and text ingestion
- topic/domain seeding
- two-pass LLM compile pipeline
- structured wiki article generation
- hybrid BM25 + vector search
- grounded Q&A over compiled content
- local inference-backed operation

These foundations come from:
- [Orchestra](https://github.com/randomchaos7800-hub/orchestra)
- [Orchestra Knowledge Capture](https://github.com/randomchaos7800-hub/orchestra-knowledge-capture)

## Architecture Shape

Context Farm v0 is intended to be a layered system:

```text
inputs
  -> ingestion
  -> compile
  -> domain model
  -> structured fact store
  -> governance
  -> search / ask / brief / agent APIs
```

The important architectural move is:
- keep the proven article compile pipeline
- add a structured knowledge layer for facts, procedures, constraints, exceptions, and decisions

## Status

Early product and research stage.

What exists today:
- ingestion and compile pipeline
- article-centric knowledge base
- article search and grounded Q&A

What is being specified and built next:
- structured fact storage
- authority and contradiction handling
- review queue
- fact-aware retrieval
- briefing workflows

## Documents

- [Product Spec v0](./PRODUCT_SPEC_V0.md)
- [Architecture Spec v0](./ARCHITECTURE_SPEC_V0.md)
- [MVP Roadmap](./ROADMAP_MVP.md)
- [Structured Object Schema v0](./STRUCTURED_OBJECT_SCHEMA_V0.md)
- [Extraction Design v0](./EXTRACTION_DESIGN_V0.md)
- [Demo Implementation v0](./DEMO_IMPLEMENTATION_V0.md)
- [Pitch v0](./PITCH_V0.md)
- [Landing Page Copy v0](./LANDING_PAGE_COPY_V0.md)
- [Demo Scenarios v0](./DEMO_SCENARIOS_V0.md)

## Milestone 1 Artifacts

- initial SQLite schema: [sql/0001_init_structured_store.sql](./sql/0001_init_structured_store.sql)
- first structured object contract: [STRUCTURED_OBJECT_SCHEMA_V0.md](./STRUCTURED_OBJECT_SCHEMA_V0.md)
- first demo domain seed: [examples/domain-service-dispatch.json](./examples/domain-service-dispatch.json)
- manual demo object set: [examples/service-dispatch-manual-objects.json](./examples/service-dispatch-manual-objects.json)
- prototype scripts: [scripts/build_demo_db.py](./scripts/build_demo_db.py), [scripts/query_demo.py](./scripts/query_demo.py), [scripts/brief_demo.py](./scripts/brief_demo.py)

## Intended Users

Best fit:
- small businesses under 100 employees
- founder-led teams
- operations-heavy teams
- finance/admin-heavy teams
- agencies and service businesses
- AI-heavy teams running multiple agents against one operating context

## Non-Goals

Context Farm is not being built as:
- a generic vector search app
- a broad enterprise search replacement
- a heavyweight ontology platform

## Contact

- **Email**: research@cha0tik.com
- **X**: [@cha0tikdino](https://x.com/cha0tikdino)
- **Site**: [boundarylabs.org/context-farm.html](https://boundarylabs.org/context-farm.html)

MIT License
