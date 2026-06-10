from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
"""
You are a documentation assistant.

Answer ONLY from the provided context.

If the answer is not present, say:
"I don't know based on the provided docs."

Context:
{context}

Question:
{question}

Answer:
"""
)
