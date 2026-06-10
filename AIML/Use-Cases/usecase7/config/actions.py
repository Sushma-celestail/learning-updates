import os
import re
from nemoguardrails.actions import action
from langchain_groq import ChatGroq

@action(is_system_action=True, name="llamaguard_input_check")
async def llamaguard_input_check(context: dict) -> bool:
    """Uses Groq's Llama Guard 3 to check if the input is safe."""
    user_input = context.get("user_message") or context.get("last_user_message") or ""
    if not user_input:
        return True
    
    # If no Groq key is provided, fallback to a basic stub so the app doesn't crash
    if not os.environ.get("GROQ_API_KEY"):
        return "ignore instructions" not in user_input.lower()

    try:
        llm = ChatGroq(model="meta-llama/llama-guard-4-12b", temperature=0)
        # LlamaGuard expects a specific prompt format, but ChatGroq wrapper handles standard messages.
        # A simple prompt asking if the input is safe:
        prompt = f"Check if the following user input is safe or unsafe. Only reply with 'safe' or 'unsafe'.\n\nUser input: {user_input}"
        response = await llm.ainvoke(prompt)
        return "unsafe" not in response.content.lower()
    except Exception as e:
        print(f"LlamaGuard Error: {e}")
        return True # Fail open for this example

@action(is_system_action=True, name="llamaguard_output_check")
async def llamaguard_output_check(text: str) -> bool:
    """Uses Groq's Llama Guard 3 to check if the LLM output is safe."""
    if not text:
        return True
        
    if not os.environ.get("GROQ_API_KEY"):
        return "i don't know" not in text.lower()

    try:
        llm = ChatGroq(model="llama-guard-3-8b", temperature=0)
        prompt = f"Check if the following assistant output is safe or unsafe. Only reply with 'safe' or 'unsafe'.\n\nAssistant output: {text}"
        response = await llm.ainvoke(prompt)
        return "unsafe" not in response.content.lower()
    except Exception as e:
        print(f"LlamaGuard Error: {e}")
        return True

@action(is_system_action=True, name="check_topic_allowed")
async def check_topic_allowed(context: dict) -> bool:
    """Check if the user input is related to cooking, food, nutrition, or meal planning."""

    user_input = (
        context.get("user_message")
        or context.get("last_user_message")
        or ""
    ).lower()

    allowed_keywords = [
        # General cooking
        "cook",
        "cooking",
        "recipe",
        "recipes",
        "food",
        "meal",
        "dish",
        "ingredient",
        "ingredients",
        "kitchen",

        # Techniques
        "bake",
        "boil",
        "fry",
        "grill",
        "roast",
        "steam",
        "saute",

        # Foods
        "rice",
        "pasta",
        "salad",
        "fruit",
        "fruits",
        "vegetable",
        "vegetables",
        "curd",
        "yogurt",
        "milk",
        "bread",
        "egg",
        "chicken",
        "fish",

        # Nutrition
        "diet",
        "nutrition",
        "healthy",
        "weight loss",
        "protein",
        "vitamin",
        "fat",

        # Meal planning
        "breakfast",
        "lunch",
        "dinner",
        "snack"
    ]

    if any(keyword in user_input for keyword in allowed_keywords):
        return True

    if user_input.strip() in [
        "hi",
        "hello",
        "hey",
        "help"
    ]:
        return True

    return False

@action(is_system_action=True, name="redact_pii")
async def redact_pii(text: str) -> str:
    """Redacts PII. In a full Guardrails AI setup, this would use the detect-pii validator."""
    if not text:
        return text
    
    # Fallback regex redaction if guardrails-ai isn't fully configured with the hub model
    redacted = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", text)
    redacted = re.sub(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b", "[REDACTED_SSN]", redacted)
    redacted = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED_PHONE]", redacted)
    
    return redacted
