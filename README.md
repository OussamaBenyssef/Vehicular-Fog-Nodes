# 🚗 Vehicular Fog Computing Simulation

> Simulation de trafic intelligent avec architecture **Edge-Fog-Cloud**, intégrant SUMO, iFogSim, SCOOT, **conscience de la mobilité**, **latence stochastique PDR**, **Load Balancing Proactif** et un Dashboard temps réel complet mesurant des **KPIs de niveau IEEE**.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Fonctionnalités avancées](#fonctionnalités-avancées)
4. [Scénarios de simulation](#scénarios-de-simulation)
5. [Installation](#installation)
6. [Lancement](#lancement)
7. [Dashboard & Résultats](#dashboard--résultats)
8. [Génération des graphiques & Évaluation](#génération-des-graphiques--évaluation)

---

## Vue d'ensemble

Ce projet de fin d'études démontre l'apport du **Fog Computing Véhiculaire collaboratif (V2V/V2I)** dans un environnement urbain ultra-dense. Il compare directement une topologie Cloud traditionnelle avec des architectures Fog distribuées, couplées à la gestion intelligente des feux par **SCOOT**. 

### Technologies

| Technologie | Rôle | Langage |
|-------------|------|---------|
| **SUMO** | Simulation granulaire de trafic routier et mobilité | XML/Config |
| **TraCI** | Contrôle réseau adaptatif temps réel via Python | Python |
| **iFogSim** | Surcouche algorithmique Fog Computing (Calcul et Offloading)| Java |
| **SCOOT** | Optimisation adaptative des temps de feux de signalisation | Java/Python |
| **Dashboard** | Télémétrie visuelle temps réel (WebSocket) | HTML/JS/CSS |

---

## Architecture

L'orchestrateur Python fait office de pont (middleware TCP) entre la mobilité gérée par SUMO et la prise de décision de calcul effectuée par le moteur mathématique Java (iFogSim).

```
┌─────────────────────────────────────────────────────────────┐
│                      CLOUD (Distant)                        │
│             Latence incompressible: ~250 ms                 │
└────────────────────────────┬────────────────────────────────┘
                             │ WAN
┌────────────────────────────┴────────────────────────────────┐
│                 COUCHE FOG (iFogSim - Java)                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│   │ RSU_J1  │  │ RSU_J2  │  │ RSU_J3  │  │ RSU_J4  │      │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
│  Latence Fog: ~22ms | SCOOT | Mobilité | PDR | KPIs IEEE  │
└────────────────────────────┬────────────────────────────────┘
                             │ Socket TCP (Port 5555)
┌────────────────────────────┴────────────────────────────────┐
│            ORCHESTRATEUR (Python - server.py)               │
│   SUMOConnector ◄── Orchestrator ──► IFogSimConnector       │
└────────────────────────────┬────────────────────────────────┘
                             │ TraCI
┌────────────────────────────┴────────────────────────────────┐
│                  SUMO (Simulation Trafic)                   │
│   Réseau 600×600m | 4 intersections (J1-J4) | 2000 veh/h    │
└─────────────────────────────────────────────────────────────┘
```

---

## Fonctionnalités avancées

### ⚖️ Load Balancing Proactif (Offloading Opportuniste V2V)
Afin de garantir un **Deadline Miss Ratio < 5%**, le modèle n'utilise plus les *Fog Vehicles* comme de simples solutions de secours. L'algorithme met en **compétition mathématique stricte** le temps de calcul et de latence V2V avec celui du RSU. Dès que le Fog Vehicle devient mathématiquement plus rapide, ou que le RSU subit une moindre pression (>15% de congestion), la tâche est déchargée proactivement vers les véhicules collaborateurs, ce qui libère la file d'attente Edge.

### 🚗 Conscience de la Mobilité (Mobility-Aware Offloading)
Le modèle d'offloading évalue le risque de déconnexion cinématique de chaque véhicule par rapport à la zone radio RSU à chaque seconde :
1. **Calcul de `timeToExit`** : distance restante / vitesse
2. **Comparaison** avec le temps d'offloading estimé `T_offload`
3. **Déconnexion imminente** (`timeToExit < 1s`) → annulation et **traitement LOCAL forcé**
4. **Risque de handover modéré** (`timeToExit < T_offload`) → ajout d'une **pénalité de handover de 75ms** au système.

### 📡 Modèle de Latence Stochastique PDR (DSRC/C-V2X)
Simulation réaliste de la perte de paquets réseau due aux interférences d'intersection :
`PDR = 1.0 - (congestionNorm × 0.35)`
La latence finale observée est gonflée par ce PDR (`Latence_Base / PDR`), simulant ainsi l'impact congestionnel réel.

### ⚡ Modèle Énergétique
Intégration du **Startup Energy Cost** (50 mJ) pour activer les interfaces radio, afin d'éviter les envois de micro-requêtes insignifiantes, tout en calculant en "Joules par MI" l'effort d'exécution CPU et de transmission bande passante.

### 📊 KPIs IEEE (Key Performance Indicators)
Le code mesure 5 métriques standard d'évaluation des performances sur la période de régime permanent (**Steady-State : de 50s à 300s**, ignorant la chauffe initiale de SUMO) :
- **Task Completion Rate** : Tâches exécutées avec succès avant la sortie de zone.
- **Deadline Miss Ratio** : Tâches accusant une latence système > 100ms.
- **RSU / FogV Utilization** : Répartition de l'utilisation en MIPS (5000 MIPS Edge vs 1500 MIPS Mobile).
- **System Throughput** : Débit global total (Mb/s) maintenu constant sur les expérimentations.

---

## Scénarios de simulation

| Scénario | Fog Nodes | SCOOT | Caractéristique |
|----------|-----------|-------|-------------|
| **Edge + Cloud** | 0% | ❌ Off | Baseline de référence, requêtes traitées lentement via WAN. |
| **Low Fog** | ~10% | ✅ Actif | Légère présence V2V, le RSU absorbe tout le poids du trafic (File M/M/1 lourde). |
| **High Fog** | ~50% | ✅ Actif | Forte densité Fog, Load Balancing proactif parfait libérant complètement l'Edge. |

---

## Installation

### Prérequis
- **SUMO** ≥ 1.18.0
- **Python** ≥ 3.10
- **Java** JDK ≥ 11

###  Compilation & Dépendances
```bash
pip install -r requirements.txt
cd ifogsim
javac -cp "jars/*" -d out src/org/fog/**/*.java
```

---

## Lancement

Dans la racine du projet, lancez :
Terminal 1 (Serveur de Calcul iFogSim) :
```bash
cd ifogsim
java -cp "out;jars/*" org.fog.test.perfeval.VehicularFogSimulation
```

Terminal 2 (Orchestrateur & SUMO) :
```bash
# Baseline
python server.py --dashboard --gui --mode edge_cloud

# High Fog Performance
python server.py --dashboard --gui --mode full_fog --fog-density high
```

Ouvrez **http://localhost:5000** pour voir le tableau de bord de télémétrie ultra-complet incluant l'Intelligence SCOOT, la carte Radar et les KPIs.

---

## Génération des graphiques & Évaluation

Le script Python lit nativement les statistiques stockées de la simulation (qui ignore la période de chauffe des 50 premières secondes) pour tracer 11 graphiques vectorisés prêts à être intégrés dans une thèse académique.

```bash
python generate_plots_from_logs.py
```
Les graphiques (Latence moyenne, distribution par composant, actions SCOOT, Task Completion, utilisation matérielle) seront enregistrés dans le dossier `plots_output/`.

---

## Conception Mathématique du Moteur Java

### L'Entonnoir de Décision d'Offloading
`destination = argmin(T_d + α·L_d + β·E_d)`

À chaque milliseconde pour chaque véhicule :
1. **CPU local dispo + tâche légère** → LOCAL
2. **Congestion RSU critique** → LOCAL (Mode Panique pour éviter perte de signal)
3. **Load Balancing Proactif** → FOG_VEHICLE (Si latence mathématique meilleure ou RSU > 15% charge)
4. **Disponibilité Edge** → RSU (Offloading V2I classique)
5. **Dernier Recours Central** → CLOUD (Latence WAN imposée ≈ 250ms)

---

## Équipe
Projet de Master Intelligence Artificielle Embarquée — Module Fog & Edge Computing (2025–2026)
- Oussama BENYSSEF
- Abdessamad EL FATHI
- Mouad ASSARGUAL
- Youssef LAGRAMEZ

*Encadré par : Pr. K. Ahed*
