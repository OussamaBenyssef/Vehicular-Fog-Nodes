# -*- coding: utf-8 -*-
"""
Generate table images for the Beamer presentation.
Images without title (title is in the Beamer frame) and compact.
Run: python generate_tables.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Output to plots_output/ subdirectory (relative to this script)
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "plots_output"

# Colors
BLUE = '#2563EB'
GREEN = '#16A34A'
RED = '#DC2626'
YELLOW = '#CA8A04'
HEADER_BG = '#1E3A5F'
HEADER_FG = 'white'
ROW_EVEN = '#F0F4F8'
ROW_ODD = '#FFFFFF'
ACCENT_GREEN = '#D1FAE5'
ACCENT_RED = '#FEE2E2'
ACCENT_YELLOW = '#FEF3C7'

def style_table(ax, table_obj, scale_y=1.5):
    """Apply consistent styling to a table."""
    table_obj.auto_set_font_size(False)
    table_obj.set_fontsize(11)
    table_obj.scale(1, scale_y)
    for key, cell in table_obj.get_celld().items():
        cell.set_edgecolor('#CBD5E1')
        cell.set_linewidth(0.5)
        row, col = key
        if row == 0:
            cell.set_facecolor(HEADER_BG)
            cell.set_text_props(color=HEADER_FG, fontweight='bold', fontsize=11)
        else:
            cell.set_facecolor(ROW_EVEN if row % 2 == 0 else ROW_ODD)
            cell.set_text_props(fontsize=10)
        if col == 0:
            cell.set_text_props(ha='left')
            cell.PAD = 0.05
        else:
            cell.set_text_props(ha='center')

# ============================================================
# TABLE 1: Simulation Scenarios
# ============================================================
def table1_scenarios():
    fig, ax = plt.subplots(figsize=(11, 2))
    ax.axis('off')
    cols = ['Scenario', 'Fog Nodes', 'SCOOT', 'Cloud', 'Description']
    data = [
        ['Edge + Cloud', '0%', 'Disabled', 'Yes', 'Baseline (no fog)'],
        ['Full Fog - Low', '~10%', 'Active', 'Yes', 'Few fog nodes'],
        ['Full Fog - High', '~50%', 'Active', 'Yes', 'Many fog nodes'],
    ]
    table = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, table, 1.4)
    table[(1,0)].set_text_props(color=RED, fontweight='bold')
    table[(2,0)].set_text_props(color=YELLOW, fontweight='bold')
    table[(3,0)].set_text_props(color=GREEN, fontweight='bold')
    plt.savefig(OUTPUT_DIR / 'table1_scenarios.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.05)
    plt.close()
    print("[OK] table1_scenarios.png")

# ============================================================
# TABLE 2a: Network Infrastructure
# ============================================================
def table2a_infrastructure():
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.axis('off')
    cols = ['Parameter', 'Value']
    data = [
        ['Simulation duration', '300 s'],
        ['Number of RSUs', '4 (at intersections)'],
        ['RSU range', '300 m'],
        ['RSU capacity', '~8 simultaneous veh.'],
        ['V2V range', '100 m'],
        ['Vehicle throughput', '2000 veh/h'],
        ['Number of roads', '5'],
    ]
    t = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, t, 1.3)
    plt.savefig(OUTPUT_DIR / 'table2a_infrastructure.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.02)
    plt.close()
    print("[OK] table2a_infrastructure.png")

# ============================================================
# TABLE 2b: Generated Tasks
# ============================================================
def table2b_taches():
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.axis('off')
    cols = ['Parameter', 'Value']
    data = [
        ['Input size (D_input)', '0.5 - 5.0 Mb'],
        ['Output size (D_output)', '20% of input'],
        ['Instructions (I)', '50 - 500 MI'],
        ['CPU load', '20 - 80%'],
    ]
    t = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, t, 1.3)
    plt.savefig(OUTPUT_DIR / 'table2b_taches.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.02)
    plt.close()
    print("[OK] table2b_taches.png")

# ============================================================
# TABLE 2c: Computing Capacities
# ============================================================
def table2c_capacites():
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.axis('off')
    cols = ['Level', 'MIPS']
    data = [
        ['Local vehicle (Edge)', '500'],
        ['Fog-capable vehicle', '1,500'],
        ['RSU', '5,000'],
        ['Cloud', '20,000'],
    ]
    t = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, t, 1.3)
    t[(1,1)].set_text_props(color=GREEN, fontweight='bold')
    t[(2,1)].set_text_props(color=YELLOW, fontweight='bold')
    t[(3,1)].set_text_props(color=BLUE, fontweight='bold')
    t[(4,1)].set_text_props(color=RED, fontweight='bold')
    plt.savefig(OUTPUT_DIR / 'table2c_capacites.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.02)
    plt.close()
    print("[OK] table2c_capacites.png")

# ============================================================
# TABLE 2d: Bandwidth and Latency
# ============================================================
def table2d_bandes():
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.axis('off')
    cols = ['Link', 'Throughput', 'Latency']
    data = [
        ['V2V (fog)', '10 Mbps', '5-20 ms'],
        ['V2I (RSU)', '20 Mbps', '7-15 ms'],
        ['Cloud up', '5 Mbps', '250 ms'],
        ['Cloud down', '10 Mbps', '250 ms'],
    ]
    t = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, t, 1.3)
    plt.savefig(OUTPUT_DIR / 'table2d_bandes.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.02)
    plt.close()
    print("[OK] table2d_bandes.png")

# ============================================================
# TABLE 3: Traffic Scenario Details
# ============================================================
def table3_scenarios_detail():
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.axis('off')
    cols = ['Parameter', 'Edge+Cloud', 'Low Fog', 'High Fog']
    data = [
        ['Total throughput', '2000 veh/h', '2000 veh/h', '2000 veh/h'],
        ['Standard vehicles', '100%', '90%', '50%'],
        ['Fog-capable vehicles', '0%', '10%', '50%'],
        ['Fog enabled', 'No', 'Yes', 'Yes'],
        ['SCOOT enabled', 'No', 'Yes', 'Yes'],
        ['Route file', 'routes.rou.xml', 'routes_low_fog', 'routes_high_fog'],
    ]
    table = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, table, 1.3)
    table[(0,1)].set_facecolor(RED)
    table[(0,2)].set_facecolor(YELLOW)
    table[(0,3)].set_facecolor(GREEN)
    plt.savefig(OUTPUT_DIR / 'table3_scenarios_detail.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.05)
    plt.close()
    print("[OK] table3_scenarios_detail.png")

# ============================================================
# TABLE 4: Evaluated Metrics
# ============================================================
def table4_metriques():
    fig, ax = plt.subplots(figsize=(11, 3.3))
    ax.axis('off')
    cols = ['Metric', 'Description']
    data = [
        ['Average latency', 'Weighted average task processing time'],
        ['Processing distribution', 'Edge / Fog / Cloud breakdown (%)'],
        ['Active Fog Nodes', 'Number of detected fog-capable vehicles'],
        ['Adjusted traffic lights', 'SCOOT decisions applied to traffic lights'],
        ['Rerouted vehicles', 'Reroutings following congestion detection'],
        ['Max congestion', 'Maximum saturation rate per RSU zone'],
        ['Energy per task', 'Weighted energy consumption per task (mJ)'],
    ]
    table = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, table, 1.3)
    for i in range(1, 8):
        table[(i,0)].set_text_props(fontweight='bold', color=BLUE)
    table.auto_set_column_width([0, 1])
    plt.savefig(OUTPUT_DIR / 'table4_metriques.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.05)
    plt.close()
    print("[OK] table4_metriques.png")

# ============================================================
# TABLE 5: Comparative Results
# ============================================================
def table5_resultats():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.axis('off')
    cols = ['Metric', 'Edge+Cloud', 'Low Fog (10%)', 'High Fog (50%)']
    data = [
        ['Max vehicles', '41', '41', '47'],
        ['Active Fog Nodes', '0', '5 (12%)', '22 (51%)'],
        ['Adjusted lights (SCOOT)', '0', '107', '146'],
        ['Rerouted vehicles', '0', '1,959', '4,296'],
        ['Max congestion', '100%', '93%', '100%'],
        ['', '', '', ''],
        ['Edge latency', '5 ms', '5 ms', '5 ms'],
        ['Fog latency', '--', '22 ms', '22 ms'],
        ['Cloud latency', '130 ms', '130 ms', '130 ms'],
        ['', '', '', ''],
        ['Average latency', '~68 ms', '~53 ms (-22%)', '~22 ms (-67%)'],
        ['Energy per task', '342 mJ', '148 mJ (-57%)', '139 mJ (-59%)'],
    ]
    table = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, table, 1.3)
    table[(0,1)].set_facecolor(RED)
    table[(0,2)].set_facecolor(YELLOW)
    table[(0,3)].set_facecolor(GREEN)
    for col in range(4):
        table[(6,col)].set_facecolor('#E2E8F0')
        table[(6,col)].set_height(0.005)
        table[(6,col)].set_text_props(fontsize=1)
        table[(10,col)].set_facecolor('#E2E8F0')
        table[(10,col)].set_height(0.005)
        table[(10,col)].set_text_props(fontsize=1)
    # Average latency row (row 11)
    table[(11,0)].set_text_props(fontweight='bold', fontsize=12)
    table[(11,1)].set_text_props(fontweight='bold', color=RED, fontsize=12)
    table[(11,1)].set_facecolor(ACCENT_RED)
    table[(11,2)].set_text_props(fontweight='bold', color=YELLOW, fontsize=12)
    table[(11,2)].set_facecolor(ACCENT_YELLOW)
    table[(11,3)].set_text_props(fontweight='bold', color=GREEN, fontsize=12)
    table[(11,3)].set_facecolor(ACCENT_GREEN)
    # Energy row (row 12)
    table[(12,0)].set_text_props(fontweight='bold', fontsize=11)
    table[(12,1)].set_text_props(fontweight='bold', color=RED, fontsize=11)
    table[(12,1)].set_facecolor(ACCENT_RED)
    table[(12,2)].set_text_props(fontweight='bold', color=GREEN, fontsize=11)
    table[(12,2)].set_facecolor(ACCENT_GREEN)
    table[(12,3)].set_text_props(fontweight='bold', color=GREEN, fontsize=11)
    table[(12,3)].set_facecolor(ACCENT_GREEN)
    for r in [7, 8, 9, 11, 12]:
        table[(r,0)].set_text_props(fontweight='bold')
    plt.savefig(OUTPUT_DIR / 'table5_resultats.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.05)
    plt.close()
    print("[OK] table5_resultats.png")

# ============================================================
# TABLE 6: Technological Evolution
# ============================================================
def table6_evolution():
    fig, ax = plt.subplots(figsize=(9, 2))
    ax.axis('off')
    cols = ['Parameter', 'DSRC (current)', '5G C-V2X', '6G (future)']
    data = [
        ['Latency', '20-50 ms', '1-10 ms', '< 1 ms'],
        ['Throughput', '27 Mbps', '1 Gbps', '1 Tbps'],
        ['Range', '300 m', '1 km', '10 km'],
    ]
    table = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
    style_table(ax, table, 1.3)
    table[(0,1)].set_facecolor(YELLOW)
    table[(0,2)].set_facecolor(BLUE)
    table[(0,3)].set_facecolor(GREEN)
    for r in range(1, 4):
        table[(r,3)].set_text_props(fontweight='bold', color=GREEN)
    plt.savefig(OUTPUT_DIR / 'table6_evolution.png', bbox_inches='tight', dpi=200, facecolor='white', pad_inches=0.05)
    plt.close()
    print("[OK] table6_evolution.png")

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Generating tables in: {OUTPUT_DIR}\n")
    table1_scenarios()
    table2a_infrastructure()
    table2b_taches()
    table2c_capacites()
    table2d_bandes()
    table3_scenarios_detail()
    table4_metriques()
    table5_resultats()
    table6_evolution()
    print(f"\n==> 9 table images generated in {OUTPUT_DIR}/")
