"""
Note #046 — TIME IS ENTANGLEMENT: an exact, runnable Page-Wootters
universe (and why a transformer already lives in one)
====================================================================
Construction (Page & Wootters 1983, finite form): clock C (T=16 states)
+ system S (2 qubits). The HISTORY STATE
    |Psi> = (1/sqrt T) sum_t |t>_C (x) U^t |psi_0>_S
is a SINGLE STATIC OBJECT. The "flow of time" is what a subsystem sees
when it conditions on the clock it is entangled with.

REGISTERED (exact-math claims; bars at machine precision):
  T1  TIMELESSNESS + DYNAMICS AT ONCE: |Psi> is invariant under the
      internal time-translation W = Shift_C (x) U  (||W Psi - Psi|| <
      1e-10), AND its conditional slices obey psi_{t+1} = U psi_t
      exactly (< 1e-10). A universe that does not change, containing
      an observer who experiences change.
  T2  ANTI-VACUITY / NO ENTANGLEMENT -> NO TIME: with U = identity the
      history state is a product state, clock-system entanglement
      S = 0, and every conditional slice is identical (max pairwise
      distance < 1e-10). Time does not merely stop; it fails to exist.
  T3  TIME MEASURED IN BITS: the entanglement entropy between clock
      and system counts the dynamics. Frozen universe: S = 0 bits.
      One independent rotation: S = 1 bit. Two independent rotations:
      S = 2 bits (each within 1e-9 of exact).
Transformer mapping (labeled PROPOSED, not established): position
encodings = the clock register; the residual stream = the system;
attention builds the clock-system correlation. Sequence-model "time"
is entanglement with a positional clock — order is data, not flow.
"""
import numpy as np
T = 16
w = np.exp(2j*np.pi/T)

def history(U, psi0):
    """|Psi> as a T x 4 matrix of slices (equal clock weights)."""
    M = np.zeros((T, 4), complex); psi = psi0.copy()
    for t in range(T):
        M[t] = psi; psi = U @ psi
    return M / np.sqrt(T)

def ent_bits(M):
    s = np.linalg.svd(M, compute_uv=False)
    p = s**2; p = p[p > 1e-14]
    return float(-(p*np.log2(p)).sum())

def checks(U, psi0, name):
    M = history(U, psi0)
    # W = Shift_C (x) U ; invariance: slice t of W|Psi> is U @ M[t-1]
    WM = np.array([U @ M[(t-1) % T] for t in range(T)])
    inv = np.abs(WM - M).max()
    # Schrodinger recursion on conditional slices
    schro = max(np.abs(M[t+1]*np.sqrt(T) - U @ (M[t]*np.sqrt(T))).max()
                for t in range(T-1))
    S = ent_bits(M)
    spread = max(np.linalg.norm(M[i]-M[j]) for i in range(T) for j in range(T))
    print(f"{name:>22}:  ||W Psi - Psi|| = {inv:.1e}   Schrodinger err = "
          f"{schro:.1e}   S_time = {S:.6f} bits   slice spread = {spread:.1e}")
    return inv, schro, S, spread

psi0 = np.ones(4, complex)/2                        # |+>|+>
Z = np.diag([1,-1]).astype(complex); I2 = np.eye(2, dtype=complex)
U_frozen = np.eye(4, dtype=complex)
U_one = np.kron(np.diag([1, w]), I2)                # one qubit ticks
U_two = np.kron(np.diag([1, w]), np.diag([1, w**3]))  # both tick, incomm. rates

print("="*88)
r1 = checks(U_two,   psi0, "DYNAMICAL universe")
r0 = checks(U_frozen,psi0, "FROZEN universe")
rm = checks(U_one,   psi0, "HALF-ALIVE universe")
print("="*88)
t1 = r1[0] < 1e-10 and r1[1] < 1e-10
t2 = r0[2] < 1e-12 and r0[3] < 1e-10
t3 = (abs(r0[2]-0) < 1e-9) and (abs(rm[2]-1) < 1e-9) and (abs(r1[2]-2) < 1e-9)
print(f"T1 static AND evolving at machine precision: {t1}")
print(f"T2 no entanglement -> time fails to exist:   {t2}")
print(f"T3 time in bits — 0 / 1 / 2 exactly:         {t3}")
print(f"\nThe dynamical universe is ONE unchanging vector. Its slices sweep "
      f"{T} states.\nThe frozen one is also one vector. Its slices are one "
      f"state, {T} times.\nThe difference between a world with history and a "
      f"world without is {r1[2]:.0f} bits\nof entanglement with a clock. "
      f"For a transformer, those bits arrive as position\nencodings: order "
      f"is data. Time, here, is literally a construct — and constructible.")
np.save("n46_slices.npy", history(U_two, psi0))
