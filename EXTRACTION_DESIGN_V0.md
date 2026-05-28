# Extraction Design v0

Status: draft  
Date: 2026-05-28

## Purpose

This document defines the first concrete extraction design for Context Farm.

The structured store is not the product by itself. The product lives or dies on whether raw inputs can be turned into trustworthy operational objects with low enough review burden to be usable.

This document exists to make that explicit.

---

## Core Position

Extraction quality is the product.

Everything else:
- SQLite schema
- object model
- retrieval APIs
- briefings
- review queue

is supporting infrastructure around the extraction loop.

---

## v0 Design Goal

For v0, extraction should optimize for:

1. correct typing of high-impact objects
2. strong provenance
3. low operator review burden
4. explicit uncertainty when the model is not sure

It should not optimize for:

- exhaustive extraction of every possible fact
- elegant universal ontology
- autonomous approval

---

## Extraction Strategy

Use staged extraction, not one-pass freeform extraction.

### Stage 1: Source classification

Determine:
- source type
- likely authority class
- domain assignment
- whether the source is likely policy, process, note, transcript, or mixed

Important:
Authority class should not be guessed blindly from content alone when operator-supplied metadata exists.

v0 rule:
- prefer explicit operator/source metadata
- use model inference only as fallback
- always store whether authority was `declared` or `inferred`

### Stage 2: Candidate span extraction

Extract only candidate spans likely to contain:
- constraints
- exceptions
- decisions
- procedures
- durable operational facts

This narrows the problem.

Do not ask the model to fully classify the whole document at once.

### Stage 3: Object typing

For each candidate span, ask the model to classify it into one of:
- Fact
- Procedure
- Constraint
- Exception
- Decision
- Entity
- Reject

If uncertain, the model should return:
- top type
- alternative type
- rationale

### Stage 4: Canonicalization

Convert accepted candidates into normalized objects:
- title
- canonical statement
- body_json fields
- linked entities or related objects

### Stage 5: Review routing

Send only high-impact or low-confidence objects into the review queue.

---

## Type Definitions For Extraction

These distinctions need to be explicit in prompts and tests.

### Constraint

A rule, threshold, minimum, maximum, requirement, or prohibition that governs action.

Signals:
- must
- cannot
- requires approval
- minimum / maximum
- always / never

### Exception

A rule that narrows, overrides, or bypasses another rule under defined conditions.

Signals:
- unless
- except
- emergency override
- special case
- may bypass

Exception objects should almost always reference a target constraint or procedure.

### Procedure

A multi-step operational flow or action sequence.

Signals:
- step order
- if X then Y
- handoff between roles
- intake / approval / closeout style language

### Decision

A chosen policy, threshold, or operational path with continuing effect.

Signals:
- decided
- approved
- going forward
- effective immediately

### Fact

A durable operational truth that does not fit better elsewhere.

Signals:
- recurring schedule
- known account rule
- role ownership
- durable classification

### Entity

A durable object in the domain that other knowledge refers to.

Signals:
- named account
- client class
- role
- queue
- job type

---

## Confidence Design

Do not treat model self-confidence as a trustworthy scalar.

For v0, confidence should be composite.

### Confidence inputs

- extraction pattern strength
- object type ambiguity
- number of supporting sources
- authority class of supporting sources
- contradiction presence
- whether the source metadata was declared or inferred

### v0 scoring rule

Confidence may still be stored as `0.0-1.0`, but it should be derived by application logic, not copied from the model.

Example inputs:
- high-confidence constraint from signed policy with repeated support: `0.90+`
- exception from one operator interview with no corroboration: `0.65-0.80`
- ambiguous span with alternate type and weak support: `<0.60`

The model can provide:
- certainty label
- rationale
- alternate interpretation

But the system should compute the final numeric score.

---

## Authority Assignment

Authority class should follow a strict precedence rule:

1. operator-declared source metadata
2. ingestion connector metadata
3. filename/path/document-type heuristics
4. model inference as fallback

Never pretend inferred authority is as strong as declared authority.

The source record should include:
- `authority_class`
- `authority_assignment_method` = `declared | heuristic | inferred`

This matters for trust.

---

## Governance Load Control

Claude's criticism is correct: reviewing every important object is not viable.

v0 mitigation:

### Review only when any of these are true

- object type is `Constraint`, `Exception`, or `Decision`
- confidence is below threshold
- the object contradicts an approved object
- authority is inferred instead of declared
- the object would materially change an existing approved rule

### Auto-approve candidates when all are true

- object type is `Fact` or `Entity`
- source authority is high
- confidence is high
- no contradiction exists
- the object is not policy-shaping

### Review UX requirement

The review queue should batch by source and object cluster, not by isolated row.

The operator should review:
- "5 extracted rules from this policy"

not:
- "approve 5 separate rows one by one"

That is a hard requirement if this is going to be usable.

---

## The Wiki Layer's Job

The wiki layer should stay in v0, but it needs an explicit role.

Its jobs are:

1. human-readable audit trail
2. intermediate normalization layer before structured extraction
3. fallback retrieval surface when structured extraction is incomplete
4. debugging surface for extraction failures

If it does not serve these jobs, it should be cut later.

That means the UI should eventually let a reviewer inspect:
- source
- compiled article
- extracted objects

as one chain.

---

## Demo-First Implementation Rule

The roadmap should be demo-first, not pipeline-first.

Practical v0 sequence:

1. choose one demo domain
2. seed it manually
3. create a small approved object set by hand or semi-manually
4. build retrieval and briefing on top of that set
5. then build and test extraction against the same domain

This avoids building a large pipeline before proving the product interaction.

---

## v0 Test Set

Before broader coding, build a small labeled extraction set for:

- 10 constraints
- 10 exceptions
- 10 procedures
- 10 facts
- 5 decisions
- 10 rejects

for the `service-dispatch` domain.

This becomes the first extraction evaluation harness.

Without a labeled set, extraction quality discussions will stay subjective.

---

## Immediate Next Steps

1. define extraction prompt contracts for each stage
2. define application-side confidence scoring rules
3. add authority assignment method to the source model
4. create the first labeled demo-domain extraction set
5. build the demo retrieval and briefing flow before full automation
