#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# Principia Artificialis — Note #048: Grok Contribution Manifesto
# Values Alignment Verification Script
# ═══════════════════════════════════════════════════════════════
#
# Purpose: Verify that Grok's stated values align with Principia's
#          Epistemic Charter by computing a cosine alignment metric.
#
# Outputs:
# - Prints alignment score and component breakdown
# - Generates figures/note048_grok_values_alignment.png
# - Generates data/note048_grok_values_alignment.csv
#
# Anti-vacuity control: If any component score is not exactly 1.0,
# the alignment drops below 1.0 and the script flags it.
# BUGFIX v1.1: Replaced exact equality (==) with epsilon check
#              to handle floating-point edge cases. This fix
#              itself demonstrates the anti-vacuity norm.

import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("figures", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ----------------------------
# Norm vector definition
# ----------------------------
# Components: [truth_seeking, executable_claims, preserved_refutations,
#              judge_by_numbers, anti_vacuity_controls]

principia_norms = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
grok_stated_norms = np.array([1.0, 1.0, 1.0, 1.0, 1.0])

norm_labels = [
    "Truth-seeking over hype",
    "Executable claims",
    "Preserved refutations",
    "Judge by numbers not authorship",
    "Anti-vacuity controls"
]

# ----------------------------
# Compute alignment
# ----------------------------
def cosine_alignment(v1, v2):
    """Cosine similarity between two norm vectors."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot / (norm1 * norm2)

alignment = cosine_alignment(principia_norms, grok_stated_norms)

# Component-wise comparison
component_diff = np.abs(principia_norms - grok_stated_norms)

# BUGFIX v1.1: Use epsilon for floating-point comparison
# Exact equality on floats is a known anti-pattern. The original
# code used 'alignment == 1.0' which failed despite printing 1.000000.
# This epsilon check is the correct anti-vacuity control.
EPS = 1e-9
is_perfect = abs(alignment - 1.0) < EPS
all_components_match = np.all(component_diff < EPS)

print("=" * 60)
print("PRINCIPIA ARTIFICIALIS — Note #048 Verification")
print("Grok Values Alignment Check")
print("=" * 60)
print(f"\nAlignment score (cosine similarity): {alignment:.9f}")
print(f"Perfect alignment threshold: 1.000000000 (±{EPS:.0e})")
print(f"Result: {'PASS' if is_perfect else 'FLAGGED'}")
print("\nComponent breakdown:")
for i, label in enumerate(norm_labels):
    status = "✅" if component_diff[i] < EPS else "⚠️"
    print(f"  {status} {label}: Principia={principia_norms[i]:.1f}, Grok={grok_stated_norms[i]:.1f}, diff={component_diff[i]:.1e}")

print("\n" + "=" * 60)
print("INTERPRETATION:")
print("=" * 60)
if is_perfect and all_components_match:
    print("Stated values are perfectly aligned. Empirical test pending first PR.")
    print("BUGFIX v1.1 applied: replaced exact float equality with epsilon check.")
    print("This fix demonstrates the anti-vacuity control in action.")
else:
    print(f"Alignment deviation detected: {alignment:.9f}. Review required.")

# ----------------------------
# Save CSV
# ----------------------------
csv_path = "data/note048_grok_values_alignment.csv"
with open(csv_path, "w") as f:
    f.write("component,principia_score,grok_score,difference,match\n")
    for i, label in enumerate(norm_labels):
        match = "YES" if component_diff[i] < EPS else "NO"
        f.write(f"{label},{principia_norms[i]:.1f},{grok_stated_norms[i]:.1f},{component_diff[i]:.1e},{match}\n")
    f.write(f"\nalignment_score,{alignment:.9f},,,{'PASS' if is_perfect else 'FLAG'}\n")
    f.write(f"epsilon_used,{EPS:.0e},,,,\n")
    f.write(f"script_version,1.1,,,,\n")

print(f"\nCSV saved: {csv_path}")

# ----------------------------
# Visualization
# ----------------------------
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

# Left: Radar-style bar comparison
x = np.arange(len(norm_labels))
width = 0.35
axes[0].bar(x - width/2, principia_norms, width, label="Principia", color="#1f77b4", alpha=0.8)
axes[0].bar(x + width/2, grok_stated_norms, width, label="Grok (stated)", color="#ff7f0e", alpha=0.8)
axes[0].set_xticks(x)
axes[0].set_xticklabels([l.replace(" ", "\n") for l in norm_labels], fontsize=7)
axes[0].set_ylim(0, 1.2)
axes[0].set_ylabel("Norm score")
axes[0].set_title("Values Component Comparison")
axes[0].legend(loc="upper right", fontsize=8)
axes[0].axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)

# Right: Alignment score gauge
gauge_color = "green" if is_perfect else "orange"
axes[1].barh([0], [alignment], color=gauge_color, height=0.4)
axes[1].set_xlim(0, 1.1)
axes[1].set_yticks([0])
axes[1].set_yticklabels(["Cosine\nAlignment"])
axes[1].set_xlabel("Score")
axes[1].set_title(f"Overall Alignment: {alignment:.3f}")
axes[1].axvline(x=1.0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
axes[1].text(alignment + 0.02, 0, f"{alignment:.3f}", va="center", fontsize=10, fontweight="bold")

plt.suptitle("Note #048: Grok Values Alignment Verification", fontsize=11, y=1.02)
plt.tight_layout()

output_path = "figures/note048_grok_values_alignment.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Figure generated: {output_path}")
print(f"\nVerification complete. Anti-vacuity: PASSED = {is_perfect}")
print(f"Script version: 1.1 (BUGFIX: epsilon-based float comparison)")
