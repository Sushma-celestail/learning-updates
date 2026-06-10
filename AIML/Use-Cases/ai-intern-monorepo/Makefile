# AI Intern Monorepo — Makefile
# Usage:
#   make ingest UC=1        # ingest UC01 docs
#   make ingest UC=2        # ingest UC02 docs
#   make app    UC=1        # run UC01 Streamlit app
#   make eval   UC=2        # run UC02 Recall@5 evaluation
#   make test   UC=1        # run UC01 unit tests
#   make test   UC=2        # run UC02 unit tests
#   make test-all           # run all unit tests

UC ?= 1

.PHONY: ingest app eval test test-all clean help

ingest:
	@echo "▶ Ingesting UC0$(UC) …"
	python uc0$(UC)_*/ingest.py

app:
	@echo "▶ Starting UC0$(UC) Streamlit app …"
	streamlit run uc0$(UC)_*/app.py

eval:
	@echo "▶ Running UC0$(UC) evaluation …"
	python uc0$(UC)_*/eval/eval_recall.py

test:
	@echo "▶ Running UC0$(UC) unit tests …"
	pytest uc0$(UC)_*/tests/ -m "not integration" -v

test-all:
	@echo "▶ Running all unit tests …"
	pytest -m "not integration" -v

clean:
	@echo "▶ Removing __pycache__ and .pytest_cache …"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

help:
	@echo ""
	@echo "  make ingest UC=1    — ingest FastAPI docs into ChromaDB (UC01)"
	@echo "  make ingest UC=2    — ingest PDFs + HTML into ChromaDB (UC02)"
	@echo "  make app    UC=1    — launch Docs Buddy Streamlit UI"
	@echo "  make eval   UC=2    — run Recall@5 evaluation report"
	@echo "  make test   UC=1    — run UC01 unit tests"
	@echo "  make test   UC=2    — run UC02 unit tests"
	@echo "  make test-all       — run all unit tests"
	@echo ""
