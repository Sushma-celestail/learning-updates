from langgraph.prebuilt import Middleware

class RiskPolicy(Middleware):
    """Simple risk‑policy middleware.

    Auto‑approves any tool whose name starts with ``read_`` and requires
    human approval for dangerous tools (write_file, execute_sql, send_email).
    The middleware works with ``HumanInTheLoopMiddleware`` – it only decides
    whether to pause for approval.
    """

    def __init__(self):
        super().__init__()
        self.dangerous = {"write_file", "execute_sql", "send_email"}

    def should_interrupt(self, tool_name: str) -> bool:
        """Return ``True`` if the tool requires human interruption.

        ``read_*`` tools are auto‑approved, all others are considered risky.
        """
        if tool_name.startswith("read_"):
            return False
        return tool_name in self.dangerous

    async def on_tool_start(self, tool_name: str, *args, **kwargs):
        # LangGraph will call this before executing a tool.
        if self.should_interrupt(tool_name):
            # Raise an interrupt payload that HumanInTheLoopMiddleware will handle.
            return {"interrupt": True, "tool_name": tool_name}
        return {"interrupt": False}
