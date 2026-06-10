# Track:
# - Model used
# - Cost
# - Latency
# - Input Tokens
# - Output Tokens
# - Total Tokens


from __future__ import annotations

from dataclasses import dataclass

from corrective_rag.tracing import observe
#langfuse tracing decorator 
from graph.state import GraphState
#langgraph state object this contains 
# state.question, state.document, state.generation


@dataclass(frozen=True)
class LangfuseMetrics:
    model: str
    cost_usd: float
    latency_ms: float
    input_tokens: int
    output_tokens: int
    total_tokens: int


@observe(name="langfuse_metrics")
def capture_langfuse_metrics(state: GraphState, model: str, latency_ms: float) -> LangfuseMetrics:
    """Summarize LLM/tool metrics that Langfuse CallbackHandler records in hosted runs."""

    input_tokens = _estimate_tokens(
        state.question + " " + " ".join(item.document.text for item in state.documents)
    )
    output_tokens = _estimate_tokens(state.generation)
    return LangfuseMetrics(
        model=model,
        cost_usd=0.0,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )


def _estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))
