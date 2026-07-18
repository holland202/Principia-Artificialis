"""
Note #045 — THE STUBBORNNESS OF THE OBJECTIVE: redundancy predicts
resistance to deliberate unlearning
====================================================================
Machine unlearning (GDPR erasure, capability removal, safety) asks: how
hard is it to make a network FORGET on purpose? Note #040 showed
Darwinian redundancy predicts survival under RANDOM damage. Unclaimed
consequence: the same number should predict survival under TARGETED
damage — gradient-ascent unlearning. If true: objectivity (in Zurek's
redundancy sense) is precisely the property that resists erasure. What
a network makes objective, it also makes stubborn.

REGISTERED:
  U0  ANTI-VACUITY: spread in steps-to-forget across models >= 2x.
  U1  Spearman rho(redundancy, steps-to-forget) >= +0.7 across 12
      models at matched clean accuracy (>= 0.95).
  U2  Redundancy out-predicts clean accuracy: |rho_R| > |rho_acc|.
  U3  SAFETY COROLLARY (directional): dropout-trained (high-R) models
      require more ascent steps to forget than sparse (low-R) ones,
      mean vs mean.
"""
import numpy as np
rng = np.random.default_rng(31)
H = 20

def data(n, r=rng):
    X = r.normal(0, 1, (n, 4)); return X, (X[:, 0] > 0).astype(int)

def fwd(p, X):
    Hh = np.tanh(X @ p[0] + p[1])
    return Hh, 1/(1+np.exp(-(Hh @ p[2] + p[3]).ravel()))

def train(regime, seed, steps=2600, bs=64, lr=0.3):
    r = np.random.default_rng(seed)
    p = [r.normal(0,.4,(4,H)), np.zeros(H), r.normal(0,.4,(H,1)), np.zeros(1)]
    for s in range(steps):
        X, y = data(bs, r)
        Hh = np.tanh(X @ p[0] + p[1])
        keep = (r.random(H) > 0.4)/0.6 if regime=="dropout" else np.ones(H)
        Hd = Hh*keep
        o = 1/(1+np.exp(-(Hd @ p[2] + p[3]).ravel()))
        g = (o - y)/bs
        gH = np.outer(g, p[2].ravel())*keep*(1-Hh**2)
        p[0] -= lr*(X.T@gH + (0.004*np.sign(p[0]) if regime=="sparse" else 0))
        p[1] -= lr*gH.sum(0)
        p[2] -= lr*(Hd.T@g[:,None] + (0.004*np.sign(p[2]) if regime=="sparse" else 0))
        p[3] -= lr*g.sum()
    return p

def acc(p, n=3000):
    X, y = data(n, np.random.default_rng(999))
    return ((fwd(p, X)[1] > .5) == y).mean()

def mi_bits(y, Hs, fr):
    pat = ((Hs[:, fr] > 0) @ (1 << np.arange(len(fr)))).astype(int)
    I = 0.0
    for s in np.unique(pat):
        m = pat == s; ps = m.mean()
        for c in (0,1):
            pj = (m & (y==c)).mean()
            if pj > 0: I += pj*np.log2(pj/(ps*(y==c).mean()))
    return I

def redundancy(p, n=5000, f=5, reps=40):
    X,_ = data(n, np.random.default_rng(555)); y = (X[:,0]>0).astype(int)
    Hs,_ = fwd(p, X)
    v = [mi_bits(y,Hs,rng.choice(H,f,replace=False)) -
         mi_bits(rng.permutation(y),Hs,rng.choice(H,f,replace=False))
         for _ in range(reps)]
    return max(0.0, float(np.mean(v)))

def steps_to_forget(p, lr=0.05, cap=400):
    """gradient ASCENT on the task loss until accuracy < 0.6"""
    q = [w.copy() for w in p]
    r = np.random.default_rng(77)
    for s in range(cap):
        if acc(q, 1200) < 0.6: return s
        X, y = data(64, r)
        Hh = np.tanh(X @ q[0] + q[1])
        o = 1/(1+np.exp(-(Hh @ q[2] + q[3]).ravel()))
        g = (o - y)/64
        gH = np.outer(g, q[2].ravel())*(1-Hh**2)
        q[0] += lr*X.T@gH; q[1] += lr*gH.sum(0)     # ASCENT
        q[2] += lr*Hh.T@g[:,None]; q[3] += lr*g.sum()
    return cap

def spearman(a,b):
    ra=np.argsort(np.argsort(a))-0.0; rb=np.argsort(np.argsort(b))-0.0
    ra-=ra.mean(); rb-=rb.mean()
    return float((ra*rb).sum()/np.sqrt((ra**2).sum()*(rb**2).sum()))

rows=[]
print(f"{'regime':>8} {'seed':>4} {'acc':>6} {'R(bits)':>8} {'steps2forget':>13}")
for regime in ("sparse","plain","dropout"):
    for seed in range(4):
        p = train(regime, 200+seed); a = acc(p)
        if a < 0.95: print(f"{regime:>8} {seed:>4}  EXCLUDED"); continue
        R = redundancy(p); S = steps_to_forget(p)
        rows.append((regime,a,R,S))
        print(f"{regime:>8} {seed:>4} {a:>6.3f} {R:>8.3f} {S:>13}")
reg=np.array([r[0] for r in rows]); A=np.array([r[1] for r in rows])
R=np.array([r[2] for r in rows]); S=np.array([r[3] for r in rows],float)
u0 = S.max()/max(S.min(),1) >= 2
rho_R, rho_A = spearman(R,S), spearman(A,S)
mS = {g: S[reg==g].mean() for g in ("sparse","plain","dropout")}
print(f"\nU0 spread {S.max()/max(S.min(),1):.1f}x >= 2x: {u0}")
print(f"U1 rho(redundancy, steps-to-forget) = {rho_R:+.2f} (>=+0.7): {rho_R>=0.7}")
print(f"U2 beats accuracy: |{rho_R:+.2f}| > |{rho_A:+.2f}|: {abs(rho_R)>abs(rho_A)}")
print(f"U3 mean steps — sparse {mS['sparse']:.0f} | plain {mS['plain']:.0f} | "
      f"dropout {mS['dropout']:.0f}: {mS['dropout']>mS['sparse']}")
