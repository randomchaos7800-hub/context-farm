# Demo Implementation v0

Status: draft  
Date: 2026-05-28

## Purpose

This document describes the first executable demo path for Context Farm.

It intentionally starts with a manual domain object set. That is deliberate. The goal is to prove the retrieval and briefing interaction before automating the full extraction pipeline.

## Files

- domain seed: [examples/domain-service-dispatch.json](./examples/domain-service-dispatch.json)
- manual structured objects: [examples/service-dispatch-manual-objects.json](./examples/service-dispatch-manual-objects.json)
- SQLite schema: [sql/0001_init_structured_store.sql](./sql/0001_init_structured_store.sql)
- database builder: [scripts/build_demo_db.py](./scripts/build_demo_db.py)
- retrieval prototype: [scripts/query_demo.py](./scripts/query_demo.py)
- briefing prototype: [scripts/brief_demo.py](./scripts/brief_demo.py)

## Build The Demo DB

```bash
cd /home/dino/context-farm-repo
python3 scripts/build_demo_db.py
```

This creates:

- `demo/context_farm_demo.db`

with:

- 1 domain
- authority rules
- 3 sources
- 10 structured knowledge objects
- typed links
- object-to-source evidence mapping

## Retrieval Example

```bash
python3 scripts/query_demo.py \
  --db demo/context_farm_demo.db \
  --question "Can we waive the deposit for an emergency VIP client?"
```

## Briefing Example

```bash
python3 scripts/brief_demo.py \
  --db demo/context_farm_demo.db \
  --topic "after-hours scheduling"
```

## What This Proves

- the structured store is usable
- the demo domain is concrete
- rule + exception retrieval is legible
- a briefing can be generated from typed knowledge objects

## What This Does Not Prove Yet

- automated extraction quality
- contradiction handling under real noisy ingestion
- scalable review workflow
- production-grade UI

That work comes next. This prototype is intentionally the manual baseline.
