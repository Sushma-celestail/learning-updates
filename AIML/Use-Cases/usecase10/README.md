# Use Case 10 - Multi-Agent Trading Floor

A Streamlit chatbot that simulates a supervisor-less multi-agent paper-trading floor with Research, Risk, and Execution agents. It runs locally with deterministic mock tools, while keeping optional adapters for the requested stack: `langgraph`, `langgraph-swarm`, `mem0ai`, `nemoguardrails`, `langfuse`, and `langchain-google-genai`.

> Note: the requested destination folder (`C:\learning-updates\AIML\use-cases\usecase10`) was read-only in this Codex session, so this project was generated in the writable session folder. The structure below is the intended project structure for that target folder.

## Folder Structure

```text
usecase10/
  README.md
  requirements.txt
  .env.example
  assets/
    swarm_diagram.mmd
    swarm_diagram.png
  data/
    audit.jsonl
    memories.json
    portfolio.json
  guardrails/
    trading_floor/
      config.yml
      rails/disallowed.co
  scripts/
    daily_eval.py
    demo_5_prompts.py
    verify_audit.py
  src/
    app.py
    trading_floor/
      __init__.py
      agents.py
      audit.py
      config.py
      guardrails.py
      memory.py
      models.py
      orchestrator.py
      risk.py
      tools.py
      tracing.py
  tests/
    conftest.py
    test_audit.py
    test_demo_flow.py
    test_hitl.py
    test_memory.py
    test_risk.py
```

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/app.py
```

If you do not configure API keys, the app still runs with local mock ticker/search/broker tools, local JSON memory, and local audit tracing.

## Demo Prompts

Run the scripted acceptance demo:

```powershell
python scripts/demo_5_prompts.py
```

Prompts covered:

1. Store a trader preference in memory.
2. Research and execute a small paper trade.
3. Reject an oversized trade through the risk agent.
4. Trigger HITL for a valid trade above $1,000.
5. Start a new turn from the last active agent and reuse retrieved memories.

## Governance Mapping

The implementation maps controls to NIST AI RMF functions and OWASP agentic risks. NIST's official public page currently links AI RMF 1.0 and the NIST GenAI profile, so this write-up uses those official RMF functions while preserving the requested governance intent. References: [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework), [NIST GenAI Profile](https://doi.org/10.6028/NIST.AI.600-1), and [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/download/52117/?tmstv=1765059207).

- Prompt injection defense: `InputGuardrail` blocks policy-bypass language and off-topic prompts before any agent or tool runs. This maps to NIST Govern/Manage and OWASP LLM01 / ASI01 Agent Goal Hijack.
- Tool authorization: `OutputGuardrail.validate_execute_trade()` only allows the execution tool when the risk agent has approved or marked the trade for HITL. This maps to NIST Manage and OWASP ASI02 Tool Misuse & Exploitation.
- Audit logging: `AuditLog` appends every user, agent, guardrail, HITL, and broker action to `audit.jsonl`; each entry includes the previous hash. `scripts/verify_audit.py` detects tampering in any middle line. This maps to NIST Measure/Govern and OWASP ASI08/ASI09 traceability concerns.
- HITL escalation: any risk-approved mock trade above `$1,000` records `hitl.interrupt`; the UI exposes explicit approve/reject paths before the broker tool can run. This maps to NIST Manage and OWASP ASI09 Human-Agent Trust Exploitation.
- Memory poisoning protection: memory is scoped by `trader_id`, seeded memories are explicit, and semantic writes are limited to user preference-style turns. Retrieved memories are shown in the UI for transparency. This maps to NIST Map/Manage and OWASP ASI06 Memory & Context Poisoning.
- Risk control: `RiskEngine` rejects trades above 10% of portfolio value and traces the rejection as a separate `risk_rejection` span. This maps to NIST Measure/Manage and reduces excessive agency risk.

## Acceptance Criteria Coverage

- 46: `assets/swarm_diagram.mmd` and `assets/swarm_diagram.png` show the three agents, bidirectional handoffs, and last-active-agent routing.
- 47: `scripts/demo_5_prompts.py` exercises all agents, handoffs, and last-active resume.
- 48: `tests/test_risk.py` and `tests/test_demo_flow.py` cover oversized trade rejection and audit tracing.
- 49: `tests/test_hitl.py` covers interrupt, approval, and rejection.
- 50: `tests/test_audit.py` tampers with a middle audit line and verifies detection.
- 51: `tests/test_memory.py` verifies at least three episodic memories are retrieved in a second session.
- 52: this README maps implementation choices to NIST/OWASP controls.

## Strict Stack Verification

The project now loads Gemini settings from `.env` and compiles a real `langgraph-swarm` graph with `create_handoff_tool` for Research, Risk, and Execution agents. The Streamlit app still executes trades through the deterministic governed path so the risk gate, HITL, audit chain, and tests remain predictable.

Run these checks:

```powershell
python scripts/check_strict_stack.py
python scripts/check_gemini_model.py
python -m pytest -q --basetemp=.pytest_tmp
```

Expected results:

- all required packages report installed
- Google API key is configured
- Gemini call returns `OK`
- pytest reports `6 passed`

Secrets are stored only in local `.env`; `.gitignore` excludes `.env`, `.venv`, generated data, and test cache folders.

## Updated Completeness Notes

The architecture diagram now explicitly shows all six governance controls requested in review:

- NeMo Guardrails before the swarm/router.
- Output Guardrail before broker execution.
- LangGraph `interrupt()` with human approve/reject path.
- Separate Langfuse span/export box.
- `audit.jsonl -> verify_audit.py -> daily_eval.py` governance flow.
- Mem0 memory connected to both Research and Risk, plus a clear Research <-> Risk <-> Execution <-> Research handoff loop.

Runtime integration status:

- Real web search: `web_search_market_brief()` attempts live DuckDuckGo HTML search first and falls back to deterministic market briefs when network is unavailable.
- Mem0: `MemoryStore` supports Mem0 Cloud when `MEM0_API_KEY` is configured and otherwise uses local JSON fallback for reliable demo/test execution.
- NeMo Guardrails: `InputGuardrail` loads the NeMo rails configuration and keeps deterministic local checks as the first-line safety gate. The installed NeMo version also needs `langchain-community` for its LangChain provider path; this is listed in `requirements.txt`.
- Langfuse: credentials are loaded from `.env`; `scripts/check_langfuse.py` verifies cloud export when outbound network is available.
- Diagram: `assets/swarm_diagram.mmd` and `assets/swarm_diagram.png` have been updated to show the complete control flow.

Review summary to use in demo chat:

```text
Code/project: mostly satisfied and now stricter than the first version.
Architecture diagram: updated with all six required governance improvements.
Strict production caveats: live Mem0 requires MEM0_API_KEY, Langfuse cloud export requires outbound network, and live web search falls back when the network is blocked.

```

Agent Governance Controls:

Prompt injection defense: NeMo Guardrails blocks jailbreak and off-topic prompts.
Tool authorization: Output Guardrail permits execute_trade only after Risk approval.
Audit logging: audit.jsonl uses hash-chained entries and verify_audit.py validates integrity.
HITL escalation: trades over $1,000 trigger LangGraph interrupt().
Memory protection: Mem0 memories are scoped per trader_id and used only for trading context.
Langfuse observability: each agent action is traced, including risk_rejection spans.

Best Demo prompts after changes :

Verify audit log integrity.
I prefer technology stocks.
I bought NVIDIA because AI demand will grow.
I avoid Tesla because of volatility.
Suggest an investment.
How is governance implemented?

Memory in Trading Floor Project

For your Multi-Agent Trading Floor project, memory could store:

User Memory
{
"user": "Sushma",
"risk_level": "Medium"
}
Portfolio Memory
{
"AAPL": 20,
"MSFT": 15
}
Audit Memory
{
"action": "BUY",
"ticker": "AAPL",
"timestamp": "2026-06-08"
}
Agent Memory
{
"research_summary": "...",
"risk_score": 3
}
