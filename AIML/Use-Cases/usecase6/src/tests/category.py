from src.memory.memory_manager import Mem0Manager

memory = Mem0Manager()

user_id = "sushma"

all_memories = memory.get_all(user_id)

print("\n===== RAW RESPONSE =====\n")
print(all_memories)

print("\n===== ALL MEMORIES =====\n")

memory_results = all_memories.get("results", [])

for idx, item in enumerate(memory_results, start=1):
    print(f"\nMemory #{idx}")
    print(item)
    print("-" * 50)