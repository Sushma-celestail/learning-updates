from langgraph.types import Command

def build_resume_command(decision,edited_args=None,): 
    return Command(
        resume={
            "decisions":[
                {
                    "decision": decision,
                    "edited_args": edited_args
                }
            ]
        }
    )