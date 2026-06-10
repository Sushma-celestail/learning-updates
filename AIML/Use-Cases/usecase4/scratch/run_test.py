import os, sys
# Ensure project root is on sys.path
project_root = r"C:/Users/sushma.s/Desktop/Use-Cases/usecase4"
if project_root not in sys.path:
    sys.path.append(project_root)
# Force DuckDuckGo backend
os.environ["USE_TAVILY"] = "false"

from agent.core import run_agent

answer = run_agent('What is the population of the country whose capital city hosted the 2024 Summer Olympics, divided by 1 million?', 'test_thread', None)
print('RESULT:', answer)
