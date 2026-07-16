# Exp #001: Entropy Production Monitoring Protocol

## Contribution by Perplexity

This addition is append-only and designed as a standalone research note for the repository compilation. It frames the runtime thermal monitor as a reproducible experiment rather than a replacement for any existing work.

### Purpose

Monitor SoC temperature over time, compute a simple Gibbs-inspired gating function, and record state transitions for later analysis. The implementation is intentionally modular so it can be adapted for Termux, Android, or simulated inputs.

### Design Notes

- Externalize thresholds and sample intervals instead of hardcoding them in multiple places.
- Log temperature, computed gate values, and trigger events to CSV for later plotting.
- Keep the loop safe, minimal, and easy to extend with additional observables.

### Research Direction

This experiment can support future work on thermal phase changes, adaptive throttling analogies, and visual exploration of threshold behavior. It is a seed for broader simulation and theory-building rather than a final claim.

## Update: Thermodynamic Visualization
The visualization pipeline for `Exp #001` is now live, providing dual-axis tracking of thermal breach events versus Gibbs proxy fluctuations.
