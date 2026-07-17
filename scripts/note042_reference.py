#!/usr/bin/env python3
"""
note042_reference.py — Coarse Ricci curvature of reasoning trajectories.
"""

import numpy as np

def wasserstein_1(p, q):
    n = len(p)
    p = p / p.sum()
    q = q / q.sum()
    cum_diff = np.cumsum(p - q)
    return np.sum(np.abs(cum_diff))

def coarse_ricci(p_t, p_tplus1, base_distance=1.0):
    w1 = wasserstein_1(p_t, p_tplus1)
    return 1 - w1 / base_distance

def synthetic_reasoning_trajectory(length=20, correct=True):
    np.random.seed(42)
    vocab_size = 50
    t0 = np.zeros(vocab_size)
    t0[0] = 0.9
    t0[1:] = 0.1 / (vocab_size-1)
    t_target = np.zeros(vocab_size)
    t_target[5] = 0.8
    t_target[0] = 0.1
    t_target[1] = 0.05
    t_target[2:] = 0.05 / (vocab_size-3)
    traj = []
    for step in range(length):
        alpha = step / (length - 1) if length > 1 else 0.5
        if not correct and step > length // 2:
            wrong_target = np.zeros(vocab_size)
            wrong_target[10] = 0.9
            wrong_target[0] = 0.05
            wrong_target[1] = 0.03
            wrong_target[2:] = 0.02 / (vocab_size-3)
            current = traj[-1] if traj else t0
            beta = (step - length//2) / (length//2)
            blended = (1 - beta) * current + beta * wrong_target
            blended /= blended.sum()
            traj.append(blended)
        else:
            interp = (1 - alpha) * t0 + alpha * t_target
            interp /= interp.sum()
            traj.append(interp)
    return np.array(traj)

def main():
    print("=== Coarse Ricci Curvature of Synthetic Reasoning Trajectories ===\n")
    for correct in [True, False]:
        traj = synthetic_reasoning_trajectory(length=15, correct=correct)
        curvatures = [coarse_ricci(traj[i], traj[i+1]) for i in range(len(traj)-1)]
        label = "Correct reasoning" if correct else "Hallucination"
        print(f"--- {label} ---")
        print(f" Step   Ricci κ")
        for i, k in enumerate(curvatures):
            marker = " *" if k < 0 else ""
            print(f" {i:3d}   {k: 7.4f}{marker}")
        print(f" Mean curvature: {np.mean(curvatures):.4f}")
        print(f" Min curvature:  {np.min(curvatures):.4f}")
        print(f" Negative?       {'YES' if np.min(curvatures) < 0 else 'NO'}\n")
    print("--- Phase Transition Detection ---")
    traj = synthetic_reasoning_trajectory(length=15, correct=False)
    curvatures = [coarse_ricci(traj[i], traj[i+1]) for i in range(len(traj)-1)]
    cumulative = np.cumsum(curvatures)
    print("Cumulative Ricci curvature:")
    for i, c in enumerate(cumulative):
        print(f" Step {i+1}: {c:.4f}")
    diffs = np.diff(cumulative)
    threshold = 2 * np.std(diffs)
    drop_steps = [i for i in range(len(diffs)) if diffs[i] < -threshold]
    print(f" Threshold for significant drop: {threshold:.4f}")
    print(f" Steps with significant drop: {drop_steps}")
    if drop_steps:
        print("→ Phase transition detected.")
    else:
        print("→ No phase transition detected.")

if __name__ == "__main__":
    main()
