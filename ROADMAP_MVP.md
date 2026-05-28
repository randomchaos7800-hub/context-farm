# Context Farm MVP Roadmap

Status: draft  
Date: 2026-05-28

## Why This Exists

Context Farm is not a fresh side project.

It is the product layer that sits on top of work already done across:
- memory systems
- agent frameworks
- local inference infrastructure
- evaluation and benchmarking discipline
- long-running internal operational use

The goal of this roadmap is to turn that accumulated infrastructure into a demonstrable MVP.

The MVP does not need to solve the whole problem. It needs to prove three things:

1. Context Farm can capture concentrated operator knowledge
2. it can structure that knowledge into grounded operational context
3. it can serve that context usefully to humans and agents

---

## MVP Definition

Context Farm MVP is achieved when a small-team workflow can be demonstrated end to end:

1. ingest messy operational material
2. seed a domain from operator knowledge
3. compile and extract structured knowledge objects
4. review high-impact facts and contradictions
5. answer domain questions with grounded, source-backed output
6. provide the same operational context through an API to an agent

If that works reliably for one or two concrete SMB scenarios, the MVP is real.

---

## What Already Exists

These are not roadmap items. They are starting assets.

### Proven infrastructure

- local inference serving through tower proxy
- working orchestration environment
- long-running internal knowledge capture usage
- benchmarking and testing culture
- months of operational iteration

### Reusable software foundation

- Orchestra extraction pipeline
- Orchestra Knowledge Capture ingestion layer
- two-pass compile pipeline
- wiki-based knowledge artifacts
- hybrid search
- grounded Q&A skeleton
- FastAPI service surface

### Strategic implication

The MVP should reuse as much of this as possible.

The real work now is not "can we ingest and search content?"

The real work is:
- structured operational knowledge
- trust/governance
- clear demo workflows

---

## MVP Scope

The MVP should support:

- one workspace
- one or two domains
- one primary human operator
- one small team use case
- one agent-facing retrieval path

That is enough.

It does not need:
- full multi-tenant SaaS
- enterprise permissions
- broad external integrations
- complex ontology editing

---

## Success Criteria

The MVP is successful if it can demonstrate:

### Product success

- one lead operator's knowledge can be seeded and captured
- the system can answer real operational questions with provenance
- exceptions and constraints are visible, not buried
- the output is useful enough that a team member would trust it for first-pass guidance

### Technical success

- structured knowledge objects are persisted and queryable
- article retrieval and fact retrieval work together
- reviewable governance states exist
- a simple agent can consume grounded context through an API

### Demo success

- one live demo can be run end to end in under 10 minutes
- the product value is obvious without a long explanation

---

## MVP Milestones

## Milestone 1: Structured Knowledge Core

### Goal

Move from article-only knowledge to typed operational knowledge objects.

### Deliverables

- define knowledge object schema
- implement SQLite structured store
- create persistence model for:
  - facts
  - procedures
  - constraints
  - exceptions
  - decisions
  - sources
- store provenance, confidence, authority, and status fields

### Depends on

- existing compile pipeline
- domain model assumptions from seed flow

### Exit criteria

- compiled or raw content can produce persisted structured objects
- objects can be queried directly outside the article layer

---

## Milestone 2: Extraction Pass

### Goal

Add the actual bridge from compiled knowledge into structured operational objects.

### Deliverables

- extraction prompt/spec for typed objects
- object creation from raw or compiled content
- source-to-object linkage
- confidence scoring
- authority-class assignment

### Preferred approach

Do not extract directly from raw inputs only.

Use the compiled article layer as a stabilizing intermediate representation where helpful, then extract typed objects from there. This reduces noise and reuses the work already done.

### Exit criteria

- one source can yield a set of typed objects with source references
- extracted constraints and exceptions are visible and inspectable

---

## Milestone 3: Governance Layer

### Goal

Make the knowledge trustworthy enough to use operationally.

### Deliverables

- statuses: draft, approved, disputed, stale, superseded
- contradiction detection
- authority hierarchy per domain
- review queue for high-impact items
- manual approval or rejection path

### Review focus for MVP

Only require review for:
- constraints
- exceptions
- decisions
- contradictions
- low-confidence items

### Exit criteria

- critical extracted knowledge can be approved or disputed
- contradictory rules are surfaced instead of silently merged

---

## Milestone 4: Fact-Aware Retrieval

### Goal

Serve better grounded answers by combining article retrieval with structured knowledge retrieval.

### Deliverables

- fact query endpoint
- retrieval policy that prioritizes approved/high-authority/fresh items
- merged context assembly for Q&A
- citations that include both source and structured object references

### Exit criteria

- answers can cite not only articles but specific structured knowledge
- rule + exception retrieval works for at least one demo domain

---

## Milestone 5: Briefing Workflow

### Goal

Demonstrate that the product can do more than search. It should generate concise operational briefings.

### Deliverables

- `POST /brief`
- briefing templates by object or domain type
- summary assembly from facts, procedures, constraints, and exceptions

### Good briefing examples

- "Brief me on after-hours dispatch rules"
- "Brief me on account transfer constraints"
- "Brief me on approval thresholds for this workflow"

### Exit criteria

- at least one domain can produce a useful operator-facing briefing from stored knowledge

---

## Milestone 6: Demo-Ready Workflow

### Goal

Package the MVP so progress is visible and credible.

### Deliverables

- one primary demo domain
- one secondary demo domain
- prepared source inputs
- seeded domain examples
- example questions
- example agent retrieval call

### Recommended demo domains

Primary:
- service business operations

Secondary:
- finance/admin operations

### Exit criteria

- a realistic demo can be run end to end by a human operator
- the product value is obvious in under 10 minutes

---

## Milestone 7: Agent Integration Proof

### Goal

Show that the same knowledge layer can ground an agent, not just a human user.

### Deliverables

- one agent retrieval client using the Context Farm API
- one example decision or recommendation grounded by returned context
- one example where constraint or exception changes the agent answer

### Exit criteria

- an agent can retrieve structured operational context and behave differently because of it

This matters because the long-term vision includes both small teams and multi-agent fleets.

---

## Build Order

Recommended order:

1. Structured Knowledge Core
2. Extraction Pass
3. Governance Layer
4. Fact-Aware Retrieval
5. Briefing Workflow
6. Demo-Ready Workflow
7. Agent Integration Proof

This order matters because retrieval and demo quality will be weak if the structured layer and governance are not in place first.

---

## Suggested Work Phases

## Phase A: Core System

Focus:
- schema
- SQLite store
- extraction pass

Success:
- typed knowledge exists and persists

## Phase B: Trust Layer

Focus:
- statuses
- contradictions
- approvals

Success:
- high-impact knowledge becomes governable

## Phase C: Retrieval Layer

Focus:
- merged retrieval
- briefings
- API responses

Success:
- humans and agents can consume grounded knowledge cleanly

## Phase D: Productization Layer

Focus:
- demo domains
- walkthrough
- clearer UX

Success:
- progress is externally demonstrable

---

## What To Measure

The MVP should generate visible evidence of progress.

Track:
- ingestion runs completed
- knowledge objects extracted per domain
- % of high-impact objects reviewed
- contradiction count
- answer/source coverage
- time to answer a demo question
- whether answer includes rule + exception + provenance

This matters because the point is not just to build. It is to show the system getting more operationally credible over time.

---

## What Not To Do Yet

Avoid these until the MVP is proven:

- broad external integrations
- elaborate multi-user permission models
- graph database migration
- generic horizontal knowledge product positioning
- too many demo domains
- autonomous write-back by agents

The main risk is over-expanding before the core workflow is defensible.

---

## Recommended Immediate Next Steps

1. Define the structured knowledge object schema in concrete file and table form
2. Implement the SQLite store
3. Design the extraction pass for facts, constraints, exceptions, and decisions
4. Build one demo domain all the way through before generalizing

That is the shortest path to real progress.

---

## Strategic Summary

Context Farm is the convergence point of the broader lab:

- memory became knowledge capture
- agents created the need for grounded operational context
- local inference made the system economically practical
- benchmarking discipline made the stack measurable

Now the work is to integrate those pieces into a product that solves a clear small-team problem.

That product does not need to be huge to be real.

It needs to show that concentrated operator knowledge can be captured, structured, governed, and served back in a way that improves how humans and agents operate.
