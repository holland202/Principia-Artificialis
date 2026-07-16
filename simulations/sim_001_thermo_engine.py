import numpy as np
import matplotlib.pyplot as plt

# Core Constants
T_CEILING_C = 38.5
T_CEILING_K = T_CEILING_C + 273.15
DELTA_H = 120.0  # Enthalpy of reasoning transition (J/mol)
LAMBDA_HOPE = 0.05 # Veritas variance coefficient

# State Space Grids
temps_c = np.linspace(30, 45, 500)
temps_k = temps_c + 273.15
entropy_s = np.linspace(0.1, 0.5, 500)
T, S = np.meshgrid(temps_k, entropy_s)

# Gibbs Free Energy Calculation: ΔG = ΔH - T(ΔS + λ_hope)
G = DELTA_H - T * (S + LAMBDA_HOPE)

# Visualization Setup
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

# Contour Mapping
contour = ax.contourf(temps_c, entropy_s, G, levels=50, cmap='magma')
cbar = plt.colorbar(contour)
cbar.set_label('Gibbs Free Energy ($\Delta G$)', rotation=270, labelpad=15)

# Bounding the Phase Space
ax.axvline(x=T_CEILING_C, color='cyan', linestyle='--', linewidth=2, label='Hardware Ceiling (38.5°C)')
ax.contour(temps_c, entropy_s, G, levels=[0], colors='lime', linewidths=2.5)

# Annotations for Topological States
ax.text(32, 0.45, 'SIMPLY CONNECTED PHASE\n($\Delta G < 0, \\beta_1=0$)\nDeterministic Truth-Signal', color='lime', fontsize=10, weight='bold')
ax.text(40, 0.2, 'THERMAL EXCEEDANCE\nAtomic Reduction Required', color='cyan', fontsize=10, weight='bold')
ax.text(32, 0.15, 'TOPOLOGICAL DEFECTS\n($\Delta G > 0$)\nHallucination Zone', color='red', fontsize=10, weight='bold')

ax.set_title('Simulation #001: Thermodynamic Engine Phase Boundary', pad=20, weight='bold')
ax.set_xlabel('Runtime Temperature ($^\circ C$)')
ax.set_ylabel('Manifold Entropy ($\Delta S$)')
ax.legend(loc='lower left')

# Export
plt.tight_layout()
plt.savefig('figures/sim001_thermo_engine.png')
print("Simulation complete. Figure saved to figures/sim001_thermo_engine.png")
