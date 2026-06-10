# Corrective RAG Chatbot with Agent Observability and Eval Pipeline

This project combines:

- **Use Case 3:** a local Corrective RAG chatbot that retrieves evidence, repairs weak retrieval, generates grounded answers, cites sources, and abstains when evidence is insufficient.
- **Use Case 9:** an observability and evaluation layer with optional Langfuse tracing, online hallucination/helpfulness evaluators, SQLite audit logs, Langfuse dataset seeding, approved-conversation export, pytest/RAGAS offline evaluation hooks, baseline comparison, and CI-friendly JSON metric gates.

The default path is fully local. Langfuse, Groq, and Tavily are optional.

## Quick Start

```powershell
cd outputs\usecase9_rag_observability
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Ask the chatbot:

```powershell
corrective-rag "How does this project map to NIST AI RMF MEASURE?"
```

Run the ChatGPT-style Streamlit UI:

```powershell
streamlit run app.py
```

The UI has two modes:

- **User View:** shows only the answer and sources.
- **Developer / Governance View:** shows an expandable panel with graph path, retrieved documents, hallucination score, helpfulness score, tokens, latency, cost, and audit status.

Build a JSON evaluation report:

```powershell
rag-eval-report --limit 10 --out reports\rag_eval_report.json
```

Validate the Langfuse seed dataset locally:

```powershell
seed-langfuse-dataset --dry-run
```

Run tests:

```powershell
pytest
```

## Optional Integrations

Install Langfuse and LangChain tracing support:

```powershell
pip install -e ".[observability]"
```

Set environment variables:

```powershell
$env:LANGFUSE_PUBLIC_KEY="..."
$env:LANGFUSE_SECRET_KEY="..."
$env:LANGFUSE_HOST="https://cloud.langfuse.com"
```

The code uses:

- `@observe` on the answer path through `corrective_rag.tracing.observe`.
- LangChain `CallbackHandler` discovery through `get_langchain_callback_handler()`.
- A `langfuse_metrics` span after generation to make model, cost, token, and latency capture explicit.
- Langfuse v4 `get_client()` flush and scoring helpers, including `score_current_span` / `score_current_trace` when available.
- A `groq-generation` span so Groq calls are visible even though the Groq client uses direct HTTP rather than LangChain.
- Online evaluator scores sent to the active Langfuse observation when context is available.

Langfuse healthcheck:

```powershell
pip install -e ".[observability]"
langfuse-healthcheck
corrective-rag "What is FastAPI?"
```

The healthcheck prints the Langfuse host, whether public/secret keys are present, whether the client loaded, and a `trace_id` or `trace_url`. It does not print secret values.

Install optional RAGAS support:

```powershell
pip install -e ".[ragas]"
pytest tests/test_ragas_offline.py
```

The default RAGAS test validates that local outputs are shaped correctly for RAGAS without requiring external model calls. A full RAGAS metric run is included and can be enabled in an environment configured with the needed RAGAS LLM and embedding providers:

```powershell
$env:RAGAS_RUN_FULL="1"
pytest tests/test_ragas_offline.py
```

Optional Groq generation:

```powershell
$env:GROQ_API_KEY="..."
$env:CORRECTIVE_RAG_LLM="groq"
$env:GROQ_MODEL="llama-3.1-8b-instant"
```

If Groq cannot be reached, the project falls back to the local grounded generator.

Optional Chroma retrieval:

```powershell
pip install -e ".[chroma]"
$env:CORRECTIVE_RAG_RETRIEVER="chroma"
```

Optional Tavily web search is used by the graph when retrieval is weak:

```powershell
$env:TAVILY_API_KEY="..."
```

## Architecture

1. The retriever loads `data/knowledge_base.jsonl` and performs local BM25-style search.
2. The graph node `retrieve` gathers candidate context.
3. The graph node `grade_documents` checks the best retrieval score.
4. If retrieval is weak, `rewrite_query` expands the query and `web_search` can add Tavily results.
5. The graph node `generate` answers from retrieved context and includes citations.
6. The `langfuse_metrics` span captures model, cost, token, and latency details. In hosted runs, Langfuse CallbackHandler captures these from LLM calls and tool invocations.
7. Online hallucination and helpfulness evaluators score the answer.
8. The run is saved to SQLite with trace id, user id, model, latency, cost, token counts, retrieval details, evaluator scores, and correction metadata.
9. Optional Langfuse tracing records node spans and evaluator scores.
10. CI and governance gates use evaluator failures to block or review releases.

## Key Files

- `src/graph/state.py`, `src/graph/nodes.py`, `src/graph/workflow.py`: Corrective RAG graph.
- `app.py`: ChatGPT-style Streamlit UI with user and governance views.
- `src/corrective_rag/pipeline.py`: Pipeline wrapper around the graph.
- `src/retriever/chroma.py`: Optional Chroma retriever with local fallback.
- `src/llm/groq.py`: Optional Groq model integration with local fallback.
- `src/tools/web_search.py`: Optional Tavily web search node.
- `src/corrective_rag/tracing.py`: Langfuse `@observe` wrapper and LangChain callback helper.
- `src/observability/langfuse_config.py`, `src/observability/callbacks.py`: Langfuse client and callback entry points.
- `src/observability/metrics.py`: Explicit model, cost, token, and latency capture.
- `src/corrective_rag/evaluators.py`: Online hallucination and helpfulness evaluators.
- `src/corrective_rag/audit.py`: SQLite audit log schema and writer.
- `src/datasets/exporter.py`: Approved conversation export from SQLite to Langfuse Dataset.
- `src/experiments/baseline.py`: Baseline comparison gate for regression checks.
- `src/corrective_rag/seed_langfuse.py`: Dataset seeding and dry-run validation.
- `src/corrective_rag/report.py`: CI-friendly JSON evaluation report.
- `tests/test_ragas_offline.py`: pytest RAGAS offline evaluation contract and optional full metric run.
- `data/eval_dataset.jsonl`: 32 local seed/eval items.
- `docs/GOVERNANCE_POLICY.md`: Release gate, failure review process, and NIST AI RMF mapping.

## Audit Log

The SQLite table `rag_audit_log` stores:

- trace id and timestamp
- user id
- user question and generated answer
- model, cost, and latency
- input, output, and total token counts
- citations
- retrieval documents, scores, matched terms, and sources
- evaluator names, scores, pass/fail status, and rationale
- correction status and correction reason

The compatibility view `audit_logs` exposes the pasted-spec fields: `user_id`, `prompt`, `response`, `retrieved_doc_ids`, `model`, `cost`, `latency`, `input_tokens`, `output_tokens`, `total_tokens`, `hallucination_score`, `helpfulness_score`, and `created_at`.

Inspect recent audit rows:

```powershell
corrective-rag --audit-limit 5
```

Export approved audit conversations to a Langfuse Dataset:

```powershell
export-approved-conversations --dry-run --limit 30
```

Compare the current report with the saved baseline:

```powershell
compare-rag-baseline --current reports\rag_eval_report.json --fail
```

## Governance Policy

### Purpose

The chatbot is intended for grounded project Q&A about Corrective RAG, observability, evaluation, audit logging, and AI governance. It should not answer outside the available project sources unless a user adds approved source material.

### Accountability

- Product owner: approves intended use and release criteria.
- ML or AI engineer: owns retrieval, generation, evaluator thresholds, and RAGAS configuration.
- Governance reviewer: approves policy, audit retention, threshold changes, and unresolved evaluator failures.
- Operator: monitors CI reports, Langfuse traces, and SQLite audit logs.

### Controls

- Source-grounding is mandatory for generated answers.
- Retrieval correction runs before generation when retrieval confidence is weak.
- Online hallucination and helpfulness evaluation runs on every answer.
- Failed online evaluation is recorded and handled by the release gate or review process.
- Every run is auditable through SQLite.
- Langfuse tracing is optional but recommended for shared environments.
- Dataset seeding requires at least 30 items and dry-run validation before external upload.
- Secrets must be stored in environment variables and never committed.

### Release Gate

A release is acceptable only when:

- unit tests pass
- the local dataset validates with at least 30 items
- the CI JSON report is generated and archived
- critical evaluator failures are reviewed or fixed
- threshold changes are documented and approved
- RAGAS results are reviewed when the optional RAGAS environment is enabled

## NIST AI RMF Mapping

### GOVERN

This project maps to the NIST AI RMF GOVERN function through:

- documented chatbot purpose and intended use
- named accountability roles
- source-grounding and abstention policy
- audit log retention expectations
- dataset ownership and validation rules
- evaluator threshold governance
- release approval criteria
- secrets handling policy

### MEASURE

This project maps to the NIST AI RMF MEASURE function through:

- online hallucination scoring
- online helpfulness scoring
- retrieval score monitoring
- correction counts in JSON reports
- row-level evaluator evidence
- pytest offline evaluation
- optional RAGAS faithfulness, answer relevancy, context precision, and context recall
- optional Langfuse traces and score history
- periodic dataset review

## CI

The included GitHub Actions workflow installs the local package, runs pytest, validates the Langfuse dataset seed in dry-run mode, generates `reports/rag_eval_report.json`, and uploads the report as an artifact.
It also fails CI if `faithfulness`, `answer_relevancy`, or `context_precision` drop below configured thresholds, and it compares the current run against the saved baseline with a maximum allowed drop of 10 percent.

## Langfuse Troubleshooting

If traces are not appearing in Langfuse Cloud:

```powershell
pip install -e ".[observability]"
langfuse-healthcheck
corrective-rag "How does this project use Langfuse tracing?"
```

Check that:

- `LANGFUSE_PUBLIC_KEY` is present.
- `LANGFUSE_SECRET_KEY` is present.
- `LANGFUSE_HOST` or `LANGFUSE_BASE_URL` points to `https://cloud.langfuse.com`.
- `langfuse-healthcheck` reports `client_available: true`.
- `langfuse-healthcheck` reports `flushed: true`.
- `langfuse-healthcheck` prints `trace_id` or `trace_url`.

The pipeline calls `flush_langfuse()` at the end of every answer after audit logging and evaluator scoring, so local runs should be pushed before the command exits.
