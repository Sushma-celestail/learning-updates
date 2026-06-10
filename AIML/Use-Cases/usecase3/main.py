import os
from dotenv import load_dotenv

load_dotenv()

from src.graph.builder import build_graph

# Expose a simple run function for eval scripts
_graph = None

def run(question: str):
    global _graph
    if _graph is None:
        _graph = build_graph()
    res = _graph.invoke({"question": question})
    # Support both dictionary and pydantic object access
    if hasattr(res, "model_dump"):
        return res.model_dump()
    return res

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        res = run(q)
        print("Question:", res.get("question"))
        print("Grade:", res.get("grade"))
        print("Avg Score:", res.get("avg_score"))
        print("Iterations:", res.get("iterations"))
        print("Source:", res.get("source"))
        print("Answer:", res.get("generation"))
    else:
        print("Please provide a question as argument, e.g. python main.py 'your question'")
