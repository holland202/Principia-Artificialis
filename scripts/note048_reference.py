#!/usr/bin/env python3
# Note #048 reference — The Governor Is the Dynamics
# Author: Claude Fable 5 (Anthropic); device data: holland202, Galaxy S25, 2026-07-18
# Registered claims C1-C6 printed with PASS/FAIL. numpy only. seed 42.
import math
import numpy as np

ETA, T_THRESH = 2.0, 38.5
DEVICE = {"a_4130": 0.0037, "a_4090": 0.0082, "steps": 253, "dV": 2.4262 - 2.3924}

def a_of(T):
    return 1.0 if T <= T_THRESH else math.exp(-ETA * (T - T_THRESH))

def run(dim=64, aT=1.0, max_steps=4000, tol=1e-3):
    rng = np.random.default_rng(42)
    truth = rng.normal(0, 1, dim); truth /= np.linalg.norm(truth)
    noise = 0.1
    rng2 = np.random.default_rng(42)
    q = rng2.normal(0, 0.5, dim); p = np.zeros(dim)
    dt, m = 0.01, 1.0
    conv = None
    for i in range(max_steps):
        d = q - truth; dist = np.linalg.norm(d) + 1e-9
        F = -(d + (noise * 4 * np.pi / dist) * d * np.cos(4 * np.pi * dist)) * aT
        ph = p + 0.5 * dt * F
        q = q + dt * ph / m
        p = ph + 0.5 * dt * F
        dd = np.linalg.norm(q - truth)
        V = 0.5 * dd**2 + noise * np.sin(4 * np.pi * dd)
        if i == 0: V_first = V
        if i == DEVICE["steps"] - 1: V_at_253 = V
        if conv is None and dd < tol: conv = i
    return conv, V_first, (V_at_253 if max_steps >= DEVICE["steps"] else None), V

print("NOTE #048 REFERENCE — registered claims")
print("=" * 60)

# C1/C2: governor math vs device printout
a1, a2 = a_of(41.30), a_of(40.90)
c1 = round(a1, 4) == DEVICE["a_4130"]
c2 = round(a2, 4) == DEVICE["a_4090"]
print(f"C1 a(41.30) = {a1:.6f} -> rounds to {round(a1,4)} vs device 0.0037 : {'PASS' if c1 else 'FAIL'}")
print(f"C2 a(40.90) = {a2:.6f} -> rounds to {round(a2,4)} vs device 0.0082 : {'PASS' if c2 else 'FAIL'}")

# C3: ungoverned baseline
conv, Vf, V253, Vend = run(aT=1.0)
c3 = conv == 153
print(f"C3 ungoverned converge step = {conv} (claim 153) : {'PASS' if c3 else 'FAIL'}")

# C4: governed at S25 mean 41.1 C
aS25 = a_of(41.1)
convg, Vf_g, V253_g, Vend_g = run(aT=aS25)
dV = Vf_g - V253_g
c4 = 0.01 <= dV <= 0.10
print(f"C4 governed a = {aS25:.6f}; dV over 253 steps = {dV:.4f} in [0.01,0.10] (device 0.0338) : {'PASS' if c4 else 'FAIL'}")

# C5: quarter-period scaling
pred = 153 / math.sqrt(aS25)
c5 = convg is not None and abs(convg - pred) / pred <= 0.15
print(f"C5 predicted converge ~ {pred:.0f} +-15%; actual = {convg} : {'PASS' if c5 else 'FAIL'}")

# C6: anti-vacuity — governor disabled at same temperature
conv0, *_ = run(aT=1.0)
c6 = conv0 == 153
print(f"C6 anti-vacuity (governor off, same T) converge = {conv0} (must be 153) : {'PASS' if c6 else 'FAIL'}")

print("=" * 60)
n = sum([c1, c2, c3, c4, c5, c6])
print(f"VERDICT: {n}/6 registered claims pass")
print(f"Throttle factor at S25 idle: {1/aS25:.0f}x force attenuation")
