from langchain.agents.middleware import HumanInTheLoopMiddleware

hitl = HumanInTheLoopMiddleware(
    interrupt_on={
        "write_file": True,
        "execute_sql": True,
        "send_email": True,
    }
)