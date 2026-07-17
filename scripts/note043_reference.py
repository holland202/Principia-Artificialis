#!/usr/bin/env python3
import numpy as np

def wasserstein_1(p, q):
    p, q = p / p.sum(), q / q.sum()
    return np.sum(np.abs(np.cumsum(p - q)))

def coarse_ricci(p_t, p_tplus1, base_distance=1.0):
    return 1 - wasserstein_1(p_t, p_tplus1) / base_distance

def entropy_production(p_t, p_tplus1, eps=1e-12):
    p, q = p_tplus1 + eps, p_t + eps
    return np.sum(p * np.log(p / q))

def topological_persistence(W):
    n = W.shape[0]
    W = (W + W.T) / 2
    np.fill_diagonal(W, 0)
    L = np.diag(W.sum(axis=1)) - W
    eigenvalues = np.linalg.eigvalsh(L)
    gaps = np.diff(eigenvalues[eigenvalues > 1e-6])
    if len(gaps) == 0:
        return 0.0
    return np.sum(np.log(1.0 / (gaps + 1e-12)))

def rmt_variance(W):
    eigvals = np.linalg.eigvalsh(W)
    eigvals = np.sort(eigvals)
    spacings = np.diff(eigvals)
    spacings = spacings[spacings > 1e-6]
    if len(spacings) < 2:
        return 0.0
    mean_spacing = np.mean(spacings)
    if mean_spacing == 0:
        return 0.0
    unfolded = spacings / mean_spacing
    return np.var(unfolded)

def free_energy(trajectory, lambdas=(0.1, 1.0, 1.0, 0.5), base_distance=1.0):
    lambda_curv, lambda_ent, lambda_pers, lambda_rmt = lambdas
    curv_term = 0.0
    ent_term = 0.0
    for i in range(len(trajectory)-1):
        k = coarse_ricci(trajectory[i], trajectory[i+1], base_distance)
        curv_term -= k
        ent_term += entropy_production(trajectory[i], trajectory[i+1])
    stds = [np.std(p) for p in trajectory]
    pers_proxy = np.mean(stds)
    pers_term = -pers_proxy
    mat = np.array(trajectory)
    cov = np.cov(mat.T)
    rmt_term = rmt_variance(cov)
    return lambda_curv * curv_term + lambda_ent * ent_term + lambda_pers * pers_term + lambda_rmt * rmt_term

def generate_trajectory(length=15, correct=True):
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
    return traj

def main():
    print("=== Free Energy of Reasoning (FER) ===\n")
    for correct in [True, False]:
        traj = generate_trajectory(length=15, correct=correct)
        F = free_energy(traj)
        label = "Correct" if correct else "Hallucinated"
        print(f"{label} reasoning trajectory: F = {F:.4f}")
        beta = 1.0
        p = np.exp(-beta * F) / (np.exp(-beta * F) + 1.0)
        print(f"  Boltzmann p(correct | F) = {p:.4f}\n")
    print("--- Multiple trajectories ---")
    np.random.seed(123)
    for _ in range(5):
        correct = np.random.rand() > 0.5
        traj = generate_trajectory(length=15, correct=correct)
        F = free_energy(traj)
        label = "Correct" if correct else "Hallucinated"
        print(f"{label}: F = {F:.4f}")
    print("\n--- AUC estimate ---")
    n = 200
    FC, FI = [], []
    for _ in range(n):
        FC.append(free_energy(generate_trajectory(length=15, correct=True)))
        FI.append(free_energy(generate_trajectory(length=15, correct=False)))
    count = sum(1 for fc in FC for fi in FI if fc < fi)
    auc = count / (n * n)
    print(f"Estimated AUC: {auc:.4f}")

if __name__ == "__main__":
    main()
