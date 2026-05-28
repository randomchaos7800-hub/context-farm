# Context Farm Demo Scenarios v0

Status: draft  
Date: 2026-05-28

## Purpose

These demo scenarios are designed to make Context Farm legible quickly.

The goal is not to show a flashy chatbot. The goal is to show that concentrated operator knowledge can be captured, structured, and served back with enough grounding to be operationally useful.

## Demo Principles

Every demo should show:
- messy inputs
- operator knowledge capture
- structured output
- a grounded answer with provenance
- at least one exception or constraint

The product becomes much more credible when the answer includes:
- the rule
- the caveat
- the source

---

## Demo 1: Service Business Operations Lead

### Scenario

A small home-services company has one operations lead who knows:
- how emergency jobs are prioritized
- when same-day scheduling is allowed
- which clients get exceptions
- when deposits can be waived

### Inputs

- scheduling SOP PDF
- client policy page from website
- pasted notes from ops lead
- transcript of a short interview with the ops lead

### Domain seed

"This is a service dispatch domain. Relevant entities include clients, jobs, technicians, service windows, deposits, emergency requests, and approvals. Constraints include technician availability, emergency priority, minimum deposit rules, and after-hours scheduling policies. Some long-term clients and emergency situations are exceptions."

### Questions to ask in demo

- "Can we waive the deposit for this emergency call?"
- "Who needs approval for after-hours scheduling?"
- "What is different for long-term maintenance clients?"

### Good answer shape

- direct answer
- cites rule
- cites exception
- points to source or operator note

### Why it works

This demo makes the product immediately understandable to non-technical buyers.

---

## Demo 2: Finance/Admin Process Grounding

### Scenario

A finance/admin lead knows the real rules around transfers, approvals, floats, and what counts as an unusual charge.

### Inputs

- budget policy PDF
- account handling notes
- recurring bills list
- transcript from finance lead explaining exceptions

### Domain seed

"This is a small-business finance operations domain. Relevant entities include accounts, bills, transfers, recurring charges, payroll events, and approval thresholds. Constraints include minimum account floats, no-overdraft rules, unusual transaction thresholds, and exception handling for emergency expenses."

### Questions to ask in demo

- "Can we transfer $900 from ops to cover this bill?"
- "What triggers escalation on a new charge?"
- "What is the minimum float policy and when can it be overridden?"

### Good answer shape

- approved rule
- exception path
- authority ranking
- source provenance

### Why it works

This shows that the product is not only about document retrieval. It is about operational correctness.

---

## Demo 3: AI Fleet Grounding

### Scenario

A small internal AI fleet handles triage, drafting, research, and operations support. Without a shared memory layer, agents use inconsistent assumptions.

### Inputs

- internal runbook docs
- operator notes about escalation thresholds
- AI conversation exports
- short seed describing approval rules and role boundaries

### Domain seed

"This is an internal operations and automation domain. Relevant entities include tasks, queues, approvals, channels, agents, and escalation paths. Constraints include which agent can act independently, what requires human approval, which sources are authoritative, and what information may be sent externally."

### Questions to ask in demo

- "Can the drafting agent send this externally without review?"
- "Which agent owns incident triage after business hours?"
- "What requires human approval before action?"

### Good answer shape

- policy answer
- role boundary
- escalation path
- supporting source set

### Why it works

This demonstrates the second half of the vision: one operational memory layer serving multiple agents consistently.

---

## Suggested Demo Flow

### 1. Show the messy source material

Start with the problem:
- PDF
- notes
- transcript
- inconsistent fragments

### 2. Seed the domain

Show that the system is guided by how the operator describes the domain.

### 3. Show compiled output

Display:
- structured articles
- extracted knowledge objects
- linked procedures, constraints, and exceptions

### 4. Ask a question that normally requires the lead

Use a realistic edge-case question, not a generic one.

### 5. Show the grounded answer

Highlight:
- answer
- exception
- provenance
- why this would have interrupted the lead before

---

## Best First Demo To Lead With

Lead with Demo 1 or Demo 2.

Demo 1 is strongest for general small-business legibility.

Demo 2 is strongest if you want to emphasize operational correctness and constraints.

Demo 3 is strongest after the audience already understands the human-team value.

---

## Anti-Demo Rules

Do not lead with:
- abstract graph visuals
- ontology terminology
- generic "chat with your docs"
- broad enterprise search framing
- toy questions with obvious answers

The winning demo is specific, operational, and slightly painful.
