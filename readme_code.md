# 📖 Documentation Technique du Code

> Explication détaillée du code principal, des calculs Fog et de chaque fichier.

---

## 📁 Fichiers Principaux

| Fichier | Langage | Rôle |
|---------|---------|------|
| `server.py` | Python | Orchestrateur central, TraCI, Dashboard |
| `VehicularFogSimulation.java` | Java | Simulation Fog, décisions RSU |
| `dashboard/app.js` | JavaScript | Visualisation temps réel |

---

## 🔷 1. server.py (Python)

**Chemin :** `simulation/server.py`

### Classes Principales

#### 1.1 `VehicleState` (dataclass)
```python
@dataclass
class VehicleState:
    id: str           # Identifiant unique du véhicule
    x: float          # Position X (mètres)
    y: float          # Position Y (mètres)
    speed: float      # Vitesse (m/s)
    vehicle_type: str # Type: "car" ou "fog_capable"
    road_id: str      # Route actuelle
    nearest_rsu: str  # RSU le plus proche (ex: "RSU_J1")
```

#### 1.2 `SimulationMetrics` (dataclass)
```python
@dataclass
class SimulationMetrics:
    simulation_time: float      # Temps simulation (secondes)
    total_vehicles: int         # Nombre total véhicules
    fog_nodes: int              # Véhicules fog-capable
    tasksProcessed: int         # Tâches traitées
    zone_congestion: Dict       # Congestion par zone RSU
    total_rerouted: int         # Compteur reroutage
    total_tl_adjusted: int      # Compteur ajustements feux
```

---

### 1.3 `SUMOConnector` - Connexion TraCI

```python
class SUMOConnector:
    def connect(self, config_path: str, gui: bool = True):
        """Lance SUMO et établit connexion TraCI"""
        sumo_cmd = [sumo_binary, "-c", config_path]
        traci.start(sumo_cmd)
    
    def step(self) -> Dict[str, VehicleState]:
        """
        Avance d'un pas de simulation (1 seconde)
        
        CALCULS EFFECTUÉS:
        1. traci.simulationStep() - Avance SUMO
        2. Pour chaque véhicule:
           - Récupère position: traci.vehicle.getPosition(veh_id)
           - Récupère vitesse: traci.vehicle.getSpeed(veh_id)
           - Calcule RSU le plus proche: _find_nearest_rsu(x, y)
        """
```

#### Calcul du RSU le plus proche
```python
def _find_nearest_rsu(self, x: float, y: float) -> str:
    """
    FORMULE: Distance Euclidienne
    
    distance = √[(x - rsu_x)² + (y - rsu_y)²]
    
    Positions RSU:
    - RSU_J1: (200, 200)
    - RSU_J2: (400, 200)
    - RSU_J3: (200, 400)
    - RSU_J4: (400, 400)
    """
    min_dist = float('inf')
    nearest = "RSU_J1"
    for rsu_id, pos in self.rsu_positions.items():
        dist = math.sqrt((x - pos['x'])**2 + (y - pos['y'])**2)
        if dist < min_dist:
            min_dist = dist
            nearest = rsu_id
    return nearest
```

---

### 1.4 `IFogSimConnector` - Communication avec Java

```python
class IFogSimConnector:
    def send_vehicle_data(self, vehicles: Dict, sim_time: float):
        """
        ENVOI → iFogSim (JSON):
        {
            "time": 345.0,
            "vehicles": [
                {"id": "veh_1", "x": 185.3, "y": 201.7, ...}
            ]
        }
        
        RÉCEPTION ← iFogSim (JSON):
        {
            "totalVehicles": 156,
            "fogNodes": 45,
            "latency": {"edge": 5.2, "fog": 22.4, "cloud": 125.3},
            "fogDecisions": {
                "actions": [
                    {"type": "EXTEND_GREEN", "rsu": "RSU_J1", ...}
                ]
            }
        }
        """
```

---

### 1.5 `SimulationOrchestrator` - Logique Principale

```python
class SimulationOrchestrator:
    def step(self, sim_time: float):
        """
        CYCLE PRINCIPAL (appelé chaque seconde):
        
        1. vehicles = self.sumo.step()      # Récupérer état SUMO
        2. self._update_metrics(vehicles)   # Calculer métriques
        3. self.ifogsim.send_vehicle_data() # Envoyer à iFogSim
        4. self._execute_fog_decisions()    # Exécuter décisions
        """
```

---

### 1.6 `_execute_fog_decisions` - Contrôle Intelligent des Feux

**C'est ici que se fait le CONTRÔLE ADAPTATIF des feux !**

```python
def _execute_fog_decisions(self, decisions: List[dict]):
    for decision in decisions:
        if decision["type"] == "EXTEND_GREEN":
            tl_id = decision["trafficLight"]  # Ex: "J1"
            
            # COOLDOWN: 10 secondes minimum entre changements
            if current_time - last_change < 10:
                continue
            
            # Récupérer phase actuelle (0, 1, 2, ou 3)
            current_phase = traci.trafficlight.getPhase(tl_id)
            
            # CALCUL CONGESTION ZONE
            zone_congestion = self.metrics.zone_congestion.get(rsu, 0)
            
            # === LOGIQUE DE DÉCISION ===
            if zone_congestion >= 0.9:
                # ALTERNANCE FORCÉE: basculer vers l'autre phase
                if current_phase == 0:
                    needed_phase = 2  # E-W → N-S
                else:
                    needed_phase = 0  # N-S → E-W
                
                traci.trafficlight.setPhase(tl_id, needed_phase)
                traci.trafficlight.setPhaseDuration(tl_id, 25)
            else:
                # EXTENSION: allonger la phase actuelle
                new_duration = current_duration + 8  # Max 45s
                traci.trafficlight.setPhaseDuration(tl_id, new_duration)
```

#### Phases des Feux de Circulation

| Phase | État | Direction Verte |
|-------|------|-----------------|
| 0 | Vert | Est-Ouest (horizontal) |
| 1 | Jaune | Transition |
| 2 | Vert | Nord-Sud (vertical) |
| 3 | Jaune | Transition |

---

## 🟠 2. VehicularFogSimulation.java (iFogSim)

**Chemin :** `ifogsim/src/org/fog/test/perfeval/VehicularFogSimulation.java`

### 2.1 Variables Globales

```java
// Compteurs par zone RSU
static Map<String, Integer> zoneVehicleCount = new HashMap<>();

// Métriques de latence (simulées)
static double edgeLatency = 5.0;   // Latence edge: 5ms
static double fogLatency = 22.0;  // Latence fog: 22ms
static double cloudLatency = 125.0; // Latence cloud: 125ms
```

### 2.2 Serveur Socket - `startServer()`

```java
public static void startServer() {
    ServerSocket serverSocket = new ServerSocket(5555);
    
    while (true) {
        Socket clientSocket = serverSocket.accept();
        
        // Lire JSON de Python
        String jsonInput = reader.readLine();
        
        // Traiter les données véhicules
        processVehicleData(jsonInput);
        
        // Construire et envoyer réponse
        String response = buildMetricsResponse();
        writer.println(response);
    }
}
```

### 2.3 Traitement Données - `processVehicleData()`

```java
private static void processVehicleData(String jsonData) {
    // Parser JSON avec Gson
    JsonObject data = JsonParser.parseString(jsonData).getAsJsonObject();
    JsonArray vehicles = data.getAsJsonArray("vehicles");
    
    // CALCUL: Compter véhicules par zone RSU
    zoneVehicleCount.clear();
    
    for (JsonElement veh : vehicles) {
        String rsu = veh.getAsJsonObject().get("rsu").getAsString();
        
        // Incrémenter compteur pour ce RSU
        zoneVehicleCount.merge(rsu, 1, Integer::sum);
    }
    
    // CALCUL: Mettre à jour latence fog (simulée)
    int totalVehicles = vehicles.size();
    fogLatency = 15.0 + (totalVehicles * 0.05); // Plus de véhicules = plus de latence
}
```

### 2.4 Décisions Fog - `buildFogDecisions()`

**C'est ici que le FOG PREND LES DÉCISIONS !**

```java
private static String buildFogDecisions() {
    StringBuilder sb = new StringBuilder();
    sb.append("{\"actions\":[");
    
    for (Map.Entry<String, Integer> entry : zoneVehicleCount.entrySet()) {
        String rsuId = entry.getKey();
        int vehicleCount = entry.getValue();
        
        // === CALCUL CONGESTION ===
        // Formule: congestion = min(vehicleCount / 30, 1.0)
        // 30 véhicules = 100% congestion
        double congestion = Math.min(vehicleCount / 30.0, 1.0);
        
        // === DÉCISION 1: Contrôle Feux ===
        // Seuil: 40% congestion
        if (congestion > 0.4) {
            sb.append("{");
            sb.append("\"type\":\"EXTEND_GREEN\",");
            sb.append("\"rsu\":\"" + rsuId + "\",");
            sb.append("\"trafficLight\":\"" + rsuId.replace("RSU_", "") + "\"");
            sb.append("}");
            
            System.out.println("[FOG DECISION] " + rsuId + 
                ": EXTEND_GREEN (congestion=" + congestion + ")");
        }
        
        // === DÉCISION 2: Réacheminement ===
        // Seuil: 80% congestion (désactivé actuellement)
        if (congestion > 0.8) {
            // Envoyer REROUTE_VEHICLES
        }
    }
    
    sb.append("]}");
    return sb.toString();
}
```

---

## 🟢 3. dashboard/app.js (Visualisation)

**Chemin :** `dashboard/app.js`

### 3.1 Configuration Réseau

```javascript
const RSU_POSITIONS = {
    RSU_J4: { x: 200, y: 200 },
    RSU_J3: { x: 400, y: 200 },
    RSU_J2: { x: 200, y: 400 },
    RSU_J1: { x: 400, y: 400 }
};
```

### 3.2 Réception Données - WebSocket

```javascript
function initWebSocket() {
    ws = new WebSocket('ws://localhost:5000/socket.io/');
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateDashboard(data);
    };
}
```

### 3.3 Mise à Jour Dashboard

```javascript
function updateDashboard(data) {
    // Métriques principales
    document.getElementById('vehicleCount').textContent = data.metrics.totalVehicles;
    document.getElementById('activeFogNodes').textContent = data.metrics.fogNodes;
    
    // Actions Fog
    document.getElementById('totalTlAdjusted').textContent = 
        data.fogActions?.totalTlAdjusted || 0;
    
    // Rendu graphique
    renderTrafficMap(data.vehicles, data.rsus);
    renderTopology(data.vehicles, data.rsus, data.metrics);
}
```

### 3.4 Rendu Carte Trafic

```javascript
function renderTrafficMap(vehicles, rsus) {
    const canvas = document.getElementById('trafficCanvas');
    const ctx = canvas.getContext('2d');
    
    // Conversion coordonnées SUMO → Canvas
    function toCanvasX(x) { return x * scaleX; }
    function toCanvasY(y) { return canvas.height - (y * scaleY); }
    
    // Dessiner véhicules
    for (const veh of vehicles) {
        ctx.fillStyle = veh.isFog ? '#16a34a' : '#2563eb';
        ctx.arc(toCanvasX(veh.x), toCanvasY(veh.y), 4, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Dessiner RSUs avec zone de couverture
    for (const rsu of rsus) {
        const color = getCongestionColor(rsu.congestion);
        ctx.arc(cx, cy, 120, 0, Math.PI * 2);
        ctx.fill();
    }
}
```

---

## 📐 Formules et Calculs

### Calcul Congestion
```
congestion = min(vehicleCount / 30, 1.0)

Exemples:
- 10 véhicules → 33% congestion
- 21 véhicules → 70% congestion
- 30+ véhicules → 100% congestion
```

### Calcul Latence (simulée)
```
edgeLatency = 5.0 ms (fixe)
fogLatency = 15.0 + (totalVehicles × 0.05) ms
cloudLatency = 125.0 ms (fixe)
```

### Calcul Distance RSU
```
distance = √[(x_véhicule - x_RSU)² + (y_véhicule - y_RSU)²]
```

### Seuils de Décision
| Métrique | Seuil | Action |
|----------|-------|--------|
| Congestion > 40% | EXTEND_GREEN | Allonger vert |
| Congestion > 80% | REROUTE | Réacheminement (désactivé) |
| Congestion > 90% | ALTERNANCE | Forcer changement phase |

---

## 🔄 Flux de Données Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                       CYCLE PRINCIPAL                            │
│                    (1 itération = 1 seconde)                     │
└─────────────────────────────────────────────────────────────────┘

                           server.py
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   SUMO      │    │  iFogSim    │    │  Dashboard  │
    │  (TraCI)    │    │   (Java)    │    │   (HTML)    │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                  │                  ▲
           │                  │                  │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────┴──────┐
    │ Positions   │    │ Calcul      │    │ Affichage   │
    │ Vitesses    │───►│ Congestion  │───►│ Temps Réel  │
    │ Routes      │    │ Décisions   │    │ Métriques   │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                  │
           │                  │
    ┌──────▼──────────────────▼──────┐
    │       EXÉCUTION TraCI           │
    │  - setPhase()                   │
    │  - setPhaseDuration()           │
    └─────────────────────────────────┘
```

---

## 📝 Résumé des Fichiers

| Fichier | Lignes | Rôle Principal |
|---------|--------|----------------|
| `server.py` | ~770 | Orchestration, TraCI, WebSocket |
| `VehicularFogSimulation.java` | ~312 | Serveur Fog, décisions |
| `app.js` | ~420 | Visualisation Canvas |
| `index.html` | ~200 | Structure dashboard |
| `styles.css` | ~350 | Styles visuels |

---

*Documentation générée pour le projet Fog Computing Véhiculaire*
