"""
Génération de tous les graphiques de la présentation à partir des fichiers logs réels.
Lit les CSV dans logs/edge_cloud, logs/full_fog_low, logs/full_fog_high
et produit les images dans le dossier plots_output/.

Usage: python generate_plots_from_logs.py
"""
import os
import csv
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 12

# === CONFIGURATION (relative to this script) ===
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "plots_output"

SCENARIOS = {
    'edge_cloud': {'label': 'Edge + Cloud\n(0% fog)', 'color': '#e74c3c', 'short': 'Edge+Cloud'},
    'full_fog_low': {'label': 'Low Fog\n(10% fog)', 'color': '#f39c12', 'short': 'Low Fog'},
    'full_fog_high': {'label': 'High Fog\n(50% fog)', 'color': '#27ae60', 'short': 'High Fog'},
}

def read_csv(scenario, filename):
    """Lit un fichier CSV et retourne les colonnes comme arrays numpy."""
    filepath = LOGS_DIR / scenario / filename
    if not filepath.exists():
        print(f"  [SKIP] {filepath} not found")
        return None
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for h in headers:
            data[h] = []
        for row in reader:
            # Filtrer pour ne garder que le régime permanent (Steady-State) de 50s à 300s
            try:
                if 'time' in row:
                    t = float(row['time'])
                    if t < 50.0 or t > 300.0:
                        continue
            except ValueError:
                pass
            
            for h in headers:
                try:
                    data[h].append(float(row[h]))
                except (ValueError, KeyError):
                    data[h].append(0.0)
    for h in headers:
        data[h] = np.array(data[h])
    return data


def compute_averages():
    """Calcule les moyennes de chaque métrique par scénario."""
    results = {}
    for sc in SCENARIOS:
        r = {}
        lat = read_csv(sc, 'latency.csv')
        if lat is not None:
            r['avg_latency'] = np.mean(lat['avg_weighted_ms'])
            r['edge_lat'] = np.mean(lat['edge_ms'])
            r['fog_lat'] = np.mean(lat['fog_ms'])
            r['cloud_lat'] = np.mean(lat['cloud_ms'])
        dist = read_csv(sc, 'distribution.csv')
        if dist is not None:
            r['edge_pct'] = np.mean(dist['edge_pct'])
            r['fog_pct'] = np.mean(dist['fog_pct'])
            r['cloud_pct'] = np.mean(dist['cloud_pct'])

        energy = read_csv(sc, 'energy.csv')
        if energy is not None:
            r['energy_total'] = np.mean(energy['energy_per_task_mJ'])
            r['energy_local'] = np.mean(energy['local_component_mJ'])
            r['energy_fog'] = np.mean(energy['fog_component_mJ'])
            r['energy_cloud'] = np.mean(energy['cloud_component_mJ'])

        cong = read_csv(sc, 'congestion.csv')
        if cong is not None:
            r['max_congestion'] = np.mean(cong['max_congestion_pct'])

        scoot = read_csv(sc, 'scoot_actions.csv')
        if scoot is not None:
            r['tl_adjusted'] = int(scoot['tl_adjusted_total'][-1])
            r['rerouted'] = int(scoot['rerouted_total'][-1])

        veh = read_csv(sc, 'vehicles.csv')
        if veh is not None:
            r['avg_vehicles'] = np.mean(veh['total_vehicles'])
            r['avg_fog_nodes'] = np.mean(veh['fog_nodes'])

        results[sc] = r
    return results


# ============================================================
# PLOT 1: Latence Moyenne par Scénario (bar chart)
# ============================================================
def plot1_latence_moyenne(avgs):
    fig, ax = plt.subplots(figsize=(10, 6))
    scenarios = list(SCENARIOS.keys())
    labels = [SCENARIOS[s]['short'] for s in scenarios]
    colors = [SCENARIOS[s]['color'] for s in scenarios]
    values = [avgs[s]['avg_latency'] for s in scenarios]

    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor='white', linewidth=2, alpha=0.9)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.1f} ms', ha='center', va='bottom', fontweight='bold', fontsize=14)

    ax.set_ylabel('Average Latency (ms)', fontweight='bold', fontsize=13)
    ax.set_title('Average Weighted Latency per Scenario', fontweight='bold', fontsize=15, pad=15)
    ax.set_ylim(0, max(values) * 1.2)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Reduction percentages
    baseline = values[0]
    for i, val in enumerate(values):
        if i > 0:
            reduction = ((baseline - val) / baseline) * 100
            # Si la barre est trop petite, on met le texte plus bas ou on réduit la police
            y_pos = max(val * 0.5, 5) # Au moins 5 pour ne pas être écrasé en bas
            ax.text(i, y_pos, f'-{reduction:.0f}%', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='white')

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot1_latence_moyenne.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 2: Évolution Latence dans le Temps (line chart)
# ============================================================
def plot2_evolution_latence():
    fig, ax = plt.subplots(figsize=(12, 6))
    for sc in SCENARIOS:
        lat = read_csv(sc, 'latency.csv')
        if lat is not None:
            # Smooth with rolling average (window=10)
            window = 10
            vals = lat['avg_weighted_ms']
            if len(vals) > window:
                smoothed = np.convolve(vals, np.ones(window)/window, mode='valid')
                t_smooth = lat['time'][window-1:]
            else:
                smoothed = vals
                t_smooth = lat['time']
            ax.plot(t_smooth, smoothed, label=SCENARIOS[sc]['short'],
                    color=SCENARIOS[sc]['color'], linewidth=2.5, alpha=0.9)

    ax.set_xlabel('Simulation Time (s)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Average Latency (ms)', fontweight='bold', fontsize=13)
    ax.set_title('Latency Evolution Over Time', fontweight='bold', fontsize=15, pad=15)
    ax.legend(fontsize=12, framealpha=0.9, loc='best')
    ax.grid(alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot2_evolution_latence.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 3: Distribution du Traitement (stacked bar)
# ============================================================
def plot3_distribution(avgs):
    fig, ax = plt.subplots(figsize=(10, 6))
    scenarios = list(SCENARIOS.keys())
    labels = [SCENARIOS[s]['short'] for s in scenarios]
    x = np.arange(len(scenarios))
    width = 0.5

    edge_vals = [avgs[s]['edge_pct'] for s in scenarios]
    fog_vals = [avgs[s]['fog_pct'] for s in scenarios]
    cloud_vals = [avgs[s]['cloud_pct'] for s in scenarios]

    ax.bar(x, edge_vals, width, label='Edge (Local)', color='#3498db', edgecolor='white', linewidth=0.5)
    ax.bar(x, fog_vals, width, bottom=edge_vals, label='Fog (RSU+Vehicles)',
           color='#2ecc71', edgecolor='white', linewidth=0.5)
    ax.bar(x, cloud_vals, width, bottom=[e+f for e,f in zip(edge_vals, fog_vals)],
           label='Cloud', color='#e74c3c', edgecolor='white', linewidth=0.5)

    # Add percentage labels on each segment
    for i in range(len(scenarios)):
        # Edge
        if edge_vals[i] > 5:
            ax.text(i, edge_vals[i]/2, f'{edge_vals[i]:.0f}%', ha='center', va='center',
                    fontweight='bold', fontsize=11, color='white')
        # Fog
        if fog_vals[i] > 5:
            ax.text(i, edge_vals[i] + fog_vals[i]/2, f'{fog_vals[i]:.0f}%', ha='center', va='center',
                    fontweight='bold', fontsize=11, color='white')
        # Cloud
        if cloud_vals[i] > 5:
            ax.text(i, edge_vals[i] + fog_vals[i] + cloud_vals[i]/2, f'{cloud_vals[i]:.0f}%',
                    ha='center', va='center', fontweight='bold', fontsize=11, color='white')

    ax.set_ylabel('Processing Distribution (%)', fontweight='bold', fontsize=13)
    ax.set_title('Processing Distribution per Scenario', fontweight='bold', fontsize=15, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=11, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot3_distribution.png'
    plt.savefig(out, dpi=200, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 4: Actions Fog (Traffic Lights + Rerouting)
# ============================================================
def plot4_actions_fog():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    for sc in SCENARIOS:
        scoot = read_csv(sc, 'scoot_actions.csv')
        if scoot is not None:
            ax1.plot(scoot['time'], scoot['tl_adjusted_total'],
                     label=SCENARIOS[sc]['short'], color=SCENARIOS[sc]['color'],
                     linewidth=2.5, alpha=0.9)
            ax2.plot(scoot['time'], scoot['rerouted_total'],
                     label=SCENARIOS[sc]['short'], color=SCENARIOS[sc]['color'],
                     linewidth=2.5, alpha=0.9)

    ax1.set_xlabel('Time (s)', fontweight='bold')
    ax1.set_ylabel('Cumulative TL Adjustments', fontweight='bold')
    ax1.set_title('Traffic Lights Adjusted', fontweight='bold', fontsize=14)
    ax1.legend(fontsize=10, framealpha=0.9)
    ax1.grid(alpha=0.3, linestyle='--')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    ax2.set_xlabel('Time (s)', fontweight='bold')
    ax2.set_ylabel('Cumulative Rerouted Vehicles', fontweight='bold')
    ax2.set_title('Vehicles Rerouted', fontweight='bold', fontsize=14)
    ax2.legend(fontsize=10, framealpha=0.9)
    ax2.grid(alpha=0.3, linestyle='--')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout(pad=2)
    out = OUTPUT_DIR / 'plot4_actions_fog.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 6: Latence par Composant (grouped bar)
# ============================================================
def plot6_latence_composant(avgs):
    fig, ax = plt.subplots(figsize=(10, 6))
    scenarios = list(SCENARIOS.keys())
    labels = [SCENARIOS[s]['short'] for s in scenarios]
    x = np.arange(len(scenarios))
    width = 0.2

    edge_lats = [avgs[s]['edge_lat'] for s in scenarios]
    fog_lats = [avgs[s]['fog_lat'] for s in scenarios]
    cloud_lats = [avgs[s]['cloud_lat'] for s in scenarios]

    ax.bar(x - width, edge_lats, width, label='Edge', color='#3498db', edgecolor='white')
    ax.bar(x, fog_lats, width, label='Fog', color='#2ecc71', edgecolor='white')
    ax.bar(x + width, cloud_lats, width, label='Cloud', color='#e74c3c', edgecolor='white')

    # Add value labels
    for i in range(len(scenarios)):
        ax.text(i - width, edge_lats[i] + 1, f'{edge_lats[i]:.0f}', ha='center', fontsize=10, fontweight='bold')
        if fog_lats[i] > 0:
            ax.text(i, fog_lats[i] + 1, f'{fog_lats[i]:.0f}', ha='center', fontsize=10, fontweight='bold')
        ax.text(i + width, cloud_lats[i] + 1, f'{cloud_lats[i]:.0f}', ha='center', fontsize=10, fontweight='bold')

    ax.set_ylabel('Latency (ms)', fontweight='bold', fontsize=13)
    ax.set_title('Latency Breakdown by Component', fontweight='bold', fontsize=15, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot6_latence_composant.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 7: Congestion (line chart over time)
# ============================================================
def plot7_congestion():
    fig, ax = plt.subplots(figsize=(12, 6))
    for sc in SCENARIOS:
        cong = read_csv(sc, 'congestion.csv')
        if cong is not None:
            # Smooth
            window = 10
            vals = cong['max_congestion_pct']
            if len(vals) > window:
                smoothed = np.convolve(vals, np.ones(window)/window, mode='valid')
                t_smooth = cong['time'][window-1:]
            else:
                smoothed = vals
                t_smooth = cong['time']
            ax.plot(t_smooth, smoothed, label=SCENARIOS[sc]['short'],
                    color=SCENARIOS[sc]['color'], linewidth=2.5, alpha=0.9)

    ax.axhline(y=60, color='#e74c3c', linestyle='--', alpha=0.5, linewidth=1.5, label='Seuil critique (60%)')
    ax.set_xlabel('Simulation Time (s)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Max Zone Congestion (%)', fontweight='bold', fontsize=13)
    ax.set_title('Congestion Evolution Over Time', fontweight='bold', fontsize=15, pad=15)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.set_ylim(0, 105)
    ax.grid(alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot7_congestion.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 8: Energy Comparison (stacked bar + reduction)
# ============================================================
def plot8_energy_comparison(avgs):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1.2, 1]})
    scenarios = list(SCENARIOS.keys())
    labels = [SCENARIOS[s]['label'] for s in scenarios]
    x = np.arange(len(scenarios))
    width = 0.55

    e_local = [avgs[s]['energy_local'] for s in scenarios]
    e_fog = [avgs[s]['energy_fog'] for s in scenarios]
    e_cloud = [avgs[s]['energy_cloud'] for s in scenarios]
    e_total = [avgs[s]['energy_total'] for s in scenarios]

    # Left: stacked bar
    colors_stack = ['#e74c3c', '#2ecc71', '#3498db']
    ax1.bar(x, e_local, width, label='Local Compute (0.5 J/MI)',
            color=colors_stack[0], alpha=0.9, edgecolor='white', linewidth=0.5)
    ax1.bar(x, e_fog, width, bottom=e_local, label='Fog Compute (0.1 J/MI)',
            color=colors_stack[1], alpha=0.9, edgecolor='white', linewidth=0.5)
    ax1.bar(x, e_cloud, width, bottom=[l+f for l,f in zip(e_local, e_fog)],
            label='Cloud Transmit', color=colors_stack[2], alpha=0.9, edgecolor='white', linewidth=0.5)

    for i, total in enumerate(e_total):
        ax1.text(i, total + 5, f'{total:.0f} mJ', ha='center', va='bottom',
                 fontweight='bold', fontsize=13, color='#2c3e50')

    ax1.set_ylabel('Energy per Task (mJ)', fontweight='bold', fontsize=13)
    ax1.set_title('Energy Breakdown by Processing Tier', fontweight='bold', fontsize=14, pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=11)
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax1.set_ylim(0, max(e_total) * 1.15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Right: total comparison with reduction
    colors_bar = ['#e74c3c', '#f39c12', '#27ae60']
    bars = ax2.bar(x, e_total, width=0.5, color=colors_bar, alpha=0.9,
                   edgecolor='white', linewidth=1.5)

    baseline = e_total[0]
    for i, (total, bar) in enumerate(zip(e_total, bars)):
        if i == 0:
            ax2.text(i, total + 5, f'{total:.0f} mJ\n(baseline)', ha='center', va='bottom',
                     fontweight='bold', fontsize=12, color='#e74c3c')
        else:
            reduction = ((baseline - total) / baseline) * 100
            ax2.text(i, total + 5, f'{total:.0f} mJ\n-{reduction:.0f}%', ha='center', va='bottom',
                     fontweight='bold', fontsize=12, color='#27ae60')

    ax2.set_ylabel('Total Energy per Task (mJ)', fontweight='bold', fontsize=13)
    ax2.set_title('Energy Reduction by Scenario', fontweight='bold', fontsize=14, pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=11)
    ax2.set_ylim(0, max(e_total) * 1.25)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout(pad=2)
    out = OUTPUT_DIR / 'plot8_energy_comparison.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 9: KPI — Task Completion Rate & Deadline Miss Ratio (bar)
# ============================================================
def plot9_kpi_rates(avgs):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    scenarios = [s for s in SCENARIOS.keys() if s != 'edge_cloud']
    labels = [SCENARIOS[s]['short'] for s in scenarios]
    colors = [SCENARIOS[s]['color'] for s in scenarios]
    x = np.arange(len(scenarios))

    # Task Completion Rate
    tcr_vals = [avgs[s].get('task_completion_rate', 100.0) for s in scenarios]
    bars1 = ax1.bar(x, tcr_vals, 0.5, color=colors, alpha=0.9, edgecolor='white', linewidth=2)
    for bar, val in zip(bars1, tcr_vals):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Task Completion Rate (%)', fontweight='bold', fontsize=13)
    ax1.set_title('Task Completion Rate', fontweight='bold', fontsize=14, pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=12)
    ax1.set_ylim(0, 110)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Deadline Miss Ratio
    dmr_vals = [avgs[s].get('deadline_miss_ratio', 0.0) for s in scenarios]
    bars2 = ax2.bar(x, dmr_vals, 0.5, color=colors, alpha=0.9, edgecolor='white', linewidth=2)
    for bar, val in zip(bars2, dmr_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=13)
    ax2.set_ylabel('Deadline Miss Ratio (%)', fontweight='bold', fontsize=13)
    ax2.set_title('Deadline Miss Ratio (>100ms)', fontweight='bold', fontsize=14, pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=12)
    ax2.set_ylim(0, max(dmr_vals) * 1.3 if max(dmr_vals) > 0 else 10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout(pad=2)
    out = OUTPUT_DIR / 'plot9_kpi_rates.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 10: KPI — Resource Utilization (grouped bar)
# ============================================================
def plot10_resource_utilization(avgs):
    fig, ax = plt.subplots(figsize=(10, 6))
    scenarios = [s for s in SCENARIOS.keys() if s != 'edge_cloud']
    labels = [SCENARIOS[s]['short'] for s in scenarios]
    x = np.arange(len(scenarios))
    width = 0.3

    rsu_vals = [avgs[s].get('rsu_utilization', 0.0) for s in scenarios]
    fogv_vals = [avgs[s].get('fogv_utilization', 0.0) for s in scenarios]

    bars1 = ax.bar(x - width/2, rsu_vals, width, label='RSU (5000 MIPS)',
                   color='#3498db', alpha=0.9, edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x + width/2, fogv_vals, width, label='Fog Vehicles (1500 MIPS)',
                   color='#2ecc71', alpha=0.9, edgecolor='white', linewidth=1.5)

    for bar, val in zip(bars1, rsu_vals):
        if val > 1:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar, val in zip(bars2, fogv_vals):
        if val > 1:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Resource Utilization (%)', fontweight='bold', fontsize=13)
    ax.set_title('Resource Utilization — RSU vs Fog Vehicles', fontweight='bold', fontsize=15, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim(0, max(max(rsu_vals), max(fogv_vals)) * 1.3 if max(max(rsu_vals), max(fogv_vals)) > 0 else 10)
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot10_resource_utilization.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 11: KPI — Throughput Evolution (line chart)
# ============================================================
def plot11_throughput():
    fig, ax = plt.subplots(figsize=(12, 6))
    for sc in SCENARIOS:
        kpi = read_csv(sc, 'kpi.csv')
        if kpi is not None and 'throughput_mbps' in kpi:
            window = 10
            vals = kpi['throughput_mbps']
            if len(vals) > window:
                smoothed = np.convolve(vals, np.ones(window)/window, mode='valid')
                t_smooth = kpi['time'][window-1:]
            else:
                smoothed = vals
                t_smooth = kpi['time']
            ax.plot(t_smooth, smoothed, label=SCENARIOS[sc]['short'],
                    color=SCENARIOS[sc]['color'], linewidth=2.5, alpha=0.9)

    ax.set_xlabel('Simulation Time (s)', fontweight='bold', fontsize=13)
    ax.set_ylabel('System Throughput (Mb/s)', fontweight='bold', fontsize=13)
    ax.set_title('Global System Throughput Over Time', fontweight='bold', fontsize=15, pad=15)
    ax.legend(fontsize=12, framealpha=0.9)
    ax.grid(alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot11_throughput.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# PLOT 12: KPI — Deadline Miss Evolution (line chart)
# ============================================================
def plot12_deadline_miss_evolution():
    fig, ax = plt.subplots(figsize=(12, 6))
    for sc in SCENARIOS:
        if sc == 'edge_cloud':
            continue
        kpi = read_csv(sc, 'kpi.csv')
        if kpi is not None and 'deadline_miss_ratio_pct' in kpi:
            window = 10
            vals = kpi['deadline_miss_ratio_pct']
            if len(vals) > window:
                smoothed = np.convolve(vals, np.ones(window)/window, mode='valid')
                t_smooth = kpi['time'][window-1:]
            else:
                smoothed = vals
                t_smooth = kpi['time']
            ax.plot(t_smooth, smoothed, label=SCENARIOS[sc]['short'],
                    color=SCENARIOS[sc]['color'], linewidth=2.5, alpha=0.9)

    ax.axhline(y=5, color='#e74c3c', linestyle='--', alpha=0.5, linewidth=1.5, label='Target (<5%)')
    ax.set_xlabel('Simulation Time (s)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Deadline Miss Ratio (%)', fontweight='bold', fontsize=13)
    ax.set_title('Deadline Miss Ratio Over Time (100ms Threshold)', fontweight='bold', fontsize=15, pad=15)
    ax.legend(fontsize=12, framealpha=0.9)
    ax.grid(alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out = OUTPUT_DIR / 'plot12_deadline_miss_evolution.png'
    plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] {out.name}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("  Generating all plots from simulation logs")
    print("=" * 60)
    print(f"  Logs: {LOGS_DIR}")
    print(f"  Output: {OUTPUT_DIR}")
    print()

    # Check all scenario dirs exist
    for sc in SCENARIOS:
        sc_dir = LOGS_DIR / sc
        if not sc_dir.exists():
            print(f"  [WARNING] Missing scenario logs: {sc_dir}")

    # Compute averages
    avgs = compute_averages()

    # Add KPI averages
    for sc in SCENARIOS:
        kpi = read_csv(sc, 'kpi.csv')
        if kpi is not None and 'task_completion_rate_pct' in kpi and len(kpi['task_completion_rate_pct']) > 0:
            avgs[sc]['task_completion_rate'] = float(np.nan_to_num(np.mean(kpi['task_completion_rate_pct'])))
            avgs[sc]['deadline_miss_ratio'] = float(np.nan_to_num(np.mean(kpi['deadline_miss_ratio_pct'])))
            avgs[sc]['rsu_utilization'] = float(np.nan_to_num(np.mean(kpi['rsu_utilization_pct'])))
            avgs[sc]['fogv_utilization'] = float(np.nan_to_num(np.mean(kpi['fogv_utilization_pct'])))
            avgs[sc]['throughput'] = float(np.nan_to_num(np.mean(kpi['throughput_mbps'])))
        else:
            avgs[sc]['task_completion_rate'] = 100.0
            avgs[sc]['deadline_miss_ratio'] = 0.0
            avgs[sc]['rsu_utilization'] = 0.0
            avgs[sc]['fogv_utilization'] = 0.0
            avgs[sc]['throughput'] = 0.0

    # Print summary
    print("\n--- Computed averages from logs ---")
    for sc in SCENARIOS:
        r = avgs[sc]
        print(f"\n  {SCENARIOS[sc]['short']}:")
        print(f"    Avg latency: {r.get('avg_latency', 0):.1f} ms")
        print(f"    Distribution: Edge={r.get('edge_pct', 0):.0f}% Fog={r.get('fog_pct', 0):.0f}% Cloud={r.get('cloud_pct', 0):.0f}%")
        print(f"    Energy: {r.get('energy_total', 0):.0f} mJ (local={r.get('energy_local', 0):.0f}, fog={r.get('energy_fog', 0):.0f}, cloud={r.get('energy_cloud', 0):.0f})")
        print(f"    TL adjusted: {r.get('tl_adjusted', 0)}, Rerouted: {r.get('rerouted', 0)}")
        print(f"    KPI: TCR={r.get('task_completion_rate', 0):.1f}% DMR={r.get('deadline_miss_ratio', 0):.1f}% RSU={r.get('rsu_utilization', 0):.1f}% FogV={r.get('fogv_utilization', 0):.1f}% Throughput={r.get('throughput', 0):.3f} Mb/s")
    print()

    # Generate all plots
    plot1_latence_moyenne(avgs)
    plot2_evolution_latence()
    plot3_distribution(avgs)
    plot4_actions_fog()
    plot6_latence_composant(avgs)
    plot7_congestion()
    plot8_energy_comparison(avgs)
    plot9_kpi_rates(avgs)
    plot10_resource_utilization(avgs)
    plot11_throughput()
    plot12_deadline_miss_evolution()

    print(f"\n==> 11 plots generated in {OUTPUT_DIR}/")
    print("    (plot5_architecture.png is unchanged - architecture diagram)")

