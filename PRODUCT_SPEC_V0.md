# Context Farm Product Spec v0

Status: draft  
Date: 2026-05-28

## Summary

Context Farm is operational memory software for small businesses and AI fleets.

It captures knowledge that usually lives in one operator's head, structures it into grounded domain context, and makes it available to both humans and agents through search, Q&A, and structured retrieval.

The core job is not "store documents" and not "chat with files." The core job is:

1. capture tribal knowledge
2. turn it into usable operational truth
3. distribute it across a team or agent fleet

---

## Target Market

Primary market:
- small businesses under 100 employees
- founder-led teams
- service businesses
- ops-heavy teams
- agencies
- internal teams with one critical lead or department head

Primary buyer:
- founder
- operations lead
- finance lead
- department head
- technical lead

Primary user:
- the person who currently answers the same questions repeatedly
- the team members who depend on that person
- internal AI agents that need stable operating context

---

## Core Problem

In small teams, critical knowledge is rarely missing. It is concentrated.

One person knows:
- the real workflow
- the exceptions to the workflow
- the thresholds that trigger action
- the caveats not written in the SOP
- which source is authoritative when documents conflict

That creates four failure modes:

1. repeated interruptions
   The same person gets asked the same questions over and over.

2. slow onboarding
   New staff cannot act confidently without finding the one person who knows.

3. inconsistent execution
   Different team members apply different interpretations of the same process.

4. weak AI automation
   Agents can read documents, but they do not know what is actually true in practice.

---

## Product Thesis

Small businesses do not need a giant enterprise knowledge platform.

They need a system that can:
- ingest messy operational material
- interview or seed a domain owner quickly
- extract procedures, constraints, exceptions, and decisions
- preserve provenance
- expose grounded answers to humans and agents

Context Farm is a domain knowledge compiler for that job.

## Practical Moat

The durable differentiator is not "we also extract structure."

That alone is not a moat. Everyone in this category is moving toward richer extraction.

The stronger wedge is:
- local-first deployment
- no-data-leaves-your-building operation
- explicit constraint/exception handling for operational workflows
- one shared context layer for both humans and agent fleets

For small teams with compliance sensitivity, internal process sensitivity, or strong preference for self-hosting, this matters more than generic AI search positioning.

---

## Product Positioning

Working positioning:

"Context Farm turns tribal business knowledge into grounded operational context for humans and AI agents."

Alternate versions:
- "Operational memory for small teams."
- "Capture what your lead operator knows before it becomes a bottleneck."
- "Ground your team and AI agents in how your business actually works."

What it is not:
- not a generic document store
- not enterprise search
- not a pure vector database
- not a heavyweight ontology platform

---

## Ideal First Use Cases

### 1. Operations lead knowledge capture

A team depends on one lead to answer process questions, exceptions, and edge cases.

Examples:
- service dispatch
- client onboarding
- billing operations
- internal approvals
- inventory or fulfillment exceptions

### 2. Finance or admin process grounding

The team needs to know:
- which account or budget rules apply
- when a transaction is unusual
- what thresholds require escalation
- what the approved operating procedure actually is

### 3. AI fleet grounding

Multiple agents need one shared operational memory layer so they:
- use the same constraints
- reference the same approved procedures
- stop making conflicting decisions

---

## User Outcomes

The product is successful if it:
- reduces repeated operator interruptions
- shortens onboarding time
- improves consistency of process execution
- gives agents grounded context instead of loose retrieval
- preserves institutional knowledge when one person is unavailable

---

## MVP Scope

Version 0 should do five things well.

### 1. Ingest operational material

Inputs:
- PDF
- URL
- pasted text
- meeting transcript
- AI conversation export
- plain-language domain seed

Later:
- Slack
- Notion
- Google Docs/Drive
- email threads
- CSV/JSON business records

### 2. Compile into typed operational knowledge

Extract and store:
- facts
- procedures
- constraints
- exceptions
- decisions
- source references

Each knowledge unit should carry:
- provenance
- source type
- confidence
- freshness or last review metadata

### 3. Seed a domain from a lead operator

The operator can describe the domain in plain English:
- what matters
- what entities exist
- what rules apply
- what exceptions are common
- which sources outrank others

That seed becomes the initial domain schema for subsequent ingestion.

### 4. Retrieve knowledge in three ways

- search: find relevant knowledge quickly
- ask: grounded Q&A with citations
- brief: generate a concise operational briefing on a person, process, account, project, or domain

### 5. Review and govern

The domain owner needs a lightweight console for:
- approving important extracted facts
- resolving contradictions
- marking stale guidance
- updating authority rules

Without this, trust will collapse.

Important v0 constraint:
- governance must not require row-by-row approval of every important object
- review has to be batched and impact-prioritized or the product will stall

---

## Product Surface

### Human-facing

- ingestion UI
- domain setup flow
- review queue
- search UI
- Q&A UI
- briefing UI

### Agent-facing

API endpoints:
- `POST /seed`
- `POST /ingest`
- `GET /search`
- `POST /ask`
- `POST /brief`
- `POST /facts/query`

Potential later endpoints:
- `POST /facts/approve`
- `POST /facts/expire`
- `POST /domain/reseed`

---

## Data Model

Context Farm should not expose "knowledge graph" language as the primary product story, but internally it should treat the domain as structured knowledge.

Core object types:
- `Fact`
- `Procedure`
- `Constraint`
- `Exception`
- `Decision`
- `Entity`
- `Source`

Key relationships:
- applies_to
- depends_on
- contradicts
- supersedes
- references
- exception_to
- approved_by

This model is enough to be useful without becoming a research project on day one.

---

## Differentiation

### Versus generic RAG

Generic RAG answers:
"Which documents mention this?"

Context Farm answers:
"What is true here, what rule applies, what exceptions exist, and where did that come from?"

### Versus internal wikis

Wikis store useful content, but they depend on someone keeping them organized and current.

Context Farm actively compiles messy inputs into structured operational knowledge.

### Versus enterprise search

Enterprise search helps users find documents.

Context Farm helps teams and agents operate correctly inside a domain.

---

## Why This Can Win

The right wedge is not broad search. It is key-person dependency reduction.

That is painful, common, and legible in SMBs.

The winning attributes are:
- fast setup
- low admin burden
- visible provenance
- support for exceptions and real process nuance
- strong fit for both humans and agents

---

## Existing Assets

The product does not start from zero.

Existing foundation:
- Orchestra extraction process with months of use
- conversation-to-knowledge pipeline
- wiki compile pipeline
- hybrid search and grounded Q&A
- local inference integration
- production usage across finance, research, and infrastructure domains

This matters because the product story can honestly say:
- the pipeline has already been used in real operations
- the product direction emerged from internal necessity
- the hard part is not hypothetical

---

## What Exists Today vs What Is Planned

### Exists today

- ingestion from PDF, URL, and text
- topic/domain seeding
- compile pipeline into structured wiki articles
- hybrid search
- grounded Q&A
- local inference-backed operation

### In progress or partially specified

- explicit domain schema lifecycle
- fact-level storage and retrieval
- authority weighting and conflict resolution
- structured SQLite query layer
- review queue and governance console
- decay and staleness management

This distinction should stay explicit in all external materials.

---

## Risks

### 1. Trust failure

If the system confidently presents the wrong operational rule, users will stop relying on it.

Mitigation:
- provenance everywhere
- approval flow for high-impact facts
- clear authority ranking

### 2. Schema drift

The original domain model will get stale as new material arrives.

Mitigation:
- drift detection
- recommended schema updates
- periodic reseed flow

### 3. Review overload

If every extracted fact needs manual cleanup, the product becomes a chore.

Mitigation:
- prioritize review by impact
- auto-accept low-risk facts
- review only contradictions, constraints, and exceptions first

### 4. Overbuilding graph complexity

Too much ontology too early will slow product velocity and confuse users.

Mitigation:
- keep the external product simple
- use structured internals without selling graph theory

---

## Product Principles

1. provenance over cleverness  
Every important answer should show where it came from.

2. speed over ontology purity  
The system should be useful quickly, even if the schema is not elegant.

3. exceptions matter  
The product must capture caveats, thresholds, and local rules, not just official policy.

4. humans first, agents second, both supported  
If humans do not trust the output, agents should not either.

5. low-admin by default  
SMBs do not have knowledge engineers.

---

## Initial ICP

Best first customers:
- owner-operated service business
- small agency with a strong delivery lead
- finance/admin-heavy SMB
- internal ops team supporting a growing company
- AI-forward small team running multiple automations or agents

Avoid first:
- giant enterprise rollout
- company-wide search replacement
- highly regulated deployments needing deep compliance features on day one

---

## Pricing Logic

Too early to set numbers, but the model should likely follow team value, not pure storage.

Potential basis:
- per workspace
- per domain
- per active operator seat
- higher tier for agent/API usage

The economic argument is straightforward:
- one lead interrupted less often
- one new hire onboarded faster
- one costly process error avoided

That is easier to sell than "better search."

---

## 30 / 60 / 90

### 30 days

- formalize product language
- tighten domain seed flow
- define typed knowledge objects
- specify fact/procedure/constraint storage format
- build example demo domains for 2-3 SMB scenarios

### 60 days

- ship review queue
- ship fact-level retrieval
- ship contradiction handling for critical facts
- produce a working agent-facing API spec

### 90 days

- pilot with one real small business or internal equivalent
- measure interruption reduction and answer quality
- add freshness and review lifecycle
- package human + agent workflows into a coherent product demo

---

## One-Sentence Product Definition

Context Farm is operational memory software that captures tribal knowledge from small teams and turns it into grounded context for both humans and AI agents.
