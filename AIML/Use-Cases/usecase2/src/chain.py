import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from src.prompts import prompt

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


def create_rag_chain(ensemble_retriever, rerank_func):

    def retrieve_and_generate(query, callbacks=None):

      # RETRIEVE
    
        docs = ensemble_retriever.invoke(query)

    # RERANK

        reranked_docs = rerank_func(query, docs)

    # DEBUG RETRIEVED DOCS

        print("\n===== RETRIEVED DOCS =====\n")

        for i, doc in enumerate(reranked_docs):

            print(f"\nDOC {i}\n")

            print(doc.page_content[:500])

     # BUILD CONTEXT
 
        context = "\n\n".join(
            [d.page_content for d in reranked_docs]
        )

    # CREATE PROMPT

        final_prompt = prompt.format(
            context=context,
            question=query
        )

        config = {}

        if callbacks:
            config["callbacks"] = callbacks
    # GENERATE ANSWER

        answer = llm.invoke(
            final_prompt,
            config=config
        ).content

        return answer, reranked_docs

    return retrieve_and_generate