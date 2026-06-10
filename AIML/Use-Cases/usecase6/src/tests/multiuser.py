# src/tests/test_multiuser.py

from src.agents.personal_assistant import PersonalAssistant

agent = PersonalAssistant()

print("\n===== USER A: ALICE =====\n")

agent.chat(
    user_id="alice",
    query="My name is Alice and I live in London"
)

print("\n===== USER B: BOB =====\n")

agent.chat(
    user_id="bob",
    query="My name is Bob and I live in Paris"
)

print("\n===== TEST ALICE =====\n")

print(
    agent.chat(
        user_id="alice",
        query="What do you know about me?"
    )
)

print("\n===== TEST BOB =====\n")

print(
    agent.chat(
        user_id="bob",
        query="What do you know about me?"
    )
)