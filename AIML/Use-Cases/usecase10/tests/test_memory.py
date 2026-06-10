from trading_floor.memory import MemoryStore


def test_second_session_retrieves_episodic_memories(tmp_path):
    path = tmp_path / "memories.json"
    first = MemoryStore(path)
    first.seed_demo_memories("demo_trader")
    first.add("demo_trader", "User wanted to invest in tech after AI demand increased.", "episodic")

    second = MemoryStore(path)
    memories = second.search("demo_trader", "tech AI invest", limit=5)

    assert len([m for m in memories if "User" in m]) >= 3
    assert any("tech" in m.lower() for m in memories)
