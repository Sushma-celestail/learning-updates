# Governance Policy

## Purpose

Use Case 3 is the core Corrective RAG product. Use Case 9 is the governance layer around it: observability, online evaluation, audit logging, dataset collection, offline RAGAS regression tests, and release gates.
Online evaluation does not create a second answer-regeneration loop. Corrective behavior remains in the Use Case 3 retrieval path: retrieve, grade, rewrite, web search, and generate.

## Release Gate

The project may be released only when all of these checks pass:

- Faithfulness >= 0.80
- Answer relevancy >= 0.80
- Context precision >= 0.75
- Hallucination failures <= 5 percent of evaluated items
- Local dataset validation confirms at least 30 examples
- SQLite audit logging is enabled
- CI JSON report is generated
- Regression comparison shows no metric drop greater than 10 percent

## Failure Review Process

When a metric drops below threshold or regresses by more than 10 percent:

1. Developer investigates failed rows in `reports/rag_eval_report.json`.
2. Developer checks Langfuse traces when available.
3. Developer reviews SQLite audit rows for affected prompts.
4. Developer updates retrieval, prompts, source data, or thresholds.
5. Lead reviewer approval is required before merging threshold changes.

## Audit Requirements

Each conversation must record:

- user id
- prompt
- response
- retrieved document ids
- model
- cost
- latency
- input tokens, output tokens, and total tokens
- hallucination score
- helpfulness score
- timestamp
- trace id
- correction status and reason

## Dataset Requirements

Approved conversations can be exported from SQLite into a Langfuse Dataset. The seed dataset must contain at least 30 items with input, expected answer, category, risk, and source metadata.

## NIST AI RMF Mapping

### GOVERN

Controls:

- Human review before production release
- Defined release thresholds
- Named accountability for threshold changes
- Audit logging for reviewability
- Dataset ownership and validation
- Secrets stored outside source control

These controls map to the NIST AI RMF GOVERN function because they establish policies, roles, accountability, oversight, and risk tolerances for the AI system.

### MEASURE

Controls:

- Online hallucination evaluation
- Online helpfulness evaluation
- RAGAS regression testing
- CI JSON metric reports
- Langfuse traces and evaluator scores
- Langfuse CallbackHandler metrics for cost, tokens, and latency
- Baseline comparison before release

These controls map to the NIST AI RMF MEASURE function because they assess, benchmark, monitor, and document AI risk and quality.
