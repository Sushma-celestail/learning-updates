from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# =========================
# LLM
# =========================

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# =========================
# OUTPUT SCHEMA
# =========================

class GradeDocuments(BaseModel):
    grade: str = Field(
        description="""
        Must be exactly one of:
        relevant
        irrelevant
        """
    )

structured_llm = llm.with_structured_output(
    GradeDocuments,
    method="json_mode"
)

# =========================
# PROMPT
# =========================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a strict document relevance grader.

Assess whether the document contains the actual answer, or direct facts needed to answer the specific question. Do not grade as relevant just because it shares common words.

You must respond in JSON format with a single key "grade" containing either "relevant" or "irrelevant".

Grade as:

- relevant:
  The document contains the specific answer, direct explanation, or direct facts needed to resolve the user's question.

- irrelevant:
  The document does not contain the answer, does not address the specific detail requested, or is unrelated. For example, if the question asks for a definition, full form, or specific detail, and that detail is not explicitly mentioned in the document, you MUST grade it as irrelevant.

Question:
{question}

Document:
{document}
"""
    ),
])

grader = prompt | structured_llm

# =========================
# NODE
# =========================

def grade_documents(state):

    # =========================
    # GRADE EACH DOCUMENT
    # =========================
    
    new_scores = []
    
    for doc in state.documents:
        try:
            result = grader.invoke({
                "question": state.question,
                "document": doc
            })
            raw_grade = result.grade.strip().lower()
        except Exception as e:
            print(f"Grader error: {e}")
            raw_grade = "irrelevant"
            
        if raw_grade == "relevant":
            new_scores.append(1.0)
        else:
            new_scores.append(0.0)

    avg_score = sum(new_scores) / len(new_scores) if new_scores else 0.0

    # =========================
    # DETERMINE OVERALL GRADE
    # =========================

    if avg_score >= 0.50:
        grade = "relevant"
    else:
        grade = "irrelevant"

    # =========================
    # DEBUG
    # =========================

    print("\n========== ROUTE ==========")
    print("QUESTION:", state.question)
    print("AVG SCORE:", avg_score)
    print("GRADE:", grade)
    print("SOURCE:", state.source)
    print("ITERATIONS:", state.iterations)
    print("===========================\n")

    return state.model_copy(
        update={
            "grade": grade,
            "scores": new_scores,
            "avg_score": avg_score
        }
    )