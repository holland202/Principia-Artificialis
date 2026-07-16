# Experiment #003 — Thermal Relaxation of the Veritas Gate

**Status:** Protocol Ready  
**Related Notes:** #004 (Thermodynamic Quantities), #011 (Arrow of Reasoning), #027 (Extractability Budget)  
**Author:** holland202  

---

## Motivation

If reasoning is a physical process, then successful inference should exhibit measurable thermodynamic signatures. Experiment #003 treats the device’s thermal response as a proxy for the “cost” of maintaining coherent computation under load. The Veritas Gate daemon enforces a thermal ceiling and records relaxation dynamics each time the ceiling is exceeded.

---

## Setup

**Substrate:** Snapdragon 8 Elite (SM8750‑AB) via Termux  
**Daemon:** `scripts/veritas_thermal_monitor.py`  
**Metrics Log:** `data/thermal_metrics.log`  
**Visualization:** `figures/thermal_relaxation_exp003.png`  
**Cycle Script:** `scripts/run_exp003_cycle.sh`

**Key parameters:**

- Thermal ceiling: (T_{\text{ceiling}} = 38.5^circ\text{C})
- Nominal band: (T_{\text{nominal}} = 31.0^circ\text{C})
- Polling rate: 10 Hz

---

## Protocol

1. Run `veritas_thermal_monitor.py` continuously in Termux.
2. When (T ge T_{\text{ceiling}}), the daemon:
   - Logs a “THERMAL CEILING EXCEEDED” event.
   - Enters a cooling phase until (T le T_{\text{nominal}}).
   - Records:
     - Peak temperature (T_{\text{peak}})
     - Recovery duration (\tau = t_{\text{end}} - t_{\text{start}})
3. The cycle script (`run_exp003_cycle.sh`):
   - Runs the monitor for ~25 s.
   - Regenerates the plot.
   - Commits and pushes the updated log and figure as an iteration.

**Log format** (`data/thermal_metrics.log`):

```text
timestamp_unix,T_peak (°C),τ (s)
