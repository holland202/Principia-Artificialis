# Repository Dependency Graph

## Contribution by Perplexity

This note adds a GitHub-native Mermaid graph that maps how the repository's ideas, experiments, and outputs connect.

### Diagram

```mermaid
flowchart TD
    N001[#001 Measurement] --> N003[#003 Fisher Information]
    N002[#002 Topological Defects] --> N008[#008 Falsification Protocol]
    N003 --> N004[#004 Thermodynamics]
    N004 --> N011[#011 Thermodynamic Arrow]
    N005[#005 Geodesics] --> N009[#009 Quantum Entanglement]
    N005 --> N013[#013 Symplectic Attention]
    N009 --> E002[Exp #002 Quantum-Geodesic Bridge]
    N013 --> E002
    N011 --> E001[Exp #001 Entropy Monitor]
    N002 --> E001
    N003 --> E001
    E001 --> V001[Visual Dashboard]
    E001 --> V002[Pipeline Diagram]
    N020[#020 Optimal Transport] --> W020[Wasserstein vs Fisher-Rao Figure]
    N020 --> N021[#021 Hyperbolic Attention]
## Use this fix script

```bash
#!/usr/bin/env bash
set -euo pipefail

GIT_REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
COMMIT_MSG="fix(visuals): repair exp001 dependency graph formatting"

NOTE_PATH="research_notes/exp001_dependency_graph.md"

mkdir -p "$(dirname "$NOTE_PATH")"

cat > "$NOTE_PATH" <<'EOF'
# Repository Dependency Graph

## Contribution by Perplexity

This note adds a GitHub-native Mermaid graph that maps how the repository's ideas, experiments, and outputs connect.

### Diagram

```mermaid
flowchart TD
    N001[#001 Measurement] --> N003[#003 Fisher Information]
    N002[#002 Topological Defects] --> N008[#008 Falsification Protocol]
    N003 --> N004[#004 Thermodynamics]
    N004 --> N011[#011 Thermodynamic Arrow]
    N005[#005 Geodesics] --> N009[#009 Quantum Entanglement]
    N005 --> N013[#013 Symplectic Attention]
    N009 --> E002[Exp #002 Quantum-Geodesic Bridge]
    N013 --> E002
    N011 --> E001[Exp #001 Entropy Monitor]
    N002 --> E001
    N003 --> E001
    E001 --> V001[Visual Dashboard]
    E001 --> V002[Pipeline Diagram]
    N020[#020 Optimal Transport] --> W020[Wasserstein vs Fisher-Rao Figure]
    N020 --> N021[#021 Hyperbolic Attention]
## Why this will work

The actual Mermaid block is fine; the issue is that the file content likely contained hidden text or formatting corruption around the closing fence. Rewriting the file from scratch with clean markdown ensures GitHub parses the diagram as a standalone block [1][3][4].

## Next useful artifact

After this repair, the next best contribution is still the **rolling statistics chart** for the Exp #001 CSV, because it adds real analysis rather than another structural diagram.
