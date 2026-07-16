import matplotlib.pyplot as plt
import csv
import datetime

log_file = "data/thermal_metrics.log"
timestamps = []
temps = []
recoveries = []

try:
    with open(log_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            timestamps.append(datetime.datetime.fromtimestamp(float(row[0])))
            temps.append(float(row[1]))
            recoveries.append(float(row[2]))
            
    fig, ax1 = plt.subplots(figsize=(10, 5))

    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Peak Temp Exceedance (°C)', color=color)
    ax1.plot(timestamps, temps, marker='o', color=color, linestyle='-', linewidth=2, label='Peak Temp')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(y=38.5, color='black', linestyle='--', label='Thermal Ceiling (38.5°C)')

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Recovery Time (seconds)', color=color)
    ax2.bar(timestamps, recoveries, width=0.0001, alpha=0.5, color=color, label='Recovery Duration')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Veritas Gate: Thermal Manifold Relaxation (Exp #003)')
    fig.tight_layout()
    
    output_path = "figures/thermal_relaxation_exp003.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph generated successfully: {output_path}")

except FileNotFoundError:
    print(f"Log file not found at {log_file}")
except Exception as e:
    print(f"Error plotting data: {e}")
