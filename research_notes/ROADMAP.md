# Research Roadmap — Principia Artificialis

## Completed (as of 2026-07-16)

- **Information-geometric foundation**  
  - Fisher-Rao and Wasserstein geometries — Note #020  
  - Visualization: `figures/note020_wasserstein_vs_fisherrao.png`

- **Manifold topology**  
  - 6-panel manifold visualization (geodesics, curvature, defects) — Note #008  
  - Visualization: `figures/manifold_topology_6panel.png`

- **Thermodynamic engine analogy**  
  - Thermodynamic cycles and phase boundaries — Notes #006–#008  
  - Visualizations: `figures/thermodynamic_engine.png`, `figures/sim001_thermo_engine.png`

- **Quantum entanglement diagnostics**  
  - Entanglement entropy, Bell inequalities, circuit complexity, advantage — Note #021  
  - Visualization: `figures/quantum_frontiers.png`

- **Renormalization-group flow**  
  - RG flow of effective couplings in representation space — Note #021  
  - Visualization: `figures/renormalization_flow.png`

- **Research dependency network**  
  - Graph of dependencies among notes, experiments, and figures — Note #021  
  - Visualization: `figures/research_dependency_network.png`

- **Pipeline documentation**  
  - Experiment/figure generation pipeline — `figures/exp001_pipeline.mmd`

## In progress

- **Quantum Fisher Information metric**  
  - QFI / Bures geometry on representation space — Note #022 (draft)  
  - Planned figure: `figures/note022_qfi_eigenvalue_spectrum.png`

- **Quantum thermodynamic RG framework**  
  - Synthesis of thermo, RG, and quantum information — Note #023 (this file’s companion)

## Next figures to generate

1. `figures/note022_qfi_eigenvalue_spectrum.png`  
   - QFI eigenvalue spectrum vs layer index / RG scale.  
   - Compare with classical Fisher-Rao eigenvalues.

2. `figures/quantum_thermo_cycle.png`  
   - P–V–like diagram for the quantum inference engine.  
   - Annotate strokes: compression, expansion, heat exchange.

3. `figures/rg_flow_with_qfi.png`  
   - RG trajectories from `renormalization_flow.png` enriched with QFI curvature indicators.  
   - Highlight fixed points and hypothesized thermodynamic phases.

## Open theoretical questions

- Do RG fixed points coincide with thermodynamic phase transitions in the representation space?
- Is there a universal relation between entanglement entropy and QFI curvature across architectures?
- Can we derive an explicit free-energy functional (mathcal{F}) whose gradient flow yields the observed RG dynamics?
- Are there architecture-specific “Carnot-like” bounds on task performance given entanglement and curvature constraints?
- How does the Wasserstein–Fisher-Rao–QFI tri-geometry change with training time, data distribution, or task complexity?

## Suggested next steps

1. Finalize Note #022 (QFI metric) and generate `note022_qfi_eigenvalue_spectrum.png`.
2. Implement QFI estimation for small latent dimensions on a toy model.
3. Construct explicit thermodynamic cycle diagrams for at least one task and model.
4. Test entanglement–curvature–efficiency triad hypotheses empirically.
