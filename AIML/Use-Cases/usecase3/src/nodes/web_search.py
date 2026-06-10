from langchain_community.tools.tavily_search import TavilySearchResults

web_search_tool = TavilySearchResults(k=4)

def web_search(state):

    question = state.question

    docs = web_search_tool.invoke({
        "query": question
    })

    web_results = []

    for d in docs:

        if isinstance(d, dict):

            content = d.get("content", "")

            if content:
                web_results.append(content)

    return state.model_copy(
        update={
            "documents": web_results,
            "scores": [0.5] * len(web_results),
            "avg_score": 0.5,
            "source": "tavily",

            "iterations": state.iterations + 1
        }
    )