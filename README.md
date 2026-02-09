# 🚗 Simulation Fog Computing Véhiculaire

> Système de simulation de trafic intelligent avec architecture Fog Computing, intégrant SUMO, TraCI et iFogSim.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du système](#architecture-du-système)
3. [Composants détaillés](#composants-détaillés)
4. [Flux de données](#flux-de-données)
5. [Traitements et décisions](#traitements-et-décisions)
6. [Installation et exécution](#installation-et-exécution)
7. [Structure des fichiers](#structure-des-fichiers)

---

## Vue d'ensemble

Ce projet simule un système de gestion intelligente du trafic basé sur le **Fog Computing**. Il démontre comment les décisions peuvent être prises au niveau local (RSU/Fog) plutôt qu'au Cloud, réduisant ainsi la latence et améliorant la réactivité du système.

### Technologies utilisées

| Technologie | Rôle | Langage |
|-------------|------|---------|
| **SUMO** | Simulation de trafic routier | XML/Configuration |
| **TraCI** | Interface de contrôle en temps réel | Python |
| **iFogSim** | Simulation couche Fog Computing | Java |
| **Dashboard** | Visualisation temps réel | HTML/JS |

---

## Architecture du système

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLOUD (Distant)                                  │
│                    Latence: ~125ms                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Connexion WAN
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    COUCHE FOG (iFogSim - Java)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   RSU_J1    │  │   RSU_J2    │  │   RSU_J3    │  │   RSU_J4    │    │
│  │ (200,200)   │  │ (400,200)   │  │ (200,400)   │  │ (400,400)   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│       │               │               │               │                 │
│       └───────────────┴───────────────┴───────────────┘                 │
│                               │                                          │
│                    Latence Fog: ~22ms                                   │
│                    ★ DÉCISIONS PRISES ICI ★                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Socket TCP (Port 5555)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATEUR (Python - server.py)                      │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │ SUMOConnector│◄───│  Orchestrator │───►│ IFogSimConn │              │
│  │   (TraCI)    │    │              │    │   (Socket)   │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                   │                    │                       │
│         │            ┌──────┴──────┐             │                       │
│         │            │  Dashboard  │             │                       │
│         │            │ (WebSocket) │             │                       │
│         │            └─────────────┘             │                       │
│         │                                                                │
│                    ★ EXÉCUTION DES DÉCISIONS ICI ★                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ TraCI (libsumo)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SUMO (Simulation Trafic)                            │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Réseau Routier 600x600m                      │    │
│  │                                                                   │    │
│  │        N1 ─────────── J1 ─────────── J2 ─────────── N2          │    │
│  │                        │              │                          │    │
│  │        S1              │              │              S2          │    │
│  │                        │              │                          │    │
│  │        N3 ─────────── J3 ─────────── J4 ─────────── N4          │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│                    ★ SIMULATION PHYSIQUE ICI ★                           │
│                    Latence Edge: ~5ms                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Composants détaillés

### 1. SUMO (Simulation of Urban Mobility)

**Fichier principal:** `sumo_config/simulation.sumocfg`

SUMO est le simulateur de trafic qui gère :
- Le **réseau routier** (intersections, routes, feux)
- Les **véhicules** (positions, vitesses, trajectoires)
- Les **feux de circulation** (phases, durées)

#### Fichiers de configuration SUMO

| Fichier | Description |
|---------|-------------|
| `network.net.xml` | Topologie du réseau (jonctions J1-J4, routes) |
| `routes.rou.xml` | Définition des flux de véhicules par phase |
| `simulation.sumocfg` | Configuration principale (durée, délais, etc.) |

#### Phases de simulation

```
Phase 1 (T=0 à T=300s)    : Trafic normal
Phase 2 (T=300 à T=600s)  : Congestion (trafic élevé)
Phase 3 (T=600 à T=900s)  : Récupération
```

---

### 2. TraCI (Traffic Control Interface)

**Fichier principal:** `server.py` → classe `SUMOConnector`

TraCI est l'API Python qui permet de contrôler SUMO en temps réel.

#### Fonctionnalités utilisées

```python
# Lecture des données véhicules
traci.vehicle.getIDList()           # Liste des véhicules actifs
traci.vehicle.getPosition(veh_id)   # Position (x, y)
traci.vehicle.getSpeed(veh_id)      # Vitesse en m/s
traci.vehicle.getTypeID(veh_id)     # Type (car, fog_capable)

# Contrôle des feux de circulation
traci.trafficlight.getPhase(tl_id)         # Phase actuelle (0-3)
traci.trafficlight.setPhase(tl_id, phase)  # Forcer une phase
traci.trafficlight.setPhaseDuration(tl_id, duration)  # Durée du vert

# Simulation
traci.simulationStep()              # Avancer d'un pas (1 seconde)
traci.simulation.getTime()          # Temps simulation actuel
```

#### Classe SUMOConnector

```python
class SUMOConnector:
    """
    Connecteur SUMO via TraCI
    
    Responsabilités:
    - Connexion/déconnexion SUMO
    - Récupération état des véhicules à chaque step
    - Exécution des commandes TraCI (feux, routes)
    """
    
    def step(self) -> Dict[str, VehicleState]:
        """
        Exécute un pas de simulation et retourne l'état des véhicules
        
        Retour:
        - Dict avec ID véhicule → VehicleState (position, vitesse, type, RSU)
        """
```

---

### 3. iFogSim (Fog Computing Simulator)

**Fichier principal:** `ifogsim/src/org/fog/test/perfeval/VehicularFogSimulation.java`

iFogSim simule la couche Fog Computing et prend les **décisions intelligentes**.

#### Architecture iFogSim

```
┌─────────────────────────────────────────────────┐
│              VehicularFogSimulation              │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         Serveur Socket (Port 5555)        │   │
│  │                                           │   │
│  │  1. Reçoit JSON de Python                 │   │
│  │  2. Parse les données véhicules           │   │
│  │  3. Calcule métriques par zone RSU        │   │
│  │  4. Prend les décisions Fog               │   │
│  │  5. Renvoie JSON avec décisions           │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Zones RSU:                                      │
│  - RSU_J1: rayon 150m autour de (200, 200)      │
│  - RSU_J2: rayon 150m autour de (400, 200)      │
│  - RSU_J3: rayon 150m autour de (200, 400)      │
│  - RSU_J4: rayon 150m autour de (400, 400)      │
│                                                  │
└─────────────────────────────────────────────────┘
```

#### Logique de décision Fog

```java
// Dans buildFogDecisions()
for (zone : zoneVehicleCount) {
    congestion = vehicleCount / 30.0;  // Max 30 véhicules = 100%
    
    if (congestion > 0.7) {
        // Décision 1: Contrôle adaptatif des feux
        decisions.add({
            type: "EXTEND_GREEN",
            rsu: zone.id,
            trafficLight: zone.id.replace("RSU_", "")
        });
        
        // Décision 2: Réacheminement (désactivé)
        // decisions.add({type: "REROUTE_VEHICLES", ...});
    }
}
```

---

## Flux de données

### Cycle principal (1 itération = 1 seconde simulation)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CYCLE PRINCIPAL                                │
└─────────────────────────────────────────────────────────────────────────┘

     SUMO                    Python                   iFogSim
       │                       │                         │
       │   1. simulationStep   │                         │
       │◄──────────────────────│                         │
       │                       │                         │
       │   2. Récupérer état   │                         │
       │──────────────────────►│                         │
       │   (positions, vitesses│                         │
       │    types véhicules)   │                         │
       │                       │                         │
       │                       │   3. Envoyer JSON       │
       │                       │────────────────────────►│
       │                       │   {vehicles, time,      │
       │                       │    positions...}        │
       │                       │                         │
       │                       │                    4. Calculer
       │                       │                    métriques par
       │                       │                    zone RSU
       │                       │                         │
       │                       │                    5. Prendre
       │                       │                    décisions Fog
       │                       │                         │
       │                       │   6. Retourner JSON     │
       │                       │◄────────────────────────│
       │                       │   {metrics,             │
       │                       │    fogDecisions: [...]} │
       │                       │                         │
       │   7. Exécuter         │                         │
       │   décisions TraCI     │                         │
       │◄──────────────────────│                         │
       │   (setPhase,          │                         │
       │    setPhaseDuration)  │                         │
       │                       │                         │
       │                       │   8. Envoyer au         │
       │                       │   Dashboard             │
       │                       │──────────►              │
       │                       │                         │
       ▼                       ▼                         ▼
```

### Format des données échangées

#### Python → iFogSim (JSON envoyé)

```json
{
  "time": 345.0,
  "vehicles": [
    {
      "id": "phase2_we_car.42",
      "x": 185.3,
      "y": 201.7,
      "speed": 2.5,
      "type": "car",
      "rsu": "RSU_J1"
    }
  ]
}
```

#### iFogSim → Python (JSON reçu)

```json
{
  "totalVehicles": 156,
  "fogNodes": 45,
  "tasksProcessed": 12450,
  "latency": {"edge": 5.2, "fog": 22.4, "cloud": 125.3},
  "zones": {"RSU_J1": 89, "RSU_J2": 23, "RSU_J3": 31, "RSU_J4": 13},
  "fogDecisions": {
    "actions": [
      {"type": "EXTEND_GREEN", "rsu": "RSU_J1", "trafficLight": "J1"},
      {"type": "EXTEND_GREEN", "rsu": "RSU_J3", "trafficLight": "J3"}
    ]
  }
}
```

---

## Traitements et décisions

### Où sont faits les traitements ?

| Traitement | Lieu | Fichier | Fonction |
|------------|------|---------|----------|
| Simulation physique trafic | SUMO | `simulation.sumocfg` | Automatique |
| Lecture état véhicules | Python (TraCI) | `server.py` | `SUMOConnector.step()` |
| Calcul congestion par zone | iFogSim (Java) | `VehicularFogSimulation.java` | `processVehicleData()` |
| Décision contrôle feux | iFogSim (Java) | `VehicularFogSimulation.java` | `buildFogDecisions()` |
| Exécution décisions | Python (TraCI) | `server.py` | `_execute_fog_decisions()` |
| Affichage Dashboard | JavaScript | `dashboard/app.js` | `updateDashboard()` |

### Algorithme de contrôle intelligent des feux

```python
def _execute_fog_decisions(self, decisions):
    """
    Exécuté dans server.py
    
    LOGIQUE INTELLIGENTE:
    1. Compter véhicules à l'arrêt (speed < 2 m/s) par direction
    2. Déterminer direction la plus congestionnée (N-S vs E-W)
    3. Basculer le feu vers cette direction
    """
    
    for decision in decisions:
        if decision.type == "EXTEND_GREEN":
            
            # Compter véhicules Nord-Sud
            ns_waiting = count(vehicles on E_N1_J1, E_S1_J1, ...)
            
            # Compter véhicules Est-Ouest
            ew_waiting = count(vehicles on E_J2_J1, ...)
            
            # Décider la phase
            if ns_waiting > ew_waiting + 5:
                traci.trafficlight.setPhase("J1", 2)  # Vert N-S
            elif ew_waiting > ns_waiting + 5:
                traci.trafficlight.setPhase("J1", 0)  # Vert E-W
            else:
                # Allonger la phase actuelle
                traci.trafficlight.setPhaseDuration("J1", +10s)
```

### Phases des feux de circulation

| Phase | État | Direction verte |
|-------|------|-----------------|
| 0 | Vert | Est-Ouest (horizontal) |
| 1 | Jaune | Transition |
| 2 | Vert | Nord-Sud (vertical) |
| 3 | Jaune | Transition |

---

## Installation et exécution

### Prérequis

- **SUMO** ≥ 1.18.0 avec variable `SUMO_HOME` configurée
- **Python** ≥ 3.10 avec packages: `traci`, `flask`, `flask-socketio`, `eventlet`
- **Java** ≥ 11 pour iFogSim

### Lancement

```bash
# Terminal 1 - iFogSim (Fog Layer)
cd ifogsim
java -cp "out;jars/*" org.fog.test.perfeval.VehicularFogSimulation

# Terminal 2 - Python + SUMO + Dashboard
python server.py --dashboard --gui
```

### Accès Dashboard

Ouvrir `http://localhost:5000` dans un navigateur.

---

## Structure des fichiers

```
simulation/
├── server.py                    # Orchestrateur principal (Python)
├── launch.bat                   # Script de lancement Windows
│
├── sumo_config/                 # Configuration SUMO
│   ├── simulation.sumocfg       # Fichier principal
│   ├── network.net.xml          # Topologie réseau
│   ├── network.nod.xml          # Nœuds (jonctions)
│   ├── network.edg.xml          # Edges (routes)
│   └── routes.rou.xml           # Flux de véhicules
│
├── ifogsim/                     # Simulateur Fog (Java)
│   ├── src/
│   │   └── org/fog/test/perfeval/
│   │       └── VehicularFogSimulation.java
│   ├── jars/                    # Dépendances JAR
│   └── out/                     # Classes compilées
│
├── dashboard/                   # Interface web
│   ├── index.html               # Page principale
│   ├── app.js                   # Logique JavaScript
│   └── styles.css               # Styles CSS
│
└── README.md                    # Ce fichier
```

---

## Auteurs

Projet réalisé dans le cadre du Master 2 - Module FOG & Edge Computing

---

## Licence

Usage académique uniquement.
