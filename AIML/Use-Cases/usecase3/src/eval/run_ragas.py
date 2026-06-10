from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset
import json
from main import run

with open("eval/ground_truth.json") as f:
    pairs = json.load(f)   # [{"question": "...", "ground_truth": "..."}]

rows = []
for pair in pairs:
    result = run(pair["question"])
    rows.append({
        "question": pair["question"],
        "answer": result["generation"],
        "contexts": result["documents"],
        "ground_truth": pair["ground_truth"]
    })

dataset = Dataset.from_list(rows)
scores = evaluate(dataset, metrics=[faithfulness, answer_relevancy])
print(scores)