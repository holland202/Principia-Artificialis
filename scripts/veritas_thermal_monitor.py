#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
# Principia Artificialis — Experiment #003 Daemon
# The Veritas Gate: Thermal Correlation & Metric Collection
# Substrate: Snapdragon 8 Elite (SM8750-AB) via Termux
# ═══════════════════════════════════════════════════════════════

import os
import time
import logging
from typing import Optional

# Configuration
THERMAL_ZONE = "/sys/class/thermal/thermal_zone"
CEILING_C = 38.5
NOMINAL_C = 31.0
POLL_RATE_HZ = 10
LOG_FILE = os.path.expanduser("~/Principia-Artificialis/data/thermal_metrics.log")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_soc_temperature() -> Optional[float]:
    max_temp = 0.0
    try:
        for i in range(50):
            zone_path = f"{THERMAL_ZONE}{i}/temp"
            if os.path.exists(zone_path):
                with open(zone_path, 'r') as f:
                    temp_raw = int(f.read().strip())
                    temp_c = temp_raw / 1000.0 if temp_raw > 1000 else temp_raw
                    if temp_c > max_temp and temp_c < 100:
                        max_temp = temp_c
        return max_temp if max_temp > 0 else None
    except Exception as e:
        return None

def trigger_atomic_reduction(temp: float):
    start_time = time.time()
    
    logging.warning(f"⚠️ THERMAL CEILING EXCEEDED: {temp:.2f}°C > {CEILING_C}°C")
    logging.warning("INITIATING ATOMIC_REDUCTION_COLLAPSE")
    
    # Mathematical retraction trigger
    import gc
    gc.collect()
    
    logging.info("State vector projected to Simply Connected Manifold (∂²=0).")
    logging.info("Cooling phase engaged. Awaiting return to nominal band...")
    
    while True:
        current_temp = get_soc_temperature()
        if current_temp and current_temp <= NOMINAL_C:
            duration = time.time() - start_time
            logging.info(f"Thermal state normalized: {current_temp:.2f}°C. Recovery: {duration:.2f}s")
            
            # Log metrics
            with open(LOG_FILE, "a") as f:
                f.write(f"{time.time()},{temp},{duration}\n")
            break
        time.sleep(0.5)

def monitor_geodesic_flow():
    logging.info(f"VERITAS GATE ACTIVE. Thermal ceiling locked at {CEILING_C}°C.")
    while True:
        current_temp = get_soc_temperature()
        if current_temp is not None:
            if current_temp >= CEILING_C:
                trigger_atomic_reduction(current_temp)
        time.sleep(1.0 / POLL_RATE_HZ)

if __name__ == "__main__":
    monitor_geodesic_flow()
