from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import GOOGLE_API_KEY, MODEL_NAME
from src.schemas.review_schema import ReviewDecision
from src.services.audit_logger import log_tool_execution


def get_llm():
    """Instantiate the real Gemini LLM.
    The model name and API key are read from environment settings.
    """
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=GOOGLE_API_KEY,
        temperature=0.0,
    )

# ----- placeholder executor (kept for future extensions) -----
def execute(tool_call):
    tool_name = tool_call["name"]
    # mock execution – real tools are invoked directly in the graph
    result = {
        "status": "success",
        "tool": tool_name,
        "message": f"Executed {tool_name}"
    }
    log_tool_execution(tool_name, result)
    return result

class DummyChatModel:
    def _invoke(self, messages, **kwargs):
        # Return the last user message as the AI response (simple echo)
        user_msg = ""
        for message in reversed(messages):
            if message.type == "human":
                user_msg = message.content
                break
        return AIMessage(content=user_msg or "I’m here to help.")

def apply_fix(tool_call, reason: str):
    if "email" in tool_call["name"]:
        tool_call["args"]["body"] = "Fixed by reviewer: " + (reason or "")
    return tool_call

def handle_review(decision: ReviewDecision, tool_call):
    if decision.decision == "approve":
        return execute(tool_call)
    elif decision.decision == "reject":
        return {
            "status": "rejected",
            "tool": tool_call["name"],
            "reason": decision.reason,
            "executed": False,
        }
    elif decision.decision == "edit":
        tool_call["args"].update(decision.edited_args or {})
        return execute(tool_call)