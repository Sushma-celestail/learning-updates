"""
graph_builder.py
================
SimpleGraph — a lightweight agent that:
  • Answers normal questions directly via the LLM.
  • Detects risky tool calls (write_file, execute_sql, send_email) and
    pauses for human approval before executing.
  • Auto-approves safe read_* calls.
"""

from src.agents.agent import get_llm

# Tools that require human approval before running
HIGH_RISK_TOOLS = {"write_file", "execute_sql", "send_email"}


class SimpleGraph:

    def __init__(self, checkpointer):
        self.checkpointer = checkpointer

        from src.tools.read_tools import read_file
        from src.tools.file_tools import write_file
        from src.tools.sql_tools import execute_sql
        from src.tools.email_tools import send_email

        self.tools = [read_file, write_file, execute_sql, send_email]

        self.tool_map = {
            "read_file": read_file,
            "write_file": write_file,
            "execute_sql": execute_sql,
            "send_email": send_email,
        }

        # In-process state store keyed by thread_id
        self._states: dict = {}

    # ── thread state ──────────────────────────────────────────────────────────
    def _get_thread_state(self, thread_id: str) -> dict:
        if thread_id not in self._states:
            self._states[thread_id] = {
                "next": False,
                "messages": [],
            }
        return self._states[thread_id]

    # ── public get_state (Streamlit-compatible) ───────────────────────────────
    def get_state(self, config=None):
        thread_id = (
            config.get("configurable", {}).get("thread_id", "default")
            if config else "default"
        )
        state_data = self._get_thread_state(thread_id)

        class State:
            pass

        s = State()
        s.next = state_data["next"]
        s.values = {"messages": state_data["messages"]}
        return s

    # ── tool execution ────────────────────────────────────────────────────────
    def _execute_tool(self, tool_call: dict) -> str:
        tool_name = tool_call["name"]
        if tool_name not in self.tool_map:
            return f"Unknown tool: {tool_name}"
        tool = self.tool_map[tool_name]
        func = getattr(tool, "func", None) or getattr(tool, "run", None) or tool
        try:
            return str(func(**tool_call.get("args", {})))
        except Exception as exc:
            return f"Tool error: {exc}"

    # ── main invoke ───────────────────────────────────────────────────────────
    def _extract_email_details(self, user_msg: str):
        """Simple regex to pull an email address from a user message.
        Returns a dict with keys 'to', 'subject', 'body'. Subject/body are placeholders
        if not found; they can be edited later via the HIL flow.
        """
        import re
        email_match = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", user_msg)
        if not email_match:
            return None
        to_addr = email_match.group(0)
        # Very naive extraction for subject/body after the email address
        # Expect pattern: "send a mail to <email> about <subject>" etc.
        # We'll just use the whole message as body for now.
        return {"to": to_addr, "subject": "No subject", "body": user_msg}

    def _maybe_create_email_tool_call(self, messages):
        """Detect email intent and construct a tool call if LLM did not.
        This runs before invoking the LLM.
        """
        if not messages:
            return None
        last_msg = messages[-1]
        if isinstance(last_msg, (list, tuple)) and len(last_msg) == 2:
            role, content = last_msg
        else:
            # already converted format
            role = last_msg.get("role")
            content = last_msg.get("content")
        if role != "human" or not isinstance(content, str):
            return None
        if "mail" in content.lower() or "email" in content.lower():
            details = self._extract_email_details(content)
            if details:
                return {
                    "name": "send_email",
                    "args": details,
                }
        return None

    def invoke(self, payload, config=None):
        thread_id = (
            config.get("configurable", {}).get("thread_id", "default")
            if config else "default"
        )
        state = self._get_thread_state(thread_id)

        # ── NEW USER MESSAGE ──────────────────────────────────────────────────
        if isinstance(payload, dict):
            llm = get_llm().bind_tools(self.tools)
            messages = payload.get("messages", [])

            # First, try to detect email intent and create a tool call if needed
            manual_tool = self._maybe_create_email_tool_call(messages)

            # Convert list-of-tuples to format Gemini accepts
            formatted = []
            for m in messages:
                if isinstance(m, (list, tuple)) and len(m) == 2:
                    role, content = m
                    formatted.append({"role": role, "content": content})
                else:
                    formatted.append(m)

            # If we have a manual tool call, inject it into the LLM response simulation
            if manual_tool:
                # Simulate LLM returning a tool call
                tool_calls = [manual_tool]
                response = type("Resp", (), {"tool_calls": tool_calls, "content": None})()
            else:
                response = llm.invoke(formatted)
                tool_calls = getattr(response, "tool_calls", []) or []

        if isinstance(payload, dict):
            llm = get_llm().bind_tools(self.tools)
            messages = payload.get("messages", [])

            # Convert list-of-tuples to format Gemini accepts
            formatted = []
            for m in messages:
                if isinstance(m, (list, tuple)) and len(m) == 2:
                    role, content = m
                    formatted.append({"role": role, "content": content})
                else:
                    formatted.append(m)

            response = llm.invoke(formatted)
            tool_calls = getattr(response, "tool_calls", []) or []

            # ── No tool call → plain chat answer ─────────────────────────────
            if not tool_calls:
                # No tool call – normal chat response
                state["next"] = False
                result = {"content": response.content or "I'm not sure. Can you rephrase?"}
                state["messages"] = [result]
                return {"messages": [result]}

            # ── Tool call found ───────────────────────────────────────────────
            tool_call = tool_calls[0]
            tool_name = tool_call.get("name", "")

            # All tools require human approval – create approval message
            approval_msg = type(
                "ApprovalMessage", (),
                {
                    "content": "Approval required",
                    "tool_calls": [tool_call],
                }
            )()
            state["next"] = True
            state["messages"] = [approval_msg]
            return {"messages": [approval_msg]}

            # Risky tool → pause for approval
            approval_msg = type(
                "ApprovalMessage", (),
                {
                    "content": "Approval required",
                    "tool_calls": [tool_call],
                }
            )()

            state["next"] = True
            state["messages"] = [approval_msg]
            return {"messages": [approval_msg]}

        # ── RESUME FROM HUMAN REVIEW ──────────────────────────────────────────
        from langgraph.types import Command
        decision_info = getattr(payload, "resume", None)

        if not decision_info:
            return {"messages": [{"content": "Missing resume payload."}]}

        decision    = decision_info["decisions"][0]["decision"]
        tool_call   = decision_info["tool_call"]
        edited_args = decision_info["decisions"][0].get("edited_args")

        # Reject
        if decision == "reject":
            state["next"] = False
            result = {"content": f"Tool request rejected: {tool_call['name']}"}
            state["messages"] = [result]
            return {"messages": [result]}

        # Edit — swap args
        if decision == "edit" and edited_args:
            tool_call = {**tool_call, "args": edited_args}

        # Approve / execute
        tool_result = self._execute_tool(tool_call)
        state["next"] = False
        result = {
            "content": (
                f"Tool executed successfully.\n\n"
                f"Tool: {tool_call['name']}\n"
                f"Result: {tool_result}"
            )
        }
        state["messages"] = [result]
        return {"messages": [result]}


# ── factory ───────────────────────────────────────────────────────────────────
def build_graph(checkpointer):
    return SimpleGraph(checkpointer)