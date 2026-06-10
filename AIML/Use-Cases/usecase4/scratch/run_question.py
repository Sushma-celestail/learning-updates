import os
import sys
import argparse

# Ensure project root is on sys.path
PROJECT_ROOT = r"C:/Users/sushma.s/Desktop/Use-Cases/usecase4"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Force DuckDuckGo backend for searches
os.environ["USE_TAVILY"] = "false"

from agent.core import run_agent


def main():
    parser = argparse.ArgumentParser(description="Answer a question using the Antigravity agent with proper output format.")
    parser.add_argument('question', nargs='*', help='The question to answer (provide as a single string or multiple words)')
    args = parser.parse_args()
    if not args.question:
        print('Please provide a question.')
        return
    question = ' '.join(args.question)
    # Use a dummy thread ID; the UI normally provides one, but any string works.
    thread_id = 'cli_thread'
    answer = run_agent(question, thread_id, callbacks=None)
    print(answer)

if __name__ == '__main__':
    main()
