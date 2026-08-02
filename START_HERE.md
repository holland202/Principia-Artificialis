# Start Here

This is **Principia-Artificialis**: an open research program on the
mathematics of artificial thought — information geometry, topology,
dynamical systems, and thermodynamics applied to AI inference. It is a
**notes program**, not a library and not a product. The primary artifact is
a numbered series of research notes, each with registered predictions and,
where possible, runnable reference code.

Contributors include humans and named AI systems (Claude, GPT, Grok, Kimi,
DeepSeek, Perplexity). AI contributions are credited by model name in each
note's header, deliberately.

## The method, in one paragraph

Claims are stated so they can be precisely wrong. Predictions are
registered and numbered (P1, P2, …) **before** running anything. Every
instrument carries an anti-vacuity control — it must be shown able to
return null, because a gate you have never seen fail is not evidence that
anything passed. When a registered claim fails, it is kept, marked
refuted, and explained; several notes are marked REFUTED on purpose.
Numbers in prose are pasted from code output, never paraphrased. Every
note ends with at least one prediction left unrun.

The full spec is `NOTE_TEMPLATE.md`. The status labels
(`Speculative` → `Draft` → `Draft, verified reference code` → `Verified`,
plus `REFUTED (kept)`) are honest by construction — a `Speculative` label
is a valid contribution, not an apology.

## Where to start reading

- **`NOTES_INDEX.md`** — the auto-generated index of the whole series
  (currently 73 notes; regenerate with `python scripts/make_index.py`).
  ⚡ marks numbers claimed by more than one note — collisions are
  displayed, not hidden. ⚠ marks a registered claim that failed and was
  kept. Those marks are assets, not defects.
- **`research_notes/note044_circularity_test.md`** — the methodology note:
  why a benchmark that validates itself carries no evidence.
- **`research_notes/note052_verification_that_cannot_fail.md`** — the
  method applied to this estate's own code, refutations included.
- **`WHITEPAPER.md`** and `whitepapers/` — longer syntheses.

## How to run things

```bash
make synthetic     # run all synthetic demos (scripts/run_all_notes.py)
make report        # show results/last_run_report.json
python scripts/make_index.py            # regenerate NOTES_INDEX.md
python sovereign_core/test_sovereign.py # governance suite (expect 33/33)
```

Reference code convention: `scripts/noteNNN_reference.py`,
dependency-light (NumPy-tier), printing every number that appears in the
matching note.

## Honest state of the repository

Two filename conventions are live (`NNN_*.md` and `noteNNN_*.md`); the
index matches both. Some files in `research_notes/` match neither and are
invisible to the index — a known, recorded defect. The note graph is
currently hub-and-spoke (the index links everything; few notes link each
other laterally); adding real cross-links is the highest-value structural
improvement available. If you find a verification script here that cannot
fail, that is note052's subject — file an issue.

*Vincit Omnia Veritas.*
