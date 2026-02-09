# Architecture et Flux de Données - Simulation Fog Véhiculaire

## Vue d'ensemble

Ce système simule une infrastructure de **Fog Computing Véhiculaire** où les véhicules, les RSUs (Roadside Units) et le Cloud collaborent pour traiter les données de trafic en temps réel.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLOUD                                    │
│                    (Latence: ~125ms)                             │
│              Analyse globale, ML, historique                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ 5% des données
                             ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  RSU_J1 │    │  RSU_J2 │    │  RSU_J3 │    │  RSU_J4 │
│(~22ms)  │    │ (~22ms) │    │ (~22ms) │    │ (~22ms) │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │
     │   25% des données (agrégation zone)        │
     ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│              VEHICULES (Fog Nodes mobiles)                       │
│                    (Latence: ~5ms)                               │
│            70% traitement local (Edge)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Composants du Système

### 1. SUMO (Simulation of Urban MObility)

**Rôle** : Génère le trafic véhiculaire réaliste

**Fichiers de configuration** :
- `network.net.xml` : Réseau routier (4 intersections J1-J4)
- `routes.rou.xml` : Itinéraires et types de véhicules
- `simulation.sumocfg` : Configuration globale (900 secondes)

**Types de véhicules** :
| Type | Vitesse max | Caractéristique |
|------|-------------|-----------------|
| `car` | 50 km/h | Véhicule standard |
| `fog_capable` | 50 km/h | Équipé pour traitement fog |
| `bus` | 40 km/h | Toujours fog-capable (arrêts fréquents) |
| `truck` | 35 km/h | Capacité de stockage |

**Phases de simulation** :
1. **Normal (0-300s)** : Trafic fluide, ~50 véhicules
2. **Congestion (300-600s)** : Incident simulé, ~150 véhicules
3. **Récupération (600-900s)** : Retour à la normale

---

### 2. RSU (Roadside Unit)

**Rôle** : Points d'agrégation fixes aux intersections

**Positions** :
```
RSU_J1 (200, 200)  ←→  RSU_J2 (400, 200)
       ↕                      ↕
RSU_J3 (200, 400)  ←→  RSU_J4 (400, 400)
```

**Zone de couverture** : 300 mètres de rayon

**Fonctions** :
- Agrégation des données des véhicules proches
- Contrôle des feux de circulation
- Cache des données fréquemment demandées
- Relais vers le Cloud (seulement données agrégées)

**Calcul de congestion** :
```
congestion = min(nombre_véhicules / 30, 1.0)
```
- Vert (< 0.3) : Fluide
- Jaune (0.3 - 0.6) : Modéré
- Rouge (> 0.6) : Congestionné

---

### 3. Fog Nodes (Véhicules)

**Critères pour devenir Fog Node** :
```python
is_fog_node = (
    type == "fog_capable" or 
    type == "bus" or 
    speed < 8.33 m/s  # < 30 km/h
)
```

**Pourquoi la vitesse compte** :
- Véhicule lent = connexion stable avec RSU
- Peut servir de relais pour véhicules rapides
- Disponibilité CPU pour traitement

**Tâches traitées localement** :
- Détection d'incidents (freinage brusque)
- Agrégation données capteurs
- Prédiction de collision V2V

---

### 4. Offload (Déchargement)

**Qu'est-ce qu'un véhicule en offload ?**

Un véhicule avec `speed < 2 m/s` (pratiquement arrêté) qui :
1. Reçoit des tâches d'autres véhicules
2. Traite ces tâches avec son CPU libre
3. Renvoie les résultats

**Visualisation** : Points rouges sur la carte

**Scénario typique** :
```
Véhicule A (60 km/h) → "J'ai une tâche lourde"
                       ↓
Véhicule B (arrêté au feu) → "Je traite pour toi"
                       ↓
Véhicule A ← Résultat en 5ms au lieu de 125ms (Cloud)
```

---

## Flux de Données en Temps Réel

### Étape 1 : SUMO génère les positions
```
SUMO → TraCI → Python (server.py)

Données par véhicule :
{
  "id": "veh_42",
  "x": 312.5,
  "y": 198.2,
  "speed": 12.4,
  "road_id": "E_J1_J2",
  "type_id": "fog_capable"
}
```

### Étape 2 : Python enrichit et transmet
```python
# Classification fog node
is_fog = type == "fog_capable" or speed < 8.33

# Trouver RSU le plus proche
nearest_rsu = find_nearest_rsu(x, y)  # Rayon 300m

# Envoyer à iFogSim via Socket
socket.send(json.dumps(vehicle_data))
```

### Étape 3 : iFogSim calcule les métriques
```java
// Réception données
JSONObject data = parseVehicleData();

// Mise à jour compteurs
totalVehicles = vehicles.size();
fogNodes = countFogCapable(vehicles);

// Calcul latences dynamiques
edgeLatency = 5.2 + congestion * 3;
fogLatency = 22.4 + congestion * 10;
cloudLatency = 125.3 + congestion * 25;

// Réduction grâce aux fog nodes
fogReduction = min(fogNodes / 20.0, 0.3);
fogLatency *= (1 - fogReduction);
```

### Étape 4 : Dashboard affiche en temps réel
```javascript
// Polling API toutes les 500ms
fetch('/api/status')
  .then(data => updateDashboard(data));

// Mise à jour canvas et graphiques
renderTrafficMap(data.vehicles, data.rsu);
updateCharts(data.metrics, data.time);
```

---

## Métriques Clés

### Distribution du Traitement
| Niveau | % Traitement | Latence | Exemple de tâche |
|--------|--------------|---------|------------------|
| Edge (véhicule) | 70% | ~5ms | Détection collision |
| Fog (RSU) | 25% | ~22ms | Agrégation zone |
| Cloud | 5% | ~125ms | Analyse ML globale |

### Bénéfices du Fog Computing

**Sans Fog (Cloud-only)** :
- Latence : 125ms pour tout
- Bande passante : 100% vers Cloud
- Congestion réseau élevée

**Avec Fog** :
- Latence moyenne : ~16-20ms
- Réduction bande passante : 95%
- Réseau décongestionné

### Formule de latence moyenne
```
latence_moyenne = (
    edge_latency × edge_percent +
    fog_latency × fog_percent +
    cloud_latency × cloud_percent
) / 100
```

---

## Scénario de Congestion

### T = 300s : Incident détecté
1. Véhicules ralentissent → Plus de fog nodes disponibles
2. RSUs détectent congestion → Couleur passe au rouge
3. Tâches redistribuées vers fog nodes
4. Latence augmente légèrement puis se stabilise

### T = 600s : Récupération
1. Trafic reprend normalement
2. Moins de fog nodes (vitesses élevées)
3. Plus de charge vers RSUs
4. Système s'adapte automatiquement

---

## Fichiers du Projet

| Composant | Fichier | Rôle |
|-----------|---------|------|
| SUMO | `sumo_config/` | Configuration trafic |
| iFogSim | `VehicularFogSimulation.java` | Serveur socket + métriques |
| Orchestrateur | `server.py` | Pont SUMO ↔ iFogSim ↔ Dashboard |
| Dashboard | `dashboard/` | Interface temps réel |

---

## Commandes de Lancement

```bash
# Terminal 1 : iFogSim
cd simulation/ifogsim
java -cp "out;jars/*" org.fog.test.perfeval.VehicularFogSimulation

# Terminal 2 : Python + SUMO
cd simulation
python server.py --dashboard --gui
```

Dashboard : http://localhost:5000
