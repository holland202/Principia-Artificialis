#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Principia Artificialis — Exp #003 Cycle Script (Termux)
# Runs thermal monitor, updates plot, commits & pushes iteration.
# ═══════════════════════════════════════════════════════════════

set -e

REPO="$HOME/Principia-Artificialis"
DATA_DIR="$REPO/data"
FIGURES_DIR="$REPO/figures"
SCRIPTS_DIR="$REPO/scripts"

cd "$REPO"

# 1. Ensure we're on main and up to date
echo "[1/7] Pulling latest main..."
git checkout main
git pull

# 2. Ensure data directory exists
echo "[2/7] Ensuring data directory exists..."
mkdir -p "$DATA_DIR"

# 3. Run thermal monitor briefly to collect new metrics
echo "[3/7] Running thermal monitor for ~25 seconds to collect new metrics..."
timeout 25 python "$SCRIPTS_DIR/veritas_thermal_monitor.py" || true

# 4. Generate updated thermal plot
echo "[4/7] Generating updated thermal plot..."
python "$SCRIPTS_DIR/plot_thermal_metrics.py"

# 5. Stage changes (including this script itself)
echo "[5/7] Staging changes..."
git add data/thermal_metrics.log
git add scripts/plot_thermal_metrics.py
git add scripts/run_exp003_cycle.sh
git add figures/thermal_relaxation_exp003.png

# 6. Commit (allow empty so each run is recorded)
echo "[6/7] Committing iteration..."
git commit -m "feat(exp003): Iteration $(date -u +%Y%m%d-%H%M%S) UTC (holland202)" || \
git commit --allow-empty -m "feat(exp003): Iteration $(date -u +%Y%m%d-%H%M%S) UTC (no file changes) (holland202)"

# 7. Push
echo "[7/7] Pushing to origin/main..."
git push origin main

echo "Exp #003 cycle complete."
