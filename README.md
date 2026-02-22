# 🚗 Vehicular Fog Computing Simulation

> Simulation de trafic intelligent avec architecture **Edge-Fog-Cloud**, intégrant SUMO, iFogSim, SCOOT et un Dashboard temps réel.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Scénarios de simulation](#scénarios-de-simulation)
4. [Installation](#installation)
5. [Lancement](#lancement)
6. [Résultats](#résultats)
7. [Génération des graphiques](#génération-des-graphiques)
8. [Structure du projet](#structure-du-projet)

---

## Vue d'ensemble

Ce projet démontre l'apport du **Fog Computing Véhiculaire** dans la gestion intelligente du trafic. Il compare 3 scénarios (Edge+Cloud, Low Fog, High Fog) et mesure l'impact du fog sur la **latence**, la **consommation énergétique**, la **distribution du traitement** et l'efficacité de l'algorithme **SCOOT**.

### Technologies

| Technologie | Rôle | Langage |
|-------------|------|---------|
| **SUMO** | Simulation de trafic routier | XML/Config |
| **TraCI** | Contrôle en temps réel de SUMO | Python |
| **iFogSim** | Simulation couche Fog Computing | Java |
| **SCOOT** | Optimisation adaptative des feux | Python |
| **Dashboard** | Visualisation temps réel (WebSocket) | HTML/JS/CSS |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLOUD (Distant)                        │
│                   Latence: ~130 ms                          │
└────────────────────────────┬────────────────────────────────┘
                             │ WAN
┌────────────────────────────┴────────────────────────────────┐
│                 COUCHE FOG (iFogSim - Java)                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│   │ RSU_J1  │  │ RSU_J2  │  │ RSU_J3  │  │ RSU_J4  │      │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
│          Latence Fog: ~22 ms  |  SCOOT decisions here      │
└────────────────────────────┬────────────────────────────────┘
                             │ Socket TCP (Port 5555)
┌────────────────────────────┴────────────────────────────────┐
│            ORCHESTRATEUR (Python - server.py)                │
│   SUMOConnector ◄── Orchestrator ──► IFogSimConnector       │
│                        │                                     │
│                   Dashboard (WS)  +  MetricsLogger (CSV)    │
└────────────────────────────┬────────────────────────────────┘
                             │ TraCI
┌────────────────────────────┴────────────────────────────────┐
│                  SUMO (Simulation Trafic)                    │
│        Réseau 600×600m  |  4 intersections (J1-J4)          │
│                  Latence Edge: ~5 ms                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Scénarios de simulation

| Scénario | Fog Nodes | SCOOT | Description |
|----------|-----------|-------|-------------|
| **Edge + Cloud** | 0% | ❌ Désactivé | Baseline : tout passe par Edge ou Cloud |
| **Full Fog - Low** | ~10% | ✅ Actif | Peu de fog nodes, SCOOT limité |
| **Full Fog - High** | ~50% | ✅ Actif | Beaucoup de fog nodes, SCOOT optimal |

### Paramètres clés

- **Durée simulation** : 300 s
- **4 RSU** aux intersections (portée 300 m, capacité ~8 véhicules)
- **V2V** : portée 100 m
- **Débit** : 2000 véhicules/h
- **Tâches** : 0.5–5 Mb input, 50–500 MI

---

## Installation

### Prérequis

- **SUMO** ≥ 1.18.0 (variable `SUMO_HOME` configurée)
- **Python** ≥ 3.10
- **Java** ≥ 11

### Dépendances Python

```bash
pip install -r requirements.txt
```

### Compilation iFogSim

```bash
cd ifogsim
javac -cp "jars/*" -d out src/org/fog/**/*.java
```

---

## Lancement

### 1. Démarrer iFogSim (Terminal 1)

```bash
cd ifogsim
java -cp "out;jars/*" org.fog.test.perfeval.VehicularFogSimulation
```

### 2. Lancer la simulation (Terminal 2)

```bash
# Scénario Edge+Cloud (baseline)
python server.py --dashboard --gui --mode edge_cloud

# Scénario Low Fog (10% fog nodes)
python server.py --dashboard --gui --mode full_fog --fog-density low

# Scénario High Fog (50% fog nodes)
python server.py --dashboard --gui --mode full_fog --fog-density high
```

### Options

| Option | Description |
|--------|-------------|
| `--dashboard` | Active le dashboard web (port 5000) |
| `--gui` | Ouvre l'interface graphique SUMO |
| `--no-gui` | Mode headless (sans GUI SUMO) |
| `--mode` | `edge_cloud` ou `full_fog` |
| `--fog-density` | `low` (10%) ou `high` (50%) |

### Dashboard

Ouvrir **http://localhost:5000** dans un navigateur.

---

## Résultats

Les métriques sont enregistrées automatiquement dans `logs/` au format CSV par le système `MetricsLogger`.

### Résultats obtenus (depuis les logs)

| Métrique | Edge+Cloud | Low Fog (10%) | High Fog (50%) |
|----------|-----------|---------------|----------------|
| **Latence moyenne** | 67.6 ms | 52.7 ms (−22%) | 22.1 ms (−67%) |
| **Énergie/tâche** | 342 mJ | 148 mJ (−57%) | 139 mJ (−59%) |
| **Distribution Fog** | 0% | 78% | 90% |
| **Feux ajustés (SCOOT)** | 0 | 107 | 146 |
| **Véhicules reroutés** | 0 | 1 959 | 4 296 |

### Fichiers de logs

Chaque scénario génère 7 fichiers CSV dans `logs/<scenario>/` :

| Fichier | Contenu |
|---------|---------|
| `latency.csv` | Latence Edge/Fog/Cloud + moyenne pondérée |
| `distribution.csv` | % traitement Edge/Fog/Cloud |
| `energy.csv` | Énergie par tâche (local, fog, cloud) |
| `congestion.csv` | Congestion max par zone RSU |
| `scoot_actions.csv` | Feux ajustés et véhicules reroutés (cumulés) |
| `vehicles.csv` | Nombre de véhicules et fog nodes |
| `tasks.csv` | Tâches traitées par niveau |

---

## Génération des graphiques

Le script `generate_plots_from_logs.py` lit les CSV des 3 scénarios et génère 7 graphiques dans `plots_output/` :

```bash
python generate_plots_from_logs.py
```

### Graphiques générés

| Fichier | Description |
|---------|-------------|
| `plot1_latence_moyenne.png` | Latence moyenne par scénario (barres) |
| `plot2_evolution_latence.png` | Évolution temporelle de la latence |
| `plot3_distribution.png` | Distribution Edge/Fog/Cloud (barres empilées) |
| `plot4_actions_fog.png` | Feux ajustés + reroutages cumulés |
| `plot6_latence_composant.png` | Latence par composant (barres groupées) |
| `plot7_congestion.png` | Évolution de la congestion |
| `plot8_energy_comparison.png` | Énergie décomposée + réduction |

---

## Structure du projet

```
simulation fog&edge/
├── server.py                        # Orchestrateur principal (Python)
├── generate_plots_from_logs.py      # Génération des graphiques depuis les logs
├── requirements.txt                 # Dépendances Python
├── launch.bat                       # Script de lancement Windows
├── .gitignore
│
├── sumo_config/                     # Configuration SUMO
│   ├── network.net.xml              # Topologie réseau (4 intersections)
│   ├── network.nod.xml              # Nœuds
│   ├── network.edg.xml              # Routes
│   ├── routes.rou.xml               # Flux véhicules (baseline)
│   ├── routes_low_fog.rou.xml       # Flux avec 10% fog
│   ├── routes_high_fog.rou.xml      # Flux avec 50% fog
│   ├── simulation.sumocfg           # Config baseline
│   ├── simulation_low_fog.sumocfg   # Config low fog
│   ├── simulation_high_fog.sumocfg  # Config high fog
│   └── detectors.add.xml            # Détecteurs de trafic
│
├── ifogsim/                         # Simulateur Fog Computing (Java)
│   ├── src/org/fog/
│   │   └── test/perfeval/
│   │       ├── VehicularFogSimulation.java  # Simulation principale
│   │       └── SCOOTController.java         # Algorithme SCOOT
│   ├── jars/                        # Dépendances JAR
│   └── out/                         # Classes compilées
│
├── dashboard/                       # Interface web temps réel
│   ├── index.html                   # Page principale
│   ├── app.js                       # Logique JavaScript (WebSocket)
│   └── styles.css                   # Styles CSS
│
├── logs/                            # Logs de simulation (CSV)
│   ├── edge_cloud/                  # Scénario 1
│   ├── full_fog_low/                # Scénario 2
│   └── full_fog_high/               # Scénario 3
│
└── plots_output/                    # Graphiques générés (gitignored)
```

---

## Auteurs

Projet réalisé dans le cadre du **Master Intelligence Artificielle Embarquée** — Module Fog & Edge Computing (2025–2026)

- Oussama BENYSSEF
- Abdessamad EL FATHI
- Mouad ASSARGUAL
- Youssef LAGRAMEZ

**Encadré par** : Pr. K. Ahed

---

## Licence

Usage académique uniquement.
