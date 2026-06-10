from app import run

in_corpus = [
    "What is the legal definition of negligence?",
    # ... 4 more from your PDFs
]

out_of_corpus = [
    "What is the latest treatment for long COVID?",
    # ... 4 more topics NOT in your PDFs
]

print("=== In-corpus (should stay local) ===")
for q in in_corpus:
    r = run(q)
    print(f"grade={r['grade']} iterations={r['iterations']} | {q[:50]}")

print("\n=== Out-of-corpus (should trigger web search) ===")
for q in out_of_corpus:
    r = run(q)
    print(f"grade={r['grade']} iterations={r['iterations']} | {q[:50]}")