#!/usr/bin/env python3
"""
Experiment Harness for Note #050 — Seasonal Memory Governance
Author: Grok / xAI

This is a lightweight, fully self-contained simulation of the idea in Note #050.
It does NOT claim to be a real thermal experiment yet — it is a controlled
toy model that lets us register predictions and later replace the temperature
source with real device readings.

Run:
    python experiments/exp050_seasonal_capacity_harness.py
"""

import numpy as np
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

@dataclass
class CacheState:
    size: int
    useful_hits: int
    stale_evictions: int
    peak_size: int

class SeasonalLRU:
    """Minimal LRU that respects a dynamic capacity schedule."""
    def __init__(self, initial_capacity: int = 1000):
        self.capacity = initial_capacity
        self.store = OrderedDict()
        self.useful_hits = 0
        self.stale_evictions = 0
        self.peak_size = 0

    def set_capacity(self, new_cap: int):
        self.capacity = max(10, new_cap)
        while len(self.store) > self.capacity:
            key, meta = self.store.popitem(last=False)
            if meta.get("useful", False):
                self.stale_evictions += 1

    def put(self, key: str, value, useful: bool = False):
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = {"value": value, "useful": useful}
        while len(self.store) > self.capacity:
            k, meta = self.store.popitem(last=False)
            if meta.get("useful", False):
                self.stale_evictions += 1
        self.peak_size = max(self.peak_size, len(self.store))

    def get(self, key: str):
        if key in self.store:
            self.store.move_to_end(key)
            if self.store[key].get("useful", False):
                self.useful_hits += 1
            return self.store[key]["value"]
        return None

    def state(self) -> CacheState:
        return CacheState(
            size=len(self.store),
            useful_hits=self.useful_hits,
            stale_evictions=self.stale_evictions,
            peak_size=self.peak_size,
        )

def capacity_schedule(hour: float, temp_c: float,
                      C_min=200, C_max=5000,
                      T_crit=38.5, delta_T=3.0) -> int:
    """Same formula as Note #050."""
    f_season = 0.15 + 0.85 * (0.5 + 0.5 * np.sin(2 * np.pi * (hour - 8) / 24))
    thermal = 1.0 / (1.0 + np.exp(-(T_crit - temp_c) / delta_T))
    return int(C_min + (C_max - C_min) * thermal * f_season)

def run_scenario(name: str, hours: list, temps: list, n_ops: int = 800):
    cache = SeasonalLRU(initial_capacity=1000)
    rng = np.random.default_rng(42)

    for h, t in zip(hours, temps):
        cap = capacity_schedule(h, t)
        cache.set_capacity(cap)

        for i in range(n_ops // len(hours)):
            key = f"k{rng.integers(0, 300)}"
            useful = rng.random() < 0.35
            if rng.random() < 0.6:
                cache.put(key, rng.normal(), useful=useful)
            else:
                cache.get(key)

    st = cache.state()
    print(f"\n=== {name} ===")
    print(f"Final size          : {st.size}")
    print(f"Peak size           : {st.peak_size}")
    print(f"Useful hits         : {st.useful_hits}")
    print(f"Useful evictions    : {st.stale_evictions}")
    return st

def main():
    print("Note #050 Experimental Harness — Seasonal + Thermal Capacity")
    print("All numbers below are produced by this script.\n")

    # Scenario A: Constant cool temperature, full day
    hours = list(np.linspace(0, 23, 12))
    cool  = [32.0] * 12
    st_cool = run_scenario("Cool constant (32°C)", hours, cool)

    # Scenario B: Realistic hot day
    hot = [30, 32, 35, 38, 41, 42, 40, 38, 36, 34, 32, 31]
    st_hot = run_scenario("Hot day curve", hours, hot)

    # Scenario C: Night-focused low capacity
    night_heavy = [28, 27, 27, 28, 30, 33, 36, 38, 37, 34, 31, 29]
    st_night = run_scenario("Night-emphasised", hours, night_heavy)

    print("\n--- Summary ---")
    print(f"Cool peak size     : {st_cool.peak_size}")
    print(f"Hot  peak size     : {st_hot.peak_size}")
    print(f"Night peak size    : {st_night.peak_size}")
    print("\nRegistered prediction (for later real-device tests):")
    print("  Joint seasonal+thermal schedule should improve useful-hit / peak-memory ratio")
    print("  compared with constant high capacity under thermal stress.")
    print("\nVincit Omnia Veritas")

if __name__ == "__main__":
    main()
