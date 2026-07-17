"""
Note #040 — THE REDUNDANCY DIVIDEND: radiation-hard AI for free?
=================================================================
Space radiation, cosmic rays at altitude, and silent data corruption in
datacenters all do the same thing to a neural network: they kill neurons
and flip weights at random. Industry answers with HARDWARE (shielding,
ECC, triple modular redundancy). This note asks whether the KNOWLEDGE
can be hardened instead — and measured for hardness BEFORE deployment.

Bridge from Note #039: Quantum Darwinism => a network makes selected
information OBJECTIVE by imprinting it REDUNDANTLY across neuron
fragments, and that redundancy is measurable (fragment mutual info).
Unclaimed consequence: Darwinian redundancy should PREDICT fault
tolerance, and training-time pressure toward redundancy should buy
radiation-hardness with zero extra silicon.

Models: MLP 4->20->1, y = sign(x1), three training regimes spanning a
redundancy spectrum: L1-sparse (concentrates knowledge), plain, dropout
(predicted by #039-D5 to proliferate it). 4 seeds each = 12 models,
matched clean accuracy required (>= 0.95) or the model is excluded.

REGISTERED (before running):
  R0  ANTI-VACUITY: the fault instrument must discriminate — spread of
      p_crit across models >= 1.5x (max/min). If all models are equally
      robust the test is uninformative and NO claim may be made.
  R1  Darwinian redundancy R = shuffle-corrected I(task bit; 25% neuron
      fragment) PREDICTS knockout tolerance: Spearman rank corr(R,
      p_crit) >= +0.7 across models.
  R2  (= #039-D5, an OPEN prediction of this repo, now run): dropout
      training yields HIGHER mean R than plain at matched accuracy.
  R3  R predicts p_crit BETTER than clean accuracy does:
      |rho(R, p_crit)| > |rho(acc, p_crit)|.
  R4  Same ranking holds under a second, different fault model (random
      sign-flips of first-layer weights): rho(R, p_crit_flip) >= +0.7.
"""
import numpy as np
rng = np.random.default_rng(17)
H = 20

def data(n, r=rng):
    X = r.normal(0, 1, (n, 4))
    return X, (X[:, 0] > 0).astype(int)

def fwd(p, X, mask=None):
    Hh = np.tanh(X @ p[0] + p[1])
    if mask is not None: Hh = Hh * mask
    o = 1/(1+np.exp(-(Hh @ p[2] + p[3]).ravel()))
    return Hh, o

def train(regime, seed, steps=2600, bs=64, lr=0.3):
    r = np.random.default_rng(seed)
    p = [r.normal(0,.4,(4,H)), np.zeros(H), r.normal(0,.4,(H,1)), np.zeros(1)]
    for s in range(steps):
        X, y = data(bs, r)
        Hh = np.tanh(X @ p[0] + p[1])
        keep = np.ones(H)
        if regime == "dropout":
            keep = (r.random(H) > 0.4) / 0.6
        Hd = Hh * keep
        o = 1/(1+np.exp(-(Hd @ p[2] + p[3]).ravel()))
        g = (o - y) / bs
        gW2 = Hd.T @ g[:, None]; gb2 = g.sum()
        gH = np.outer(g, p[2].ravel()) * keep * (1 - Hh**2)
        p[0] -= lr * (X.T @ gH + (0.004*np.sign(p[0]) if regime=="sparse" else 0))
        p[1] -= lr * gH.sum(0)
        p[2] -= lr * (gW2 + (0.004*np.sign(p[2]) if regime=="sparse" else 0))
        p[3] -= lr * gb2
    return p

def acc(p, n=3000, mask=None):
    X, y = data(n, np.random.default_rng(999))
    _, o = fwd(p, X, mask)
    return ((o > .5) == y).mean()

def mi_bits(y, Hs, frag):
    pat = ((Hs[:, frag] > 0) @ (1 << np.arange(len(frag)))).astype(int)
    I = 0.0
    for s in np.unique(pat):
        m = pat == s; ps = m.mean()
        for c in (0, 1):
            pj = (m & (y == c)).mean()
            if pj > 0: I += pj*np.log2(pj/(ps*(y==c).mean()))
    return I

def redundancy(p, n=5000, f=5, reps=40):
    X, _ = data(n, np.random.default_rng(555))
    y = (X[:, 0] > 0).astype(int)
    Hs, _ = fwd(p, X)
    vals = []
    for _ in range(reps):
        fr = rng.choice(H, f, replace=False)
        vals.append(mi_bits(y, Hs, fr) - mi_bits(rng.permutation(y), Hs, fr))
    return max(0.0, float(np.mean(vals)))

def p_crit_knockout(p, thresh=0.9):
    """largest neuron-death fraction at which mean acc still >= thresh"""
    grid = np.linspace(0, 0.9, 19); last = 0.0
    for q in grid:
        accs = []
        for t in range(24):
            m = (np.random.default_rng(7000+t).random(H) > q).astype(float)
            accs.append(acc(p, 1500, m))
        if np.mean(accs) >= thresh: last = q
        else: break
    return last

def p_crit_flip(p, thresh=0.9):
    """largest fraction of W1 sign-flips (SEU model) with acc >= thresh"""
    grid = np.linspace(0, 0.9, 19); last = 0.0
    for q in grid:
        accs = []
        for t in range(24):
            r2 = np.random.default_rng(9000+t)
            W = p[0].copy()
            f = r2.random(W.shape) < q
            W[f] = -W[f]
            accs.append(acc([W,p[1],p[2],p[3]], 1500))
        if np.mean(accs) >= thresh: last = q
        else: break
    return last

def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    return float((ra*rb).sum()/np.sqrt((ra**2).sum()*(rb**2).sum()))

rows = []
print(f"{'regime':>8} {'seed':>4} {'acc':>6} {'R (bits)':>9} "
      f"{'p_crit KO':>10} {'p_crit flip':>11}")
for regime in ("sparse", "plain", "dropout"):
    for seed in range(4):
        p = train(regime, 100+seed)
        a = acc(p)
        if a < 0.95:
            print(f"{regime:>8} {seed:>4}  EXCLUDED (acc {a:.3f})"); continue
        R = redundancy(p)
        ko = p_crit_knockout(p); fl = p_crit_flip(p)
        rows.append((regime, seed, a, R, ko, fl))
        print(f"{regime:>8} {seed:>4} {a:>6.3f} {R:>9.3f} {ko:>10.2f} {fl:>11.2f}")

reg = np.array([r[0] for r in rows]); A = np.array([r[2] for r in rows])
R = np.array([r[3] for r in rows]); KO = np.array([r[4] for r in rows])
FL = np.array([r[5] for r in rows])
r0 = KO.max()/max(KO.min(),1e-9) >= 1.5
rho_R  = spearman(R, KO); rho_A = spearman(A, KO); rho_F = spearman(R, FL)
mR = {g: R[reg==g].mean() for g in ("sparse","plain","dropout")}
print(f"\nR0 instrument discriminates (spread {KO.max()/max(KO.min(),1e-9):.1f}x "
      f">= 1.5x): {r0}")
print(f"R1 redundancy predicts knockout tolerance: rho = {rho_R:+.2f} "
      f"(>= +0.7): {rho_R >= 0.7}")
print(f"R2 (#039-D5 CLOSED) mean R — sparse {mR['sparse']:.3f} | plain "
      f"{mR['plain']:.3f} | dropout {mR['dropout']:.3f} : "
      f"{mR['dropout'] > mR['plain']}")
print(f"R3 R beats accuracy as predictor: |{rho_R:+.2f}| > |{rho_A:+.2f}| : "
      f"{abs(rho_R) > abs(rho_A)}")
print(f"R4 transfers to SEU sign-flip faults: rho = {rho_F:+.2f} "
      f"(>= +0.7): {rho_F >= 0.7}")
np.savez("n40.npz", R=R, KO=KO, FL=FL, A=A,
         reg=np.array([r[0] for r in rows]))
