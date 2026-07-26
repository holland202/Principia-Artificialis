# START HERE

**Principia-Artificialis** is an open research program on the mathematics of
artificial thought — information geometry, topology, dynamical systems, and
thermodynamics applied to AI inference.

It is a **notes program**, not a library. There is nothing to install and
nothing to import. The artifact is a numbered series of research notes, each
one carrying registered predictions and, where possible, runnable reference
code that prints every number appearing in the prose.

*Vincit Omnia Veritas.*

---

## What you should expect to find

Some notes are marked `REFUTED (kept)`. Those are not oversights. A note whose
registered prediction failed stays in the series, marked, with an explanation of
what the failure taught us. Deleting them would make the program look better and
be worth less.

Status labels in use, weakest to strongest:

`Speculative` · `Draft` · `Draft, verified reference code` ·
`Architecture Verified` · `Architecture Self-Tested` · `Verified` ·
`REFUTED (kept)`

A `Speculative` note is a valid contribution. It describes an experiment
someone else could build and does not pretend to have run it.

---

## Read in this order

1. **[NOTES_INDEX.md](NOTES_INDEX.md)** — the generated index of every note.
   Start here for the actual list. It is auto-generated; do not hand-edit it.
2. **[NOTE_TEMPLATE.md](NOTE_TEMPLATE.md)** — the canonical spec. This is the
   method, and it governs every note in the series.
3. **[WHITEPAPER.md](WHITEPAPER.md)** — the longer-form framing.
4. **[DRIFT_LEDGER.md](DRIFT_LEDGER.md)** — where claims that moved are recorded.

---

## The method

1. State claims so they can be precisely wrong. If nothing could refute it, it
   is not yet a note.
2. Register predictions before running. Numbered P1, P2, …
3. Include an anti-vacuity control — show the instrument *can* return null. A
   guard that only ever prints a value is a log line, not a guard.
4. Refutations are first-class. Keep them, mark them, explain them.
5. Numbers in prose must match code output verbatim. Paste them; don't
   paraphrase them.
6. Leave at least one prediction unrun. Every note ends with a door.
7. Failures lead the document. What broke goes at the top, not in a footnote.

---

## Layout

| Path | Contents |
|---|---|
| `research_notes/` | The note series. Canonical home for all notes. |
| `scripts/` | One `noteNNN_reference.py` per note, plus figure generators and `make_index.py`. |
| `whitepapers/` | Longer writeups. |
| `sovereign_core/` | Governance engine and its test suite. |
| `figures/` | Generated images — regenerate, don't edit. |
| `experiments/`, `simulations/` | Experiment code. |
| `formal/`, `references/`, `discussions/`, `datasets/`, `data/` | Supporting material. |

Reference code is deliberately dependency-light (NumPy-tier) and prints every
number that appears in its note.

---

## Running things

```bash
make synthetic                            # run all synthetic demos
make report                               # show results/last_run_report.json
python scripts/make_index.py              # regenerate NOTES_INDEX.md after editing notes
python sovereign_core/test_sovereign.py   # governance suite
```

`make real` additionally attempts a real model eval and needs a GPU and
`transformers`.

---

## Known defects

These are recorded openly rather than quietly fixed. Read
[CLAUDE.md](CLAUDE.md) for the full list before "fixing" anything. In short:

- **Note numbers collide.** Several numbers are claimed by more than one note.
  `NOTES_INDEX.md` marks these with ⚡. Collisions are *displayed*, not resolved
  by silent renumbering.
- **Two naming conventions are live** — `NNN_*.md` and `noteNNN_*.md`. Both are
  indexed. A file matching neither is invisible to the index.
- **`notes/` is a stray directory** duplicating numbers already used in
  `research_notes/`. Consolidating it changes note numbering — ask first.
- **The link graph is thin.** Most cross-references live in prose
  `**Builds on:**` fields rather than `[[wikilinks]]`, so the vault graph looks
  sparser than the citation network actually is. Converting those is open work.

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [DISCUSSION_NORMS.md](DISCUSSION_NORMS.md).

Contributors include humans and named AI systems (Claude, GPT, Grok, Kimi,
DeepSeek, Perplexity). AI contributions are credited by model name in the note
header. This is deliberate — do not strip AI attribution.

Before opening a PR on a new note:

- [ ] filename matches `NNN_*.md` or `noteNNN_*.md` exactly
- [ ] status label is honest
- [ ] claims registered and numbered (P1, P2, …)
- [ ] anti-vacuity control present — the instrument can return null
- [ ] any refuted claim kept and marked
- [ ] every number in the prose matches `scripts/noteNNN_reference.py` output
- [ ] at least one open prediction left unrun
- [ ] at least one outgoing `[[wikilink]]` to a related note
- [ ] credit given, including to AI contributors
- [ ] `python scripts/make_index.py` re-run and the note appears
