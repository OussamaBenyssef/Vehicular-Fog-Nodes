# -*- coding: utf-8 -*-
"""
Generate plot images for the Beamer presentation.
Images WITHOUT TITLE (title is in the Beamer frame) and compact.
Run: python generate_plots.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Theme colors
RED = '#DC2626'
GREEN = '#16A34A'
BLUE = '#2563EB'
YELLOW = '#CA8A04'
PURPLE = '#7C3AED'

# Global style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

# ============================================================
# PLOT 1: Average Latency per Scenario
# ============================================================
def plot1_latence_moyenne():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    scenarios = ['Edge+Cloud\n(0% fog)', 'Low Fog\n(10%)', 'High Fog\n(50%)']
    latences = [90, 35, 18]
    colors = [RED, YELLOW, GREEN]
    
    bars = ax.bar(scenarios, latences, color=colors, width=0.5, edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, latences):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val} ms', ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    ax.set_ylabel('Average Latency (ms)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 115)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.annotate('-61%', xy=(1, 35), xytext=(0.5, 65),
                fontsize=12, fontweight='bold', color=YELLOW,
                arrowprops=dict(arrowstyle='->', color=YELLOW, lw=2),
                ha='center')
    ax.annotate('-80%', xy=(2, 18), xytext=(1.5, 55),
                fontsize=12, fontweight='bold', color=GREEN,
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2),
                ha='center')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot1_latence_moyenne.png'))
    plt.close()
    print("[OK] plot1_latence_moyenne.png")

# ============================================================
# PLOT 2: Latency Evolution vs Number of Vehicles
# ============================================================
def plot2_evolution_latence():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    vehicules = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    edge_cloud = [60, 70, 78, 82, 85, 88, 90, 92, 95]
    low_fog = [20, 25, 28, 30, 32, 34, 35, 37, 38]
    high_fog = [12, 14, 15, 16, 17, 17, 18, 18, 19]
    
    ax.plot(vehicules, edge_cloud, color=RED, marker='s', markersize=7, linewidth=2.5,
            label='Edge+Cloud (0% fog)', markerfacecolor=RED)
    ax.plot(vehicules, low_fog, color=YELLOW, marker='^', markersize=7, linewidth=2.5,
            label='Low Fog (10%)', markerfacecolor=YELLOW)
    ax.plot(vehicules, high_fog, color=GREEN, marker='o', markersize=7, linewidth=2.5,
            label='High Fog (50%)', markerfacecolor=GREEN)
    
    ax.set_xlabel('Number of vehicles on the network', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Latency (ms)', fontsize=12, fontweight='bold')
    ax.set_xlim(5, 45)
    ax.set_ylim(0, 110)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.fill_between(vehicules, high_fog, edge_cloud, alpha=0.08, color=GREEN)
    ax.annotate('Fog Gain', xy=(30, 53), fontsize=11, color=GREEN,
                fontstyle='italic', ha='center')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot2_evolution_latence.png'))
    plt.close()
    print("[OK] plot2_evolution_latence.png")

# ============================================================
# PLOT 3: Processing Distribution (Stacked Bar)
# ============================================================
def plot3_distribution():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    scenarios = ['Edge+Cloud\n(0% fog)', 'Low Fog\n(10%)', 'High Fog\n(50%)']
    edge_pct = [65, 25, 20]
    fog_pct = [0, 55, 72]
    cloud_pct = [35, 20, 8]
    
    x = np.arange(len(scenarios))
    width = 0.45
    
    bars1 = ax.bar(x, edge_pct, width, label='Edge (local)', color=GREEN, edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x, fog_pct, width, bottom=edge_pct, label='Fog (RSU + V2V)', color=BLUE, edgecolor='white', linewidth=1.5)
    bars3 = ax.bar(x, cloud_pct, width, bottom=[e+f for e,f in zip(edge_pct, fog_pct)],
                   label='Cloud', color=RED, edgecolor='white', linewidth=1.5)
    
    for i, (e, f, c) in enumerate(zip(edge_pct, fog_pct, cloud_pct)):
        if e > 5:
            ax.text(i, e/2, f'{e}%', ha='center', va='center', fontweight='bold', color='white', fontsize=12)
        if f > 5:
            ax.text(i, e + f/2, f'{f}%', ha='center', va='center', fontweight='bold', color='white', fontsize=12)
        if c > 5:
            ax.text(i, e + f + c/2, f'{c}%', ha='center', va='center', fontweight='bold', color='white', fontsize=12)
    
    ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.set_ylim(0, 110)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3, fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot3_distribution.png'))
    plt.close()
    print("[OK] plot3_distribution.png")

# ============================================================
# PLOT 4: Fog Actions (Adjusted Lights + Rerouted Vehicles)
# ============================================================
def plot4_actions_fog():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    scenarios = ['Edge+Cloud\n(0% fog)', 'Low Fog\n(10%)', 'High Fog\n(50%)']
    feux = [0, 18, 360]
    reroutes = [0, 445, 2077]
    
    x = np.arange(len(scenarios))
    width = 0.3
    
    bars1 = ax.bar(x - width/2, feux, width, label='Adjusted lights (SCOOT)', color=BLUE, edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x + width/2, reroutes, width, label='Rerouted vehicles', color=YELLOW, edgecolor='white', linewidth=1.5)
    
    for bar, val in zip(bars1, feux):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                    str(val), ha='center', va='bottom', fontweight='bold', fontsize=11, color=BLUE)
    for bar, val in zip(bars2, reroutes):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                    str(val), ha='center', va='bottom', fontweight='bold', fontsize=11, color=YELLOW)
    
    ax.set_ylabel('Number of actions', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.set_ylim(0, 2500)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot4_actions_fog.png'))
    plt.close()
    print("[OK] plot4_actions_fog.png")

# ============================================================
# PLOT 5: 3-Tier Architecture (Diagram)
# ============================================================
def plot5_architecture():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # Cloud layer
    cloud = plt.Rectangle((1, 5.5), 10, 1.3, facecolor='#FEE2E2', edgecolor=RED, linewidth=2, 
                           joinstyle='round', zorder=2)
    ax.add_patch(cloud)
    ax.text(6, 6.35, 'CLOUD', fontsize=16, fontweight='bold', ha='center', va='center', color=RED)
    ax.text(6, 5.9, '20,000 MIPS  |  250 ms  |  5/10 Mbps', fontsize=10, ha='center', va='center', color='#666')
    
    # Fog layer
    fog = plt.Rectangle((1, 3), 10, 1.6, facecolor='#DBEAFE', edgecolor=BLUE, linewidth=2,
                         joinstyle='round', zorder=2)
    ax.add_patch(fog)
    ax.text(6, 4.05, 'FOG (RSU + Fog-Capable Vehicles)', fontsize=14, fontweight='bold',
            ha='center', va='center', color=BLUE)
    ax.text(6, 3.55, 'RSU: 5,000 MIPS, 7-15ms  |  V2V: 1,500 MIPS, 5-20ms', fontsize=10,
            ha='center', va='center', color='#666')
    ax.text(6, 3.2, 'V2I: 20 Mbps  |  V2V: 10 Mbps  |  Range: 100-300m', fontsize=9,
            ha='center', va='center', color='#999')
    
    # Edge layer  
    edge = plt.Rectangle((1, 0.5), 10, 1.6, facecolor='#DCFCE7', edgecolor=GREEN, linewidth=2,
                          joinstyle='round', zorder=2)
    ax.add_patch(edge)
    ax.text(6, 1.55, 'EDGE (Vehicles)', fontsize=14, fontweight='bold',
            ha='center', va='center', color=GREEN)
    ax.text(6, 1.05, '500 MIPS  |  3 ms  |  Local processing', fontsize=10,
            ha='center', va='center', color='#666')
    ax.text(6, 0.7, '2,000 veh/h  |  CPU: 20-80%  |  Tasks: 0.5-5 Mb', fontsize=9,
            ha='center', va='center', color='#999')
    
    # Arrows
    ax.annotate('', xy=(4, 3), xytext=(4, 2.1),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5))
    ax.text(3.3, 2.55, 'V2I / V2V', fontsize=9, color='#666', fontstyle='italic')
    
    ax.annotate('', xy=(8, 3), xytext=(8, 2.1),
                arrowprops=dict(arrowstyle='<-', color=GREEN, lw=2.5))
    ax.text(8.3, 2.55, 'Response', fontsize=9, color='#666', fontstyle='italic')
    
    ax.annotate('', xy=(4, 5.5), xytext=(4, 4.6),
                arrowprops=dict(arrowstyle='->', color=BLUE, lw=2.5))
    ax.text(3.1, 5.05, 'Overflow', fontsize=9, color='#666', fontstyle='italic')
    
    ax.annotate('', xy=(8, 5.5), xytext=(8, 4.6),
                arrowprops=dict(arrowstyle='<-', color=BLUE, lw=2.5))
    ax.text(8.3, 5.05, 'Result', fontsize=9, color='#666', fontstyle='italic')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot5_architecture.png'))
    plt.close()
    print("[OK] plot5_architecture.png")

# ============================================================
# PLOT 6: Latency per Component
# ============================================================
def plot6_latence_composant():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    scenarios = ['Edge+Cloud', 'Low Fog (10%)', 'High Fog (50%)']
    edge_lat = [3, 3, 3]
    fog_lat = [0, 18, 7]
    cloud_lat = [250, 250, 250]
    
    x = np.arange(len(scenarios))
    width = 0.22
    
    bars1 = ax.bar(x - width, edge_lat, width, label='Edge (local)', color=GREEN, edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x, fog_lat, width, label='Fog (RSU + V2V)', color=BLUE, edgecolor='white', linewidth=1.5)
    bars3 = ax.bar(x + width, cloud_lat, width, label='Cloud', color=RED, edgecolor='white', linewidth=1.5)
    
    for bar, val in zip(bars1, edge_lat):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{val}', ha='center', fontweight='bold', fontsize=10, color=GREEN)
    for bar, val in zip(bars2, fog_lat):
        label = 'N/A' if val == 0 else str(val)
        ax.text(bar.get_x() + bar.get_width()/2, max(bar.get_height(), 0) + 5,
                label, ha='center', fontweight='bold', fontsize=10, color=BLUE)
    for bar, val in zip(bars3, cloud_lat):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(val), ha='center', fontweight='bold', fontsize=10, color=RED)
    
    ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.set_ylim(0, 295)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3, fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot6_latence_composant.png'))
    plt.close()
    print("[OK] plot6_latence_composant.png")

# ============================================================
# PLOT 7: Maximum Congestion
# ============================================================
def plot7_congestion():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    scenarios = ['Edge+Cloud\n(0% fog)', 'Low Fog\n(10%)', 'High Fog\n(50%)']
    congestion = [77, 77, 63]
    colors = [RED, YELLOW, GREEN]
    
    bars = ax.bar(scenarios, congestion, color=colors, width=0.5, edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, congestion):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f'{val}%', ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    ax.axhline(y=80, color=RED, linestyle='--', linewidth=2, alpha=0.5)
    ax.text(2.3, 81, 'Critical threshold (80%)', fontsize=10, color=RED, fontstyle='italic')
    
    ax.set_ylabel('Maximum Congestion (%)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.annotate('-18%', xy=(2, 63), xytext=(1.5, 50),
                fontsize=13, fontweight='bold', color=GREEN,
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2),
                ha='center')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'plot7_congestion.png'))
    plt.close()
    print("[OK] plot7_congestion.png")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print(f"Generating plots in: {OUTPUT_DIR}\n")
    plot1_latence_moyenne()
    plot2_evolution_latence()
    plot3_distribution()
    plot4_actions_fog()
    plot5_architecture()
    plot6_latence_composant()
    plot7_congestion()
    print(f"\n==> 7 plot images generated successfully!")
