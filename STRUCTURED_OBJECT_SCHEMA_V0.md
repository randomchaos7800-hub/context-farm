# Structured Object Schema v0

Status: draft  
Date: 2026-05-28

## Purpose

This document defines the first concrete storage contract for Context Farm's structured knowledge layer.

It is the implementation bridge between:
- the product spec
- the architecture spec
- the MVP roadmap

This schema is intentionally small and operational. It is designed to be sufficient for the MVP, not theoretically complete.

---

## Design Principles

1. every important object must carry provenance
2. high-impact knowledge must be reviewable
3. constraints and exceptions must be first-class
4. relationships should be typed but simple
5. SQLite should remain the system of record for the structured layer in v0

---

## Object Types

The structured layer stores these primary object types:

- `Fact`
- `Procedure`
- `Constraint`
- `Exception`
- `Decision`
- `Entity`
- `Source`

These are the only required types for v0.

---

## Status Values

Structured knowledge objects use one of these statuses:

- `draft`
- `approved`
- `disputed`
- `stale`
- `superseded`

Default:
- all extracted objects begin as `draft`
- high-impact objects should be promoted to `approved` by review

---

## Freshness Values

Objects may carry a freshness state:

- `current`
- `needs_review`
- `stale`
- `unknown`

This is separate from status.

Example:
- a constraint can be `approved` but `needs_review`

---

## Core Object Shape

Every structured knowledge object should be representable as:

```json
{
  "id": "constraint.dispatch.after-hours-approval",
  "object_type": "Constraint",
  "domain_slug": "service-dispatch",
  "title": "After-hours approval required",
  "canonical_statement": "After-hours scheduling requires operations lead approval unless the request is classified as emergency priority.",
  "body_json": {
    "applies_to": ["procedure.dispatch.after-hours-scheduling"],
    "thresholds": ["after_hours=true"],
    "approver_roles": ["ops-lead"]
  },
  "status": "approved",
  "freshness_state": "current",
  "confidence_score": 0.93,
  "authority_class": "internal-sop",
  "review_priority": "high",
  "source_count": 2,
  "created_at": "2026-05-28T12:00:00Z",
  "updated_at": "2026-05-28T12:05:00Z",
  "reviewed_at": "2026-05-28T12:20:00Z"
}
```

---

## Required Fields

All structured objects must have:

- `id`
- `object_type`
- `domain_slug`
- `title`
- `canonical_statement`
- `status`
- `freshness_state`
- `confidence_score`
- `authority_class`
- `created_at`
- `updated_at`

Optional but strongly preferred:

- `body_json`
- `reviewed_at`
- `review_priority`
- `source_count`

---

## Object ID Format

Use deterministic slugs where possible:

`{object_type-lower}.{domain_slug}.{object_slug}`

Examples:
- `constraint.finance.ops-float-minimum`
- `procedure.service-dispatch.deposit-waiver-flow`
- `exception.service-dispatch.vip-client-waiver`
- `decision.finance.emergency-transfer-approval`

This keeps IDs readable and portable.

---

## Object-Specific Expectations

## Fact

Use for discrete domain truths that do not clearly belong in a more specific type.

Examples:
- "Recurring payroll runs on the 15th and last day of the month."
- "Unrecognized charges over $200 must be flagged."

Expected `body_json` fields:
- `subject`
- `predicate`
- `object`
- `qualifiers`

## Procedure

Use for multi-step operational flows.

Examples:
- intake process
- transfer approval flow
- emergency scheduling flow

Expected `body_json` fields:
- `steps`
- `inputs`
- `outputs`
- `roles`
- `handoffs`

## Constraint

Use for hard rules, thresholds, minimums, required approvals, or forbidden actions.

Examples:
- minimum float rules
- no-overdraft rules
- approval thresholds

Expected `body_json` fields:
- `applies_to`
- `thresholds`
- `conditions`
- `enforcement`

## Exception

Use for cases that override or narrow a rule.

Examples:
- VIP client exception
- emergency override
- manual approval bypass

Expected `body_json` fields:
- `exception_to`
- `conditions`
- `approver_roles`
- `scope`

## Decision

Use for recorded domain decisions that affect future behavior.

Examples:
- choose one billing workflow over another
- set a new escalation threshold

Expected `body_json` fields:
- `decision`
- `rationale`
- `effective_date`
- `decision_maker`

## Entity

Use for durable domain objects referenced by other knowledge.

Examples:
- account
- client
- technician
- approval role

Expected `body_json` fields:
- `entity_type`
- `attributes`
- `aliases`

## Source

Sources are stored separately in the relational schema, but should still be thought of as first-class objects in the domain model.

Examples:
- PDF policy
- URL
- text note
- transcript
- operator interview

---

## Link Types

The MVP only needs these typed relationships:

- `applies_to`
- `depends_on`
- `references`
- `contradicts`
- `supersedes`
- `exception_to`
- `approved_by`

This set is enough for useful traversal and governance.

---

## Authority Classes

Each domain should define a simple authority hierarchy.

Suggested default classes:

- `signed-policy`
- `official-sop`
- `manager-note`
- `meeting-transcript`
- `operator-interview`
- `informal-note`
- `unknown`

These should remain configurable per domain.

---

## Review Priority

Suggested values:

- `high`
- `medium`
- `low`

Default rules for v0:

- `Constraint`, `Exception`, and `Decision` default to `high`
- contradictions default to `high`
- low-confidence `Fact` objects default to `medium`
- most `Entity` objects default to `low`

---

## Source Linkage

Every structured object should be linkable to one or more source records.

The linkage must support:

- one object from many sources
- many objects from one source
- evidence snippets per source where possible

This will be handled relationally in the SQLite schema rather than duplicating full source metadata in every object.

---

## Example Objects

## Constraint example

```json
{
  "id": "constraint.finance.ops-float-minimum",
  "object_type": "Constraint",
  "domain_slug": "finance",
  "title": "OPS float minimum",
  "canonical_statement": "OPS account must remain above $500 unless emergency transfer override is approved.",
  "body_json": {
    "applies_to": ["entity.account.ops"],
    "thresholds": ["minimum_balance_usd=500"],
    "conditions": ["normal_operations=true"]
  },
  "status": "approved",
  "freshness_state": "current",
  "confidence_score": 0.98,
  "authority_class": "signed-policy",
  "review_priority": "high",
  "source_count": 2
}
```

## Exception example

```json
{
  "id": "exception.finance.emergency-transfer-override",
  "object_type": "Exception",
  "domain_slug": "finance",
  "title": "Emergency transfer override",
  "canonical_statement": "OPS minimum float may be temporarily breached if an emergency expense is approved by the finance lead.",
  "body_json": {
    "exception_to": ["constraint.finance.ops-float-minimum"],
    "conditions": ["expense_class=emergency"],
    "approver_roles": ["finance-lead"]
  },
  "status": "draft",
  "freshness_state": "current",
  "confidence_score": 0.88,
  "authority_class": "manager-note",
  "review_priority": "high",
  "source_count": 1
}
```

---

## Implementation Notes

For v0:

- `body_json` should remain flexible JSON stored as text in SQLite
- top-level fields should be relational and queryable
- extraction can improve over time without forcing a full schema rewrite

This gives us enough structure for operational retrieval without overcommitting too early.
