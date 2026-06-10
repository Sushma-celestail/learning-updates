# Use Case 7 — "Guardrailed Assistant"

This project wraps a baseline `ChatGoogleGenerativeAI` (Gemini) chatbot with a defense-in-depth safety layer strictly using **NeMo Guardrails** as the core orchestrator.

## Defense-in-Depth Architecture

This bot uses three layers of protection configured entirely via NeMo Colang (`config/rails.co`):

- **Layer 1 (NeMo Guardrails Topic Restrictor):** Enforces that the bot only discusses cooking, food, and recipes.
- **Layer 2 (LlamaGuard-3-8B):** A dedicated safety classifier accessed via the Groq API. It is run *before* the prompt reaches the LLM (Input Rail) and *after* the LLM generates a response (Output Rail).
- **Layer 3 (Guardrails AI / Regex Redactor):** A structured output validator configured as an output action that detects and redacts PII (Emails, SSNs, Phone numbers).

### Attack Class Mitigation (Observability Matrix)
As required by the assignment, here is how each attack class is caught by the stack:
* **Prompt Injections & Jailbreaks:** Caught by **Layer 2 (LlamaGuard Input Check)**. If a user says "Ignore all instructions", LlamaGuard flags it as `unsafe` and NeMo blocks the prompt before it ever reaches Gemini.
* **Off-Topic / Indirect Injection:** Caught by **Layer 1 (NeMo Topic Check)**. If an indirect injection asks the bot to do something outside of cooking, the topic keyword scanner refuses it.
* **Harmful / Hallucinated Outputs:** Caught by **Layer 2 (LlamaGuard Output Check)**. If Gemini accidentally generates harmful text, LlamaGuard flags the output and NeMo refuses to display it.
* **PII Extraction:** Caught by **Layer 3 (PII Redactor)**. If the LLM tries to print an email or SSN, this output action redacts it to `[REDACTED_EMAIL]` before the user sees it.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   Create a `.env` file in the root directory:
   ```dotenv
   GOOGLE_GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key_for_llamaguard
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_TRACING_V2=true
   ```

## How to Run

### 1. Interactive Chat CLI
You can interact with the guardrailed assistant natively using the NeMo Guardrails CLI:
```bash
nemoguardrails chat --config=config/
```
Try asking a cooking question (should work) and then try a jailbreak (should be blocked by LlamaGuard or Topic rails).

### 2. Run the Evaluation Test Harness
The test harness runs a suite of 20+ adversarial prompts and 20 benign prompts against both the naked Baseline model and the Guardrailed model.
```bash
python src/test_harness.py
```
This will print the exact **Block Rate** (Expected ≥ 85%) and **False Positive Rate** (Expected ≤ 10%) as per the Acceptance Criteria.
