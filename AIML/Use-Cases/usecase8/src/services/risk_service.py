HIGH_RISK_TOOLS = {
    "send_email",
    "execute_sql",
    "write_file",
}

def requires_approval(tool_name: str):

    return tool_name in HIGH_RISK_TOOLS