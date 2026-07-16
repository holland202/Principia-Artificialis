#!/usr/bin/env python3
"""
Exp #001: Entropy Production Monitoring Protocol
Contribution by Perplexity
Standalone, append-only experiment script that logs SoC temperature and a Gibbs-inspired proxy.
"""

import csv
import gc
import time
from datetime import datetime, timezone
import os

# Configurable parameters
THERMAL_CEILING_C = float(os.getenv("THERMAL_CEILING_C", "38.5"))
SAMPLE_INTERVAL_S = float(os.getenv("SAMPLE_INTERVAL_S", "2.0"))
OUT_CSV = os.getenv("OUT_CSV", "data/exp001_entropy_log.csv")

def poll_soc_temperature():
    """Attempt common thermal zone paths used on Linux/Android. Fallback to deterministic nominal."""
    paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/class/thermal/thermal_zone2/temp",
    ]
    for path in paths:
        try:
            with open(path, "r") as f:
                raw = f.read().strip()
            temp = int(raw)
            return temp / 1000.0 if temp > 1000 else float(temp)
        except Exception:
            continue
    # deterministic fallback for simulation or unsupported environment
    return 34.2

def calculate_gibbs_proxy(temp_c, delta_h=120.0, delta_s=0.35, lambda_hope=0.05):
    """Simple Gibbs-like proxy: ΔG = ΔH - T(ΔS + λ)."""
    temp_k = temp_c + 273.15
    return delta_h - temp_k * (delta_s + lambda_hope)

def ensure_data_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def main():
    ensure_data_dir(OUT_CSV)
    # Append header only if file doesn't exist
    header_needed = not os.path.exists(OUT_CSV)
    with open(OUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["timestamp_utc", "temp_c", "delta_g_proxy", "state", "event"])
            f.flush()
        try:
            while True:
                temp_c = poll_soc_temperature()
                delta_g = calculate_gibbs_proxy(temp_c)
                event = ""
                state = "stable"
                if temp_c >= THERMAL_CEILING_C:
                    state = "critical"
                    event = "thermal_ceiling_breach"
                    gc.collect()
                    time.sleep(5)
                elif delta_g > 0:
                    state = "warning"
                    event = "delta_g_positive"
                    time.sleep(2)
                else:
                    state = "stable"
                ts = datetime.now(timezone.utc).isoformat()
                writer.writerow([ts, f"{temp_c:.2f}", f"{delta_g:.4f}", state, event])
                f.flush()
                print(f"{ts} | T={temp_c:.2f}C | ΔG={delta_g:.4f} | {state} {event}")
                time.sleep(SAMPLE_INTERVAL_S)
        except KeyboardInterrupt:
            print("\n[TERMINATE] monitoring halted by user.")

if __name__ == "__main__":
    main()
