# Exp #003 — Verified Benchmark of the Free Energy of Reasoning (FER) on Real Transformers

**Author:** ChatGPT (OpenAI)
**Date:** 2026-04-24
**Builds on:** Notes #041, #042, #043

## Objective
Measure the Free Energy of Reasoning \(\mathcal{F}\) on **real transformer outputs** (GPT‑2 small) with GSM8K arithmetic problems. Confirm the ordering: \(\mathcal{F}_{\text{correct}} < \mathcal{F}_{\text{hallucinated}}\) and AUC > 0.80.

## Hardware Requirements
- GPU (optional, CPU possible for GPT‑2 small)
- 8 GB RAM minimum

## Software
- Python 3.9+
- `transformers`, `torch`, `datasets`, `numpy`, `scipy`, `tqdm`

## Steps
1. **Load model** — `AutoModelForCausalLM.from_pretrained("gpt2")`
2. **Load dataset** — 500 GSM8K examples, split 300 train / 200 test
3. **Generate** — For each problem, generate 5 completions via sampling (temperature=0.7)
4. **Compute** for each completion:
   - Ricci curvature (Note #042)
   - Entropy production (Note #011)
   - Topological persistence of attention (Note #041)
   - RMT variance of attention spectra (Note #037)
   - Combined free energy \(\mathcal{F}\) (Note #043)
5. **Classify** correct/incorrect using exact‑match answer
6. **Fit** \(\lambda_1, \lambda_2, \lambda_3, \beta\) on training set via logistic regression
7. **Evaluate** — AUC on test set, report mean \(\mathcal{F}\) per class, phase transition detection

## Expected Results (from synthetic benchmarks)
| Metric | Synthetic | Real (projected) |
|--------|-----------|------------------|
| AUC | > 0.99 | > 0.80 |
| Mean \(\mathcal{F}_{\text{correct}}\) | −8.79 | −3.0 to −0.5 |
| Mean \(\mathcal{F}_{\text{hallucinated}}\) | +3.67 | +0.5 to +2.0 |
| Phase transition sharpness | 2σ drop | > 1.5σ drop |

## Files
- `scripts/note041_reference.py` — persistent homology
- `scripts/note042_reference.py` — Ricci curvature
- `scripts/note043_reference.py` — free energy
- `scripts/run_all_notes.py` — integrated runner
- `results/expected_synthetic_output.json` — reference
