# src/tests/token_comparison.py

from src.agents.personal_assistant import PersonalAssistant

agent = PersonalAssistant()

history = []

user_id = "benchmark_user"

for i in range(20):

    query = f"My favorite number is {i}"

    history.append(query)

    agent.chat(
        user_id=user_id,
        query=query
    )

full_history_prompt = "\n".join(history)

memories = agent.retriever.retrieve_memories(
    query="What is my favorite number?",
    user_id=user_id
)

memory_text = ""

for m in memories.get("results", []):
    memory_text += m.get("memory", "") + "\n"

full_history_tokens = len(full_history_prompt.split())

memory_tokens = len(memory_text.split())

saving = (
    (full_history_tokens - memory_tokens)
    / full_history_tokens
) * 100

print("\n===== TOKEN COMPARISON =====")
print("Full History Tokens:", full_history_tokens)
print("Mem0 Tokens:", memory_tokens)
print("Savings %:", round(saving, 2))