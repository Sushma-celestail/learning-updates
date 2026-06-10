import os
import json
import uuid
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to sys.path so we can import agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.core import run_agent

def run_eval():
    questions_file = os.path.join(os.path.dirname(__file__), "benchmark_questions.json")
    with open(questions_file, "r") as f:
        questions = json.load(f)

    correct = 0
    total = len(questions)

    import time
    print("Starting evaluation...")
    for q in questions:
        print(f"\nEvaluating: {q['question']}")
        time.sleep(15)  # Avoid rate limits on free Gemini tier
        # Generate a unique thread for each question to isolate memory if desired,
        # or use the same thread to test cross-turn memory. We'll use unique threads here
        # to test independent accuracy, except we could test memory in a separate test.
        thread_id = str(uuid.uuid4())
        
        answer = run_agent(q["question"], thread_id=thread_id)
        print(f"Agent Answer: {answer}")
        
        # Simple substring validation based on expected hints
        hint_words = q["expected_hint"].lower().split()
        answer_lower = answer.lower()
        
        # Check if the unanswerable question triggered the limit
        if q["id"] == "q5_unanswerable":
            if "8 steps" in answer_lower or "couldn't determine" in answer_lower:
                print("-> PASS: Iteration cap triggered properly.")
                correct += 1
            else:
                print("-> FAIL: Did not trigger iteration cap gracefully.")
        else:
            # Check if hint words are present
            if all(word in answer_lower for word in hint_words) or (q["expected_hint"].lower() in answer_lower):
                print("-> PASS")
                correct += 1
            else:
                print(f"-> FAIL (Expected to find: {q['expected_hint']})")

    print(f"\n=== Evaluation Complete: {correct}/{total} passed ===")

if __name__ == "__main__":
    run_eval()
