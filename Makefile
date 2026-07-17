.PHONY: help synthetic real real-test clean report

help:
@echo "Principia Artificialis — Makefile"
@echo ""
@echo "Targets:"
@echo "  synthetic   — Run all synthetic demos (Notes #041, #042, #043)"
@echo "  real        — Attempt real model evaluation (requires GPU/transformers)"
@echo "  report      — Show last saved report"
@echo "  clean       — Remove temporary files"

synthetic:
@echo "Running all synthetic demos..."
python scripts/run_all_notes.py

real: synthetic
@echo "Attempting real model evaluation..."
python -c "from scripts.run_all_notes import run_real_if_available; print(run_real_if_available())"

real-test: real
@echo "Real model test complete (if dependencies installed)."

report:
@cat results/last_run_report.json 2>/dev/null || echo "No report found. Run 'make synthetic' first."

clean:
rm -f results/last_run_report.json
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
@echo "Cleaned."
