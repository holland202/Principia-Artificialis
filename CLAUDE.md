# CLAUDE.md — Principia-Artificialis

Persistent context for Claude Code and any other agent working in this repo.
Read this before touching anything.

**Motto:** Vincit Omnia Veritas. **Prime directive:** trust the files, not the
summary of the files — including not trusting this one. Verify before you act.

---

## What this repo is

An open research program on the mathematics of artificial thought: information
geometry, topology, dynamical systems, and thermodynamics applied to AI
inference. It is a **notes program**, not a library. The primary artifact is a
numbered series of research notes, each with registered predictions and, where
possible, runnable reference code.

Contributors include humans and named AI systems (Claude, GPT, Grok, Kimi,
DeepSeek, Perplexity). AI contributions are credited by model name in the note
header. This is deliberate — do not strip AI attribution.

**What it is not:** a product, a framework, or a proof. Notes carry honest
status labels and several are marked REFUTED and kept on purpose.

---

## The method (binding — this governs every edit)

From `NOTE_TEMPLATE.md`, which is the canonical spec:

1. **State claims so they can be precisely wrong.** If nothing could refute it,
   it is not yet a note.
2. **Register predictions before running.** Numbered P1, P2, …
3. **Include an anti-vacuity control.** Show the instrument *can* return null.
   A guard that only ever prints a value is a log line, not a guard — it needs
   an expected value beside it.
4. **Refutations are first-class.** If a registered claim failed, KEEP IT, mark
   it refuted, and write what the failure taught you. Never quietly delete a
   failed prediction.
5. **Numbers in prose must match code output verbatim.** Paste them; don't
   paraphrase them.
6. **Leave at least one prediction unrun.** Every note ends with a door.
7. **Failures lead the document.** Put what broke at the top, not in a footnote.

Status labels in use: `Speculative`, `Draft`, `Draft, verified reference code`,
`Architecture Verified`, `Architecture Self-Tested`, `Verified`,
`REFUTED (kept)`.

---

## Directory map

| Path | Contents | Notes |
|---|---|---|
| `research_notes/` | 78 `.md` files — the note series | **Canonical home for all notes** |
| `notes/` | 2 stray `.md` files | Colliding duplicates — see Known defects |
| `scripts/` | 29 files: `noteNNN_reference.py`, figure generators, `make_index.py` | One reference script per note |
| `whitepapers/` | 8 longer writeups | |
| `sovereign_core/` | Governance engine + `test_sovereign.py` | 33/33 deterministic on device |
| `experiments/`, `simulations/` | Experiment code | |
| `figures/` | 49 generated images | Regenerate via `scripts/generate_*.py` |
| `results/` | `last_run_report.json` | Written by `make synthetic` |
| `formal/`, `references/`, `discussions/`, `datasets/`, `data/` | Supporting material | |

Governing documents at root: `NOTE_TEMPLATE.md`, `NOTES_INDEX.md`,
`DISCUSSION_NORMS.md`, `DRIFT_LEDGER.md`, `ROADMAP.md`, `WHITEPAPER.md`,
`CONTRIBUTING.md`.

---

## Naming conventions

Two conventions are in use and both are live:

- `NNN_short_title.md` — 45 files (earlier series)
- `noteNNN_short_title.md` — 24 files (later series)

`scripts/make_index.py` matches both patterns and indexes **69 notes**. There
are **78 `.md` files in `research_notes/`**, so roughly 9 files match neither
pattern and are invisible to the index. Before adding a note, match one of the
two patterns exactly or it will not appear in `NOTES_INDEX.md`.

Reference code convention: `scripts/noteNNN_reference.py`, dependency-light
(NumPy-tier), printing every number that appears in the note.

---

## Known defects — read before you "fix" anything

These are recorded, not hidden. Do not paper over them.

1. **Number collisions are real and intentional to display.** `NOTES_INDEX.md`
   reports 20 numbers claimed by multiple notes, marked ⚡. Collisions are
   *shown*, not resolved by silent renumbering. Example: `#041` is claimed by
   both `041_retrocausal_self_consistency.md` and
   `note041_persistent_homology.md`.

2. **`notes/` duplicates numbers already used in `research_notes/`.**
   - `notes/028_thought_tensor_category_morphism.md` vs
     `research_notes/028_categorical_quantum_gravity_thought.md`
   - `notes/note048_grok_contribution_manifesto.md` vs
     `research_notes/note048_the_governor_is_the_dynamics.md`
   Different titles, same numbers. `notes/` is a stray directory. Consolidating
   it into `research_notes/` is a real cleanup task — but it changes note
   numbering, so **ask before doing it**.

3. **`START_HERE.md` is wrong.** It is an SECP deployment guide that tells the
   reader "All files are in `/mnt/user-data/outputs/`" — an AI sandbox path that
   exists on no reader's machine. It does not introduce the notes program at
   all. The file named START_HERE is currently the worst entry point in the
   repo. Rewriting it is high value.

4. **The graph is a star, not a network.** Across 78 notes there are **4
   `[[wikilinks]]` total**; 76 notes have zero outgoing links. `NOTES_INDEX.md`
   links out to everything, so the topology is one hub with 78 spokes and
   almost no lateral edges. Opening this vault in Obsidian today produces a
   scatter plus an orphan ring. Adding real cross-links is the single highest-
   value structural improvement available, and the 20 ⚡ collisions are the
   obvious first candidates — notes that collide on a number are usually
   topically adjacent.

---

## House rules for agents

- **Ask before restructuring.** Renumbering, merging directories, or bulk
  renaming changes the note series identity. Propose, don't perform.
- **Never edit a note to make a claim look better.** If a registered prediction
  failed, the failure stays and gets explained.
- **Never delete a refuted note.** `⚠` in the index marks kept failures. That
  mark is an asset.
- **Do not hand-edit `NOTES_INDEX.md`.** It is auto-generated. Edit notes, then
  re-run `python scripts/make_index.py`.
- **Preserve `[[wikilinks]]` and existing markdown links** on any edit.
- **Credit contributors, including AIs, by model name.**
- **Do not present a reading of a file as a verified fact.** Run it, paste the
  output, then claim it.
- **Do not add a claim to a note without the code that prints its numbers.**
  If there is no code yet, label the note `Speculative` and describe the
  experiment someone else could build. That is a valid contribution.
- **One command at a time** when handing commands to the operator; this repo is
  driven from Termux on an Android device.

---

## Commands

```bash
make synthetic              # run all synthetic demos via scripts/run_all_notes.py
make real                   # synthetic, then attempt real model eval (needs GPU/transformers)
make report                 # cat results/last_run_report.json
make clean                  # remove report + __pycache__
python scripts/make_index.py    # regenerate NOTES_INDEX.md after editing notes
python sovereign_core/test_sovereign.py   # governance suite (expect 33/33)
```

Environment note: this repo is developed on a Samsung Galaxy S25 Ultra under
Termux (aarch64, Python 3.14). `set +H` before pasting anything containing `!`
or markdown image syntax. `/tmp` is not writable — use `$HOME`.

---

## Adding a note — checklist

Copy `NOTE_TEMPLATE.md`. Then, before opening a PR:

- [ ] filename matches `NNN_*.md` or `noteNNN_*.md` exactly
- [ ] status label is honest
- [ ] claims registered and numbered (P1, P2, …)
- [ ] anti-vacuity control present — the instrument can return null
- [ ] any refuted claim kept and marked
- [ ] every number in the prose matches `scripts/noteNNN_reference.py` output
- [ ] at least one open prediction left unrun
- [ ] at least one outgoing `[[wikilink]]` to a related note (no orphans)
- [ ] credit given, including to AI contributors
- [ ] `python scripts/make_index.py` re-run and the note appears
