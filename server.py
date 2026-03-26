"""
Serveur Principal - Orchestrateur Simulation Fog Véhiculaire
Intègre SUMO (TraCI), iFogSim (Socket), et Dashboard (WebSocket)
Supporte 2 modes: edge_cloud, full_fog
"""
import os
import sys
import json
import time
import threading
import socket
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class SimulationMode(Enum):
    """Modes de simulation pour comparaison"""
    EDGE_CLOUD = "edge_cloud"    # Edge + Cloud (latence élevée)
    FULL_FOG = "full_fog"        # Edge + Fog (RSU + Véhicules) + Cloud


# Descriptions des modes pour affichage
MODE_DESCRIPTIONS = {
    SimulationMode.EDGE_CLOUD: {
        "name": "Edge + Cloud",
        "description": "Véhicules + Cloud distant (130ms). Coordination lente.",
        "fog_enabled": False,
        "cloud_enabled": True,
        "scoot_enabled": False  # SCOOT via cloud trop lent
    },
    SimulationMode.FULL_FOG: {
        "name": "Full Fog (Optimal)",
        "description": "Edge + RSU + Véhicules Fog + Cloud. SCOOT temps réel.",
        "fog_enabled": True,
        "cloud_enabled": True,
        "scoot_enabled": True
    }
}

# Configuration SUMO
if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

try:
    import traci
    TRACI_AVAILABLE = True
except ImportError:
    TRACI_AVAILABLE = False
    print("[Avertissement] TraCI non disponible - mode simulation uniquement")

# Configuration Flask-SocketIO
try:
    from flask import Flask, render_template, jsonify, send_from_directory
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[Avertissement] Flask non disponible - dashboard désactivé")


# Configuration
SUMO_CONFIG_DIR = Path(__file__).parent / "sumo_config"
SUMO_CONFIG = SUMO_CONFIG_DIR / "simulation.sumocfg"
IFOGSIM_PORT = 5555
DASHBOARD_PORT = 5000

# Variable globale pour la densité fog (modifiée au runtime)
current_fog_density = "high"  # "low" ou "high"

# Positions RSU (intersections)
RSU_POSITIONS = {
    "RSU_J1": (200.0, 200.0),
    "RSU_J2": (400.0, 200.0),
    "RSU_J3": (200.0, 400.0),
    "RSU_J4": (400.0, 400.0),
}
RSU_RANGE = 300.0  # mètres


@dataclass
class VehicleState:
    """État d'un véhicule"""
    id: str
    x: float
    y: float
    speed: float
    road_id: str
    type_id: str
    is_fog_node: bool = False
    nearest_rsu: str = ""
    timestamp: float = 0.0


@dataclass
class SimulationMetrics:
    """Métriques de simulation temps réel"""
    simulation_time: float = 0.0
    total_vehicles: int = 0
    fog_nodes: int = 0
    tasks_processed: int = 0
    
    # Latences mesurées (ms)
    edge_latency: float = 5.2
    fog_latency: float = 22.4
    cloud_latency: float = 125.3
    
    # Distribution traitement (%)
    edge_processing: float = 70.0
    fog_processing: float = 25.0
    cloud_processing: float = 5.0
    
    # Par zone RSU
    zone_vehicle_count: Dict[str, int] = field(default_factory=dict)
    zone_congestion: Dict[str, float] = field(default_factory=dict)
    
    # Compteurs actions Fog (pour démo)
    total_rerouted: int = 0
    total_tl_adjusted: int = 0
    incident_active: bool = False


class MetricsLogger:
    """
    Enregistre les métriques de simulation dans des fichiers CSV.
    Un fichier par métrique, séparé par scénario.
    Structure: logs/<scenario>/latency.csv, distribution.csv, etc.
    """
    
    def __init__(self, mode: 'SimulationMode', fog_density: str = "high"):
        # Déterminer le nom du scénario
        if mode == SimulationMode.EDGE_CLOUD:
            self.scenario_name = "edge_cloud"
        else:
            self.scenario_name = f"full_fog_{fog_density}"
        
        # Créer le dossier logs/<scenario>
        self.logs_dir = Path(__file__).parent / "logs" / self.scenario_name
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer les fichiers CSV avec headers
        self.files = {}
        self._init_csv("latency", ["time", "edge_ms", "fog_ms", "cloud_ms", "avg_weighted_ms"])
        self._init_csv("distribution", ["time", "edge_pct", "fog_pct", "cloud_pct"])
        self._init_csv("vehicles", ["time", "total_vehicles", "fog_nodes", "fog_ratio_pct"])
        self._init_csv("scoot_actions", ["time", "tl_adjusted_total", "rerouted_total"])
        self._init_csv("congestion", ["time", "RSU_J1", "RSU_J2", "RSU_J3", "RSU_J4", "max_congestion_pct"])
        self._init_csv("energy", ["time", "energy_per_task_mJ", "local_component_mJ", "fog_component_mJ", "cloud_component_mJ"])
        self._init_csv("tasks", ["time", "tasks_processed", "offloading_count"])
        self._init_csv("kpi", ["time", "task_completion_rate_pct", "deadline_miss_ratio_pct", "rsu_utilization_pct", "fogv_utilization_pct", "throughput_mbps", "total_tasks", "total_deadline_misses"])
        
        # Timestamp de démarrage
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Écrire un fichier info
        info_path = self.logs_dir / "simulation_info.txt"
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(f"Scenario: {self.scenario_name}\n")
            f.write(f"Started: {self.start_time}\n")
            f.write(f"Mode: {mode.value}\n")
            f.write(f"Fog density: {fog_density}\n")
            f.write(f"---\n")
            f.write(f"Files:\n")
            f.write(f"  latency.csv      - Edge/Fog/Cloud latency per step\n")
            f.write(f"  distribution.csv - Processing distribution (Edge/Fog/Cloud %)\n")
            f.write(f"  vehicles.csv     - Vehicle counts and fog ratio\n")
            f.write(f"  scoot_actions.csv- SCOOT traffic light adjustments and rerouting\n")
            f.write(f"  congestion.csv   - Per-RSU congestion levels\n")
            f.write(f"  energy.csv       - Energy consumption per task\n")
            f.write(f"  tasks.csv        - Tasks processed count\n")
        
        print(f"[MetricsLogger] Logging to: {self.logs_dir}")
    
    def _init_csv(self, name: str, headers: list):
        """Crée un fichier CSV avec les headers."""
        filepath = self.logs_dir / f"{name}.csv"
        self.files[name] = filepath
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(",".join(headers) + "\n")
    
    def _append(self, name: str, values: list):
        """Ajoute une ligne au fichier CSV."""
        filepath = self.files[name]
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(",".join(str(v) for v in values) + "\n")
    
    def log(self, metrics: SimulationMetrics, offloading_count: int = 0):
        """Enregistre toutes les métriques pour un pas de simulation."""
        t = round(metrics.simulation_time, 1)
        
        # 1. Latence
        avg_latency = (
            metrics.edge_latency * metrics.edge_processing +
            metrics.fog_latency * metrics.fog_processing +
            metrics.cloud_latency * metrics.cloud_processing
        ) / 100.0
        self._append("latency", [
            t,
            round(metrics.edge_latency, 2),
            round(metrics.fog_latency, 2),
            round(metrics.cloud_latency, 2),
            round(avg_latency, 2)
        ])
        
        # 2. Distribution du traitement
        self._append("distribution", [
            t,
            round(metrics.edge_processing, 1),
            round(metrics.fog_processing, 1),
            round(metrics.cloud_processing, 1)
        ])
        
        # 3. Véhicules
        total_v = max(metrics.total_vehicles, 1)
        fog_ratio = round((metrics.fog_nodes / total_v) * 100, 1)
        self._append("vehicles", [
            t,
            metrics.total_vehicles,
            metrics.fog_nodes,
            fog_ratio
        ])
        
        # 4. Actions SCOOT
        self._append("scoot_actions", [
            t,
            metrics.total_tl_adjusted,
            metrics.total_rerouted
        ])
        
        # 5. Congestion par zone
        cong = metrics.zone_congestion
        max_cong = round(max(cong.values()) * 100, 1) if cong else 0.0
        self._append("congestion", [
            t,
            round(cong.get("RSU_J1", 0) * 100, 1),
            round(cong.get("RSU_J2", 0) * 100, 1),
            round(cong.get("RSU_J3", 0) * 100, 1),
            round(cong.get("RSU_J4", 0) * 100, 1),
            max_cong
        ])
        
        # 6. Énergie (même formule que la présentation)
        # E_local = 500 mJ, E_fog = 115 mJ, E_cloud = 185 mJ
        e_local = (metrics.edge_processing / 100) * 500
        e_fog = (metrics.fog_processing / 100) * 115
        e_cloud = (metrics.cloud_processing / 100) * 185
        energy_total = e_local + e_fog + e_cloud
        self._append("energy", [
            t,
            round(energy_total, 1),
            round(e_local, 1),
            round(e_fog, 1),
            round(e_cloud, 1)
        ])
        
        # 7. Tâches
        self._append("tasks", [
            t,
            metrics.tasks_processed,
            offloading_count
        ])
    
    def log_kpi(self, t: float, kpi_stats: dict):
        """Enregistre les KPIs IEEE pour un pas de simulation."""
        self._append("kpi", [
            round(t, 1),
            round(kpi_stats.get('taskCompletionRate', 100.0), 2),
            round(kpi_stats.get('deadlineMissRatio', 0.0), 2),
            round(kpi_stats.get('rsuUtilization', 0.0), 2),
            round(kpi_stats.get('fogVUtilization', 0.0), 2),
            round(kpi_stats.get('throughputMbps', 0.0), 3),
            kpi_stats.get('totalTasks', 0),
            kpi_stats.get('totalDeadlineMisses', 0)
        ])
    
    def write_summary(self, metrics: SimulationMetrics):
        """Écrit un résumé final de la simulation."""
        summary_path = self.logs_dir / "summary.txt"
        
        avg_latency = (
            metrics.edge_latency * metrics.edge_processing +
            metrics.fog_latency * metrics.fog_processing +
            metrics.cloud_latency * metrics.cloud_processing
        ) / 100.0
        
        e_local = (metrics.edge_processing / 100) * 500
        e_fog = (metrics.fog_processing / 100) * 115
        e_cloud = (metrics.cloud_processing / 100) * 185
        energy_total = e_local + e_fog + e_cloud
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"=== SIMULATION SUMMARY: {self.scenario_name} ===\n")
            f.write(f"Duration: {metrics.simulation_time:.0f}s\n")
            f.write(f"Total vehicles (max): {metrics.total_vehicles}\n")
            f.write(f"Fog nodes: {metrics.fog_nodes}\n")
            f.write(f"Tasks processed: {metrics.tasks_processed}\n")
            f.write(f"\n--- Latency ---\n")
            f.write(f"Edge: {metrics.edge_latency:.1f} ms\n")
            f.write(f"Fog:  {metrics.fog_latency:.1f} ms\n")
            f.write(f"Cloud: {metrics.cloud_latency:.1f} ms\n")
            f.write(f"Average (weighted): {avg_latency:.1f} ms\n")
            f.write(f"\n--- Processing Distribution ---\n")
            f.write(f"Edge:  {metrics.edge_processing:.1f}%\n")
            f.write(f"Fog:   {metrics.fog_processing:.1f}%\n")
            f.write(f"Cloud: {metrics.cloud_processing:.1f}%\n")
            f.write(f"\n--- SCOOT Actions ---\n")
            f.write(f"Traffic lights adjusted: {metrics.total_tl_adjusted}\n")
            f.write(f"Vehicles rerouted: {metrics.total_rerouted}\n")
            f.write(f"\n--- Energy ---\n")
            f.write(f"Energy per task: {energy_total:.0f} mJ\n")
            f.write(f"  Local: {e_local:.0f} mJ ({metrics.edge_processing:.0f}%)\n")
            f.write(f"  Fog:   {e_fog:.0f} mJ ({metrics.fog_processing:.0f}%)\n")
            f.write(f"  Cloud: {e_cloud:.0f} mJ ({metrics.cloud_processing:.0f}%)\n")
            f.write(f"\n--- Congestion ---\n")
            max_cong = max(metrics.zone_congestion.values()) * 100 if metrics.zone_congestion else 0
            f.write(f"Max congestion: {max_cong:.0f}%\n")
            for rsu, cong in metrics.zone_congestion.items():
                f.write(f"  {rsu}: {cong*100:.0f}%\n")
        
        print(f"[MetricsLogger] Summary written to: {summary_path}")


class SUMOConnector:
    """Connecteur SUMO via TraCI"""
    
    def __init__(self, config_path: str, gui: bool = True):
        self.config_path = config_path
        self.gui = gui
        self.connected = False
        self.vehicles: Dict[str, VehicleState] = {}
        self.step_count = 0
        
    def connect(self) -> bool:
        """Établit connexion TraCI"""
        if not TRACI_AVAILABLE:
            print("[SUMO] TraCI non disponible")
            return False
            
        try:
            sumo_binary = "sumo-gui" if self.gui else "sumo"
            traci.start([sumo_binary, "-c", str(self.config_path)])
            self.connected = True
            print(f"[SUMO] Connecté: {self.config_path}")
            return True
        except Exception as e:
            print(f"[SUMO] Erreur connexion: {e}")
            return False
    
    def step(self) -> Dict[str, VehicleState]:
        """Avance simulation d'un pas et récupère données véhicules"""
        if not self.connected:
            return {}
        
        try:
            traci.simulationStep()
            self.step_count += 1
            
            # Récupérer tous les véhicules
            vehicle_ids = traci.vehicle.getIDList()
            current_time = traci.simulation.getTime()
            
            updated_vehicles = {}
            for veh_id in vehicle_ids:
                pos = traci.vehicle.getPosition(veh_id)
                speed = traci.vehicle.getSpeed(veh_id)
                road_id = traci.vehicle.getRoadID(veh_id)
                type_id = traci.vehicle.getTypeID(veh_id)
                
                # Déterminer si fog-capable UNIQUEMENT par le type
                # Seuls les véhicules spéciaux peuvent être Fog Nodes
                is_fog = type_id in ["fog_capable", "bus", "truck"]
                
                # Trouver RSU le plus proche
                nearest_rsu = self._find_nearest_rsu(pos[0], pos[1])
                
                state = VehicleState(
                    id=veh_id,
                    x=pos[0],
                    y=pos[1],
                    speed=speed,
                    road_id=road_id,
                    type_id=type_id,
                    is_fog_node=is_fog,
                    nearest_rsu=nearest_rsu,
                    timestamp=current_time
                )
                
                updated_vehicles[veh_id] = state
            
            self.vehicles = updated_vehicles
            return updated_vehicles
            
        except traci.exceptions.FatalTraCIError:
            self.connected = False
            return {}
    
    def _find_nearest_rsu(self, x: float, y: float) -> str:
        """Trouve RSU le plus proche"""
        nearest = ""
        min_dist = float('inf')
        
        for rsu_id, (rx, ry) in RSU_POSITIONS.items():
            dist = ((x - rx)**2 + (y - ry)**2) ** 0.5
            if dist < min_dist and dist <= RSU_RANGE:
                min_dist = dist
                nearest = rsu_id
        
        return nearest
    
    def get_simulation_time(self) -> float:
        """Retourne temps simulation"""
        if self.connected:
            return traci.simulation.getTime()
        return 0.0
    
    def is_running(self) -> bool:
        """Vérifie si simulation active"""
        if not self.connected:
            return False
        return traci.simulation.getMinExpectedNumber() > 0
    
    def control_traffic_lights(self, zone_congestion: Dict[str, float]) -> int:
        """
        Contrôle adaptatif des feux selon la congestion (décision Fog/RSU).
        Retourne le nombre de feux ajustés.
        """
        if not self.connected:
            return 0
        
        adjusted_count = 0
        rsu_to_tl = {
            "RSU_J1": "J1",
            "RSU_J2": "J2", 
            "RSU_J3": "J3",
            "RSU_J4": "J4"
        }
        
        try:
            for rsu_id, congestion in zone_congestion.items():
                tl_id = rsu_to_tl.get(rsu_id)
                if not tl_id:
                    continue
                
                # Si congestion > 50%, intervenir (seuil abaissé)
                if congestion > 0.5:
                    current_phase = traci.trafficlight.getPhase(tl_id)
                    
                    # Congestion critique > 90%: forcer alternance
                    if congestion > 0.9:
                        if current_phase in [0, 2]:
                            new_phase = 2 if current_phase == 0 else 0
                            traci.trafficlight.setPhase(tl_id, new_phase)
                            traci.trafficlight.setPhaseDuration(tl_id, 40)
                            direction = "N-S" if new_phase == 2 else "E-W"
                            print(f"[FOG CRITIQUE] {tl_id}: ALTERNANCE FORCÉE vers {direction} (congestion: {congestion:.0%})")
                            adjusted_count += 1
                    elif current_phase in [0, 2]:
                        current_duration = traci.trafficlight.getPhaseDuration(tl_id)
                        new_duration = min(current_duration + 15, 60)
                        traci.trafficlight.setPhaseDuration(tl_id, new_duration)
                        print(f"[FOG ACTION] {tl_id}: Vert étendu à {new_duration}s (congestion: {congestion:.0%})")
                        adjusted_count += 1
                        
        except Exception as e:
            print(f"[Feux] Erreur contrôle: {e}")
        
        return adjusted_count
    
    def reroute_vehicles(self, zone_congestion: Dict[str, float]) -> int:
        """
        Réachemine les véhicules si congestion > 0.6.
        Retourne le nombre de véhicules reroutés.
        """
        if not self.connected:
            return 0
        
        total_rerouted = 0
        
        try:
            # Seuil abaissé à 60%
            congested_rsus = [rsu for rsu, cong in zone_congestion.items() if cong > 0.6]
            
            if not congested_rsus:
                return 0
            
            for veh_id, veh_state in self.vehicles.items():
                if veh_state.nearest_rsu in congested_rsus:
                    try:
                        traci.vehicle.rerouteTraveltime(veh_id)
                        total_rerouted += 1
                    except:
                        pass
            
            if total_rerouted > 0:
                print(f"[FOG REROUTE] {total_rerouted} véhicules réacheminés (zones: {congested_rsus})")
                
        except Exception as e:
            print(f"[Reroute] Erreur: {e}")
        
        return total_rerouted
    
    def apply_fog_actions(self, zone_congestion: Dict[str, float]) -> tuple:
        """
        Applique les actions Fog et retourne (feux_ajustés, véhicules_reroutés).
        """
        tl_adjusted = self.control_traffic_lights(zone_congestion)
        rerouted = self.reroute_vehicles(zone_congestion)
        return (tl_adjusted, rerouted)
    
    def close(self):
        """Ferme connexion"""
        if self.connected:
            traci.close()
            self.connected = False


class TrafficDataCollector:
    """
    Collecteur de données de trafic temps réel pour l'algorithme SCOOT.
    Récupère les métriques avancées via TraCI pour chaque intersection.
    """
    
    # Mapping des edges par direction pour chaque intersection (basé sur network.net.xml)
    # Edges existants: E_J1_J2, E_J1_J3, E_J1_N1, E_J1_S1, E_J2_J1, E_J2_J4, E_J2_N2, E_J2_S2,
    #                  E_J3_J1, E_J3_J4, E_J3_N1, E_J3_N3, E_J4_J2, E_J4_J3, E_J4_N2, E_J4_N4,
    #                  E_N1_J1, E_N1_J3, E_N2_J2, E_N2_J4, E_N3_J3, E_N4_J4, E_S1_J1, E_S2_J2
    INTERSECTION_EDGES = {
        "RSU_J1": {
            "north": "E_N1_J1",      # Depuis N1 vers J1
            "south": "E_S1_J1",      # Depuis S1 vers J1 
            "east": "E_J2_J1",       # Depuis J2 vers J1
            "west": "E_J3_J1"        # Depuis J3 vers J1
        },
        "RSU_J2": {
            "north": "E_N2_J2",      # Depuis N2 vers J2
            "south": "E_S2_J2",      # Depuis S2 vers J2
            "east": "E_J4_J2",       # Depuis J4 vers J2
            "west": "E_J1_J2"        # Depuis J1 vers J2
        },
        "RSU_J3": {
            "north": "E_N1_J3",      # Depuis N1 vers J3
            "south": "E_N3_J3",      # Depuis N3 vers J3
            "east": "E_J1_J3",       # Depuis J1 vers J3
            "west": "E_J4_J3"        # Depuis J4 vers J3
        },
        "RSU_J4": {
            "north": "E_N2_J4",      # Depuis N2 vers J4
            "south": "E_N4_J4",      # Depuis N4 vers J4
            "east": "E_J2_J4",       # Depuis J2 vers J4
            "west": "E_J3_J4"        # Depuis J3 vers J4
        }
    }
    
    def collect_all_intersections(self) -> dict:
        """
        Collecte les données de trafic pour toutes les intersections.
        Retourne un dictionnaire formaté pour SCOOT.
        """
        if not TRACI_AVAILABLE:
            return {}
        
        traffic_data = {}
        for rsu_id in RSU_POSITIONS.keys():
            traffic_data[rsu_id] = self.collect_intersection_data(rsu_id)
        
        return traffic_data
    
    def collect_intersection_data(self, rsu_id: str) -> dict:
        """
        Collecte les données de trafic pour une intersection spécifique.
        
        Retourne:
        - queueLength: longueur de file (mètres) par direction
        - vehicleCount: nombre de véhicules par direction
        - occupancy: taux d'occupation (0-1) par direction
        - waitingTime: temps d'attente moyen (s) par direction
        - currentPhase: phase actuelle du feu
        - phaseTime: temps écoulé dans la phase actuelle
        """
        data = {
            "queueLength": {},
            "vehicleCount": {},
            "occupancy": {},
            "waitingTime": {},
            "currentPhase": 0,
            "phaseTime": 0
        }
        
        edges = self.INTERSECTION_EDGES.get(rsu_id, {})
        tl_id = rsu_id.replace("RSU_", "")
        
        for direction, edge_id in edges.items():
            if edge_id is None:
                data["queueLength"][direction] = 0
                data["vehicleCount"][direction] = 0
                data["occupancy"][direction] = 0
                data["waitingTime"][direction] = 0
                continue
            
            try:
                # Nombre de véhicules sur l'edge
                veh_count = traci.edge.getLastStepVehicleNumber(edge_id)
                data["vehicleCount"][direction] = veh_count
                
                # Longueur de file (véhicules arrêtés)
                halting_count = traci.edge.getLastStepHaltingNumber(edge_id)
                # Estimer longueur de file (7m par véhicule en moyenne)
                data["queueLength"][direction] = halting_count * 7.0
                
                # Taux d'occupation (0-1)
                occupancy = traci.edge.getLastStepOccupancy(edge_id)
                data["occupancy"][direction] = min(occupancy / 100.0, 1.0)
                
                # Temps d'attente cumulé des véhicules
                waiting_time = traci.edge.getWaitingTime(edge_id)
                avg_waiting = waiting_time / max(veh_count, 1)
                data["waitingTime"][direction] = avg_waiting
                
            except Exception as e:
                data["queueLength"][direction] = 0
                data["vehicleCount"][direction] = 0
                data["occupancy"][direction] = 0
                data["waitingTime"][direction] = 0
        
        # Données du feu de circulation
        try:
            data["currentPhase"] = traci.trafficlight.getPhase(tl_id)
            # Temps dans la phase actuelle
            next_switch = traci.trafficlight.getNextSwitch(tl_id)
            current_time = traci.simulation.getTime()
            program = traci.trafficlight.getAllProgramLogics(tl_id)[0]
            current_phase_duration = program.phases[data["currentPhase"]].duration
            data["phaseTime"] = int(current_phase_duration - (next_switch - current_time))
        except Exception as e:
            data["currentPhase"] = 0
            data["phaseTime"] = 0
        
        return data


class IFogSimConnector:
    """Connecteur vers iFogSim Java via Socket"""
    
    def __init__(self, port: int = IFOGSIM_PORT):
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.metrics = SimulationMetrics()
        self.fog_decisions: List[dict] = []  # Décisions reçues du niveau Fog
        self.scoot_decisions: dict = {}  # Décisions SCOOT reçues
        self.offloading_vehicle_ids: set = set()  # IDs des véhicules en offloading
        self.traffic_collector = TrafficDataCollector()  # Collecteur SCOOT
        self.mobility_stats: dict = {}  # Stats conscience de la mobilité
    
    def connect(self) -> bool:
        """Connecte au serveur iFogSim"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('localhost', self.port))
            self.connected = True
            print(f"[iFogSim] Connecté sur port {self.port}")
            return True
        except Exception as e:
            print(f"[iFogSim] Connexion échouée: {e}")
            return False
    
    def send_vehicle_data(self, vehicles: Dict[str, VehicleState], sim_time: float):
        """Envoie données véhicules et données de trafic SCOOT à iFogSim"""
        if not self.connected:
            return
        
        # Collecter les données de trafic pour SCOOT
        traffic_data = self.traffic_collector.collect_all_intersections()
        
        data = {
            "time": sim_time,
            "vehicles": [
                {
                    "id": v.id,
                    "x": v.x,
                    "y": v.y,
                    "speed": v.speed,
                    "type": v.type_id,
                    "is_fog": v.is_fog_node,
                    "rsu": v.nearest_rsu
                }
                for v in vehicles.values()
            ],
            "trafficData": traffic_data  # Données SCOOT
        }
        
        try:
            msg = json.dumps(data) + "\n"
            self.socket.sendall(msg.encode())
            
            # Recevoir métriques
            response = self.socket.recv(4096).decode()
            if response:
                self._parse_metrics(json.loads(response))
                
        except Exception as e:
            print(f"[iFogSim] Erreur envoi: {e}")
            self.connected = False
    
    def _parse_metrics(self, data: dict):
        """Parse métriques et décisions iFogSim"""
        self.metrics.simulation_time = data.get("time", 0)
        self.metrics.total_vehicles = data.get("totalVehicles", 0)
        self.metrics.fog_nodes = data.get("fogNodes", 0)
        self.metrics.tasks_processed = data.get("tasksProcessed", 0)
        
        latency = data.get("latency", {})
        self.metrics.edge_latency = latency.get("edge", 5.2)
        self.metrics.fog_latency = latency.get("fog", 22.4)
        self.metrics.cloud_latency = latency.get("cloud", 250.0)
        
        # Parser les statistiques d'offloading
        offloading_stats = data.get("offloadingStats", {})
        self.offloading_vehicle_ids = set(offloading_stats.get("offloadingVehicleIds", []))
        
        # Mettre à jour distribution dynamique depuis iFogSim
        # iFogSim envoie: local, fogVehicle, rsu, cloud
        # Dashboard attend: edge, fog, cloud
        distribution = offloading_stats.get("distribution", {})
        # local = traitement local sur le véhicule (edge)
        # fogVehicle + rsu = traitement fog (véhicules fog + RSU)
        # cloud = traitement cloud
        local_pct = distribution.get("local", 60.0)
        fog_vehicle_pct = distribution.get("fogVehicle", 15.0)
        rsu_pct = distribution.get("rsu", 20.0)
        cloud_pct = distribution.get("cloud", 5.0)
        
        # Mapping vers le modèle dashboard
        self.metrics.edge_processing = local_pct
        self.metrics.fog_processing = fog_vehicle_pct + rsu_pct  # Fog = V2V + RSU
        self.metrics.cloud_processing = cloud_pct
        
        if self.offloading_vehicle_ids:
            print(f"[iFogSim] {len(self.offloading_vehicle_ids)} véhicule(s) en offloading")
        
        # Parser les décisions Fog (prises par iFogSim/RSU)
        fog_decisions = data.get("fogDecisions", {})
        self.fog_decisions = fog_decisions.get("actions", [])
        
        if self.fog_decisions:
            print(f"[iFogSim] Reçu {len(self.fog_decisions)} décision(s) Fog")
        
        # Parser les décisions SCOOT
        self.scoot_decisions = data.get("scootDecisions", {})
        scoot_actions = self.scoot_decisions.get("actions", [])
        if scoot_actions:
            print(f"[SCOOT] Reçu {len(scoot_actions)} décision(s) SCOOT - Cycle: {self.scoot_decisions.get('globalCycleTime', 60)}s")
        
        # Parser les stats de mobilité
        self.mobility_stats = data.get("mobilityStats", {})
        
        # Parser les KPIs IEEE
        self.kpi_stats = data.get("kpiStats", {})
    
    def close(self):
        """Ferme connexion"""
        if self.socket:
            self.socket.close()
            self.connected = False


class SimulationOrchestrator:
    """Orchestrateur principal de la simulation"""
    
    def __init__(self, sumo_config: str, use_gui: bool = True, mode: SimulationMode = SimulationMode.FULL_FOG):
        self.sumo = SUMOConnector(sumo_config, use_gui)
        self.ifogsim = IFogSimConnector()
        self.metrics = SimulationMetrics()
        self.running = False
        self.dashboard_data = {}
        # Cooldown pour éviter changements de feux trop fréquents
        self.last_tl_change = {}  # {tl_id: simulation_time}
        
        # Mode de simulation
        self.mode = mode
        self.mode_config = MODE_DESCRIPTIONS[mode]
        
        # Compteurs pour statistiques par mode
        self.tasks_edge = 0
        self.tasks_fog_rsu = 0
        self.tasks_fog_vehicle = 0
        self.tasks_cloud = 0
        
        # Logger de métriques
        self.logger = MetricsLogger(mode, current_fog_density)
        
    def start(self):
        """Démarre la simulation"""
        print(f"[Orchestrateur] Démarrage simulation en mode: {self.mode_config['name']}")
        
        # Connecter SUMO
        if not self.sumo.connect():
            print("[Orchestrateur] Impossible de connecter SUMO")
            return False
        
        # Connecter iFogSim seulement si Fog est activé
        if self.mode_config['fog_enabled']:
            self.ifogsim.connect()
        else:
            print(f"[{self.mode.value}] Fog désactivé - pas de connexion iFogSim")
        
        self.running = True
        return True
    
    def step(self) -> dict:
        """Exécute un pas de simulation"""
        if not self.running:
            return {}
        
        # Récupérer données SUMO
        vehicles = self.sumo.step()
        sim_time = self.sumo.get_simulation_time()
        
        # Mettre à jour métriques
        self._update_metrics(vehicles, sim_time)
        
        # ===== COMPORTEMENT SELON LE MODE =====
        
        if self.mode == SimulationMode.EDGE_CLOUD:
            # MODE A: Edge + Cloud (latence élevée, pas de fog)
            self._step_edge_cloud(vehicles, sim_time)
        else:  # FULL_FOG
            # MODE B: Full Fog - RSU + Véhicules Fog + SCOOT
            self._step_full_fog(vehicles, sim_time)
        
        # ===== LOG RÉSUMÉ (toutes les 30 secondes) =====
        if int(sim_time) % 30 == 0 and int(sim_time) > 0:
            self._print_summary(sim_time)
        
        # Préparer données dashboard
        self.dashboard_data = self._prepare_dashboard_data(vehicles, sim_time)
        
        # Logger les métriques (toutes les 1s de simulation)
        if int(sim_time * 10) % 10 == 0:  # Chaque seconde
            offloading = self.metrics.fog_nodes if self.mode_config['fog_enabled'] else 0
            self.logger.log(self.metrics, offloading)
            # Logger les KPIs IEEE
            if self.ifogsim.connected and self.ifogsim.kpi_stats:
                self.logger.log_kpi(sim_time, self.ifogsim.kpi_stats)
        
        # Vérifier fin simulation
        if not self.sumo.is_running():
            self.running = False
        
        return self.dashboard_data
    
    
    def _step_edge_cloud(self, vehicles: Dict, sim_time: float):
        """Mode Edge + Cloud: traitement local avec fallback cloud (lent)"""
        fog_capable_count = sum(1 for v in vehicles.values() if v.is_fog_node)
        normal_count = len(vehicles) - fog_capable_count
        
        # Véhicules fog-capable: traitement local
        self.tasks_edge += fog_capable_count
        
        # Véhicules normaux: envoi au cloud (simulation latence)
        cloud_delay = 130.0  # ms - latence cloud typique
        self.tasks_cloud += normal_count
        
        # Décisions Fog basiques via Cloud (très lentes)
        # SCOOT désactivé car trop lent via cloud
        if int(sim_time) % 5 == 0:  # Décisions lentes toutes les 5s
            congestion_zones = [rsu for rsu, cong in self.metrics.zone_congestion.items() if cong > 0.7]
            if congestion_zones:
                # Reroutage lent
                rerouted = self.sumo.reroute_vehicles(self.metrics.zone_congestion)
                self.metrics.total_rerouted += rerouted
        
        # Latences pour ce mode
        self.metrics.edge_latency = 5.0
        self.metrics.fog_latency = 0.0  # Pas de fog
        self.metrics.cloud_latency = cloud_delay
        
        # Distribution: edge + cloud
        if len(vehicles) > 0:
            edge_pct = (fog_capable_count / len(vehicles)) * 100
            cloud_pct = 100 - edge_pct
        else:
            edge_pct, cloud_pct = 50, 50
        self.metrics.edge_processing = edge_pct
        self.metrics.fog_processing = 0.0
        self.metrics.cloud_processing = cloud_pct
    
    def _step_full_fog(self, vehicles: Dict, sim_time: float):
        """Mode Full Fog: RSU + Véhicules Fog + SCOOT (optimal)"""
        # Envoyer à iFogSim si connecté
        if self.ifogsim.connected:
            self.ifogsim.send_vehicle_data(vehicles, sim_time)
            
            # Préserver les compteurs locaux avant de récupérer les métriques iFogSim
            saved_rerouted = self.metrics.total_rerouted
            saved_tl_adjusted = self.metrics.total_tl_adjusted
            saved_incident = self.metrics.incident_active
            
            self.metrics = self.ifogsim.metrics
            
            # Restaurer les compteurs
            self.metrics.total_rerouted = saved_rerouted
            self.metrics.total_tl_adjusted = saved_tl_adjusted
            self.metrics.incident_active = saved_incident
            
            # ===== EXÉCUTER DÉCISIONS FOG (SEULEMENT si fog activé) =====
            if self.mode_config.get("fog_enabled", False):
                if self.ifogsim.fog_decisions:
                    self._execute_fog_decisions(self.ifogsim.fog_decisions)
                else:
                    # Fallback: décisions locales si pas de décisions reçues
                    tl_adj, rerouted = self.sumo.apply_fog_actions(self.metrics.zone_congestion)
                    self.metrics.total_tl_adjusted += tl_adj
                    self.metrics.total_rerouted += rerouted
            
            # ===== EXÉCUTER DÉCISIONS SCOOT (SEULEMENT si SCOOT activé) =====
            if self.mode_config.get("scoot_enabled", False):
                if self.ifogsim.scoot_decisions:
                    self._execute_scoot_decisions(self.ifogsim.scoot_decisions)
        else:
            # Fallback: décisions locales SEULEMENT si fog activé et iFogSim non connecté
            if self.mode_config.get("fog_enabled", False):
                tl_adj, rerouted = self.sumo.apply_fog_actions(self.metrics.zone_congestion)
                self.metrics.total_tl_adjusted += tl_adj
                self.metrics.total_rerouted += rerouted
    
    def _simulate_incident(self, sim_time: float):
        """Simule un incident entre T=400 et T=450 en ralentissant une lane"""
        if 400 <= sim_time < 450:
            if not self.metrics.incident_active:
                self.metrics.incident_active = True
                try:
                    # Réduire la vitesse max sur une edge (simule accident)
                    traci.edge.setMaxSpeed("E_N1_J1", 2.0)  # 2 m/s = ~7 km/h
                    print(f"\n{'='*60}")
                    print(f"[INCIDENT] ⚠️  ACCIDENT SIMULÉ sur E_N1_J1 (T={sim_time:.0f}s)")
                    print(f"[INCIDENT] Vitesse réduite à 7 km/h - Congestion attendue!")
                    print(f"{'='*60}\n")
                except:
                    pass
        elif sim_time >= 450 and self.metrics.incident_active:
            self.metrics.incident_active = False
            try:
                traci.edge.setMaxSpeed("E_N1_J1", 13.89)  # Retour à 50 km/h
                print(f"\n{'='*60}")
                print(f"[INCIDENT] ✓ Incident terminé - Vitesse normale restaurée (T={sim_time:.0f}s)")
                print(f"{'='*60}\n")
            except:
                pass
    
    def _print_summary(self, sim_time: float):
        """Affiche un résumé périodique pour la présentation"""
        phase = "NORMAL" if sim_time < 300 else ("CONGESTION" if sim_time < 600 else "RÉCUPÉRATION")
        max_congestion = max(self.metrics.zone_congestion.values()) if self.metrics.zone_congestion else 0
        
        print(f"\n{'─'*60}")
        print(f"[RÉSUMÉ T={sim_time:.0f}s] Phase: {phase}")
        print(f"  Véhicules: {self.metrics.total_vehicles} | Fog Nodes: {self.metrics.fog_nodes}")
        print(f"  Feux ajustés: {self.metrics.total_tl_adjusted} | Reroutés: {self.metrics.total_rerouted}")
        print(f"  Congestion max: {max_congestion:.0%}")
        if self.metrics.incident_active:
            print(f"  INCIDENT ACTIF")
        print(f"{'─'*60}\n")
    
    def _execute_fog_decisions(self, decisions: List[dict]):
        """
        Exécute les décisions prises par le niveau Fog (iFogSim).
        Les décisions viennent du RSU, pas de l'orchestrateur.
        """
        if not decisions:
            return
        
        for decision in decisions:
            action_type = decision.get("type")
            rsu = decision.get("rsu", "")
            
            if action_type == "EXTEND_GREEN":
                # Exécuter dans SUMO: contrôle INTELLIGENT du feu
                tl_id = decision.get("trafficLight", rsu.replace("RSU_", ""))
                
                # Vérifier cooldown (10 secondes minimum entre changements)
                current_time = self.metrics.simulation_time
                last_change = self.last_tl_change.get(tl_id, 0)
                if current_time - last_change < 10:
                    continue
                
                try:
                    current_phase = traci.trafficlight.getPhase(tl_id)
                    
                    # Compter véhicules en attente sur les lanes contrôlées
                    ns_waiting = 0
                    ew_waiting = 0
                    
                    # Compter tous les véhicules arrêtés près de cette jonction
                    for veh_id, veh in self.sumo.vehicles.items():
                        if veh.nearest_rsu == rsu and veh.speed < 1.5:
                            road = veh.road_id
                            # Détecter direction par le nom de la route:
                            # Routes verticales (N-S): contiennent "N" ou "S" suivi d'un chiffre
                            # Routes horizontales (E-W): contiennent "J" suivi d'un chiffre vers autre "J"
                            if "_N" in road or "_S" in road:
                                ns_waiting += 1
                            else:
                                ew_waiting += 1
                    
                    # Logique de décision améliorée
                    # Si le feu actuel est en phase jaune (1 ou 3), ne pas forcer
                    if current_phase in [1, 3]:
                        continue
                    
                    # Calculer congestion totale pour cette zone
                    zone_congestion = self.metrics.zone_congestion.get(rsu, 0)
                    
                    # ===== CORRECTION DEADLOCK J4 =====
                    # Si des véhicules attendent dans la direction OPPOSÉE, forcer alternance
                    # Phase 0 = E-W vert, Phase 2 = N-S vert
                    current_is_ew = (current_phase == 0)
                    opposite_waiting = ns_waiting if current_is_ew else ew_waiting
                    current_waiting = ew_waiting if current_is_ew else ns_waiting
                    
                    # Vérifier temps depuis dernier changement
                    time_in_phase = current_time - last_change
                    
                    # RÈGLE 1: Si congestion critique >90%, forcer alternance immédiate
                    if zone_congestion >= 0.9:
                        needed_phase = 2 if current_is_ew else 0
                        traci.trafficlight.setPhase(tl_id, needed_phase)
                        traci.trafficlight.setPhaseDuration(tl_id, 25)
                        direction = "N-S" if needed_phase == 2 else "E-W"
                        print(f"[EXEC FOG→SUMO] {tl_id}: ALTERNANCE FORCÉE vers {direction} (congestion critique)")
                    
                    # RÈGLE 2: Si véhicules attendent dans l'autre direction depuis >15s
                    elif opposite_waiting > 0 and time_in_phase > 15:
                        needed_phase = 2 if current_is_ew else 0
                        traci.trafficlight.setPhase(tl_id, needed_phase)
                        traci.trafficlight.setPhaseDuration(tl_id, 30)
                        direction = "N-S" if needed_phase == 2 else "E-W"
                        print(f"[EXEC FOG→SUMO] {tl_id}: Alternance vers {direction} ({opposite_waiting} veh. en attente)")
                    
                    # RÈGLE 3: Basculer si beaucoup plus de véhicules dans l'autre direction
                    elif opposite_waiting > current_waiting + 3:
                        needed_phase = 2 if current_is_ew else 0
                        traci.trafficlight.setPhase(tl_id, needed_phase)
                        traci.trafficlight.setPhaseDuration(tl_id, 35)
                        direction = "N-S" if needed_phase == 2 else "E-W"
                        print(f"[EXEC FOG→SUMO] {tl_id}: BASCULÉ vers {direction} - NS:{ns_waiting} EW:{ew_waiting}")
                    
                    # RÈGLE 4: Sinon, extension modérée SEULEMENT si pas de véhicules opposés
                    elif opposite_waiting == 0 and current_waiting > 0:
                        new_duration = min(traci.trafficlight.getPhaseDuration(tl_id) + 5, 40)
                        traci.trafficlight.setPhaseDuration(tl_id, new_duration)
                        direction = "N-S" if current_phase == 2 else "E-W"
                        print(f"[EXEC FOG→SUMO] {tl_id}: Vert {direction} étendu à {new_duration:.0f}s")
                    
                    self.last_tl_change[tl_id] = current_time
                    self.metrics.total_tl_adjusted += 1
                        
                except Exception as e:
                    print(f"[EXEC] Erreur feu {tl_id}: {e}")
            
            elif action_type == "REROUTE_VEHICLES":
                # Réacheminement des véhicules dans les zones congestionnées
                try:
                    affected_count = decision.get("affectedVehicles", 0)
                    rerouted = 0
                    
                    for veh_id, veh_state in self.sumo.vehicles.items():
                        if veh_state.nearest_rsu == rsu:
                            try:
                                traci.vehicle.rerouteTraveltime(veh_id)
                                rerouted += 1
                            except:
                                pass
                    
                    if rerouted > 0:
                        self.metrics.total_rerouted += rerouted
                        print(f"[EXEC FOG→SUMO] {rsu}: {rerouted} véhicules REROUTÉS")
                        
                except Exception as e:
                    print(f"[EXEC] Erreur rerouting {rsu}: {e}")
            
            elif action_type == "CRITICAL_CONGESTION":
                # CONGESTION CRITIQUE: action d'urgence maximale
                try:
                    tl_id = rsu.replace("RSU_", "")
                    congestion_level = decision.get("congestionLevel", 1.0)
                    
                    # 1. Forcer alternance immédiate des feux
                    current_phase = traci.trafficlight.getPhase(tl_id)
                    if current_phase in [0, 2]:
                        new_phase = 2 if current_phase == 0 else 0
                        traci.trafficlight.setPhase(tl_id, new_phase)
                        traci.trafficlight.setPhaseDuration(tl_id, 45)
                    
                    # 2. Rerouter TOUS les véhicules de la zone
                    critical_rerouted = 0
                    for veh_id, veh_state in self.sumo.vehicles.items():
                        if veh_state.nearest_rsu == rsu:
                            try:
                                # Forcer un nouveau chemin
                                traci.vehicle.rerouteTraveltime(veh_id)
                                critical_rerouted += 1
                            except:
                                pass
                    
                    self.metrics.total_rerouted += critical_rerouted
                    self.metrics.total_tl_adjusted += 1
                    
                    print(f"[EXEC CRITIQUE] {rsu}: URGENCE - {critical_rerouted} véhicules reroutés, feu basculé!")
                    
                except Exception as e:
                    print(f"[EXEC] Erreur gestion critique {rsu}: {e}")
    
    def _get_congested_edges(self, rsu: str) -> List[str]:
        """
        Retourne les edges (routes) proches d'un RSU congestionné.
        Cela permet à SUMO de savoir quelles routes éviter.
        """
        # Mapping RSU -> edges à proximité
        rsu_edges = {
            "RSU_J1": ["E_J3_J1", "E_N1_J1", "E_S1_J1", "E_J2_J1"],
            "RSU_J2": ["E_J4_J2", "E_N2_J2", "E_S2_J2", "E_J1_J2"],
            "RSU_J3": ["E_N3_J3", "E_J4_J3", "E_J1_J3", "E_N1_J3"],
            "RSU_J4": ["E_N4_J4", "E_J3_J4", "E_J2_J4", "E_N2_J4"],
        }
        return rsu_edges.get(rsu, [])
    
    def _execute_scoot_decisions(self, scoot_data: dict):
        """
        Exécute les décisions SCOOT prises par le niveau Fog (iFogSim).
        Implémente:
        - SCOOT_SPLIT: Ajustement durée des phases
        - SCOOT_OFFSET: Coordination des offsets entre intersections
        - SCOOT_CYCLE: Modification du temps de cycle global
        """
        if not scoot_data or not self.sumo.connected:
            return
        
        actions = scoot_data.get("actions", [])
        if not actions:
            return
        
        for decision in actions:
            action_type = decision.get("type")
            tl_id = decision.get("trafficLight", "")
            rsu_id = decision.get("rsu", "")
            
            if action_type == "SCOOT_SPLIT":
                # Ajuster la durée des phases
                phase_durations = decision.get("phaseDurations", [])
                if not phase_durations or len(phase_durations) < 4:
                    continue
                
                try:
                    # Récupérer le programme actuel
                    programs = traci.trafficlight.getAllProgramLogics(tl_id)
                    if not programs:
                        continue
                    
                    program = programs[0]
                    phases = list(program.phases)
                    
                    # Mettre à jour les durées des phases
                    for i, duration in enumerate(phase_durations):
                        if i < len(phases):
                            phases[i] = traci.trafficlight.Phase(
                                duration=duration,
                                state=phases[i].state,
                                minDur=max(5, duration - 10),
                                maxDur=duration + 10
                            )
                    
                    # Appliquer le nouveau programme
                    new_program = traci.trafficlight.Logic(
                        programID=program.programID,
                        type=program.type,
                        currentPhaseIndex=traci.trafficlight.getPhase(tl_id),
                        phases=phases,
                        subParameter=program.subParameter
                    )
                    traci.trafficlight.setProgramLogic(tl_id, new_program)
                    
                    reason = decision.get("reason", "")
                    pi = decision.get("performanceIndex", 0)
                    print(f"[SCOOT SPLIT] {tl_id}: EW={phase_durations[0]}s, NS={phase_durations[2]}s (PI={pi:.2f}, {reason})")
                    self.metrics.total_tl_adjusted += 1
                    
                except Exception as e:
                    print(f"[SCOOT] Erreur SPLIT {tl_id}: {e}")
            
            elif action_type == "SCOOT_OFFSET":
                # Ajuster l'offset pour la coordination green wave
                offset = decision.get("offset", 0)
                ref_rsu = decision.get("referenceRSU", "")
                
                try:
                    # L'offset se traduit par un décalage du début de cycle
                    # Dans SUMO, on peut simuler ça en changeant la phase de départ
                    current_phase = traci.trafficlight.getPhase(tl_id)
                    programs = traci.trafficlight.getAllProgramLogics(tl_id)
                    
                    if programs:
                        program = programs[0]
                        # Calculer dans quelle phase on devrait être avec l'offset
                        # (simplifié - dans la réalité c'est plus complexe)
                        cycle_time = sum(p.duration for p in program.phases)
                        if cycle_time > 0:
                            offset_phase = int((offset / cycle_time) * len(program.phases)) % len(program.phases)
                            if offset_phase != current_phase:
                                traci.trafficlight.setPhase(tl_id, offset_phase)
                                print(f"[SCOOT OFFSET] {tl_id}: offset={offset}s (ref: {ref_rsu})")
                    
                except Exception as e:
                    print(f"[SCOOT] Erreur OFFSET {tl_id}: {e}")
            
            elif action_type == "SCOOT_CYCLE":
                # Modification du temps de cycle global
                cycle_time = decision.get("cycleTime", 60)
                reason = decision.get("reason", "")
                
                try:
                    # Appliquer à tous les feux du réseau
                    for tl in ["J1", "J2", "J3", "J4"]:
                        programs = traci.trafficlight.getAllProgramLogics(tl)
                        if not programs:
                            continue
                        
                        program = programs[0]
                        phases = list(program.phases)
                        
                        # Calculer le ratio de mise à l'échelle
                        current_cycle = sum(p.duration for p in phases)
                        if current_cycle > 0:
                            scale = cycle_time / current_cycle
                            
                            for i in range(len(phases)):
                                new_dur = int(phases[i].duration * scale)
                                phases[i] = traci.trafficlight.Phase(
                                    duration=max(5, new_dur),
                                    state=phases[i].state,
                                    minDur=max(3, new_dur - 5),
                                    maxDur=new_dur + 5
                                )
                            
                            new_program = traci.trafficlight.Logic(
                                programID=program.programID,
                                type=program.type,
                                currentPhaseIndex=traci.trafficlight.getPhase(tl),
                                phases=phases,
                                subParameter=program.subParameter
                            )
                            traci.trafficlight.setProgramLogic(tl, new_program)
                    
                    print(f"[SCOOT CYCLE] Réseau: {cycle_time}s ({reason})")
                    
                except Exception as e:
                    print(f"[SCOOT] Erreur CYCLE: {e}")
    
    def _update_metrics(self, vehicles: Dict[str, VehicleState], sim_time: float):
        """Met à jour métriques locales"""
        self.metrics.simulation_time = sim_time
        self.metrics.total_vehicles = len(vehicles)
        self.metrics.fog_nodes = sum(1 for v in vehicles.values() if v.is_fog_node)
        self.metrics.tasks_processed += len(vehicles)
        
        # Compter par zone RSU
        zone_counts = {rsu: 0 for rsu in RSU_POSITIONS}
        for v in vehicles.values():
            if v.nearest_rsu:
                zone_counts[v.nearest_rsu] += 1
        
        self.metrics.zone_vehicle_count = zone_counts
        
        # Calculer congestion par zone
        for rsu, count in zone_counts.items():
            self.metrics.zone_congestion[rsu] = min(count / 30.0, 1.0)
        
        # === MÉTRIQUES DYNAMIQUES BASÉES SUR LA DENSITÉ FOG ===
        total_v = max(self.metrics.total_vehicles, 1)
        fog_ratio = self.metrics.fog_nodes / total_v
        
        if self.ifogsim.connected:
            # iFogSim connecté → utiliser les VRAIES latences et distribution
            # Les latences sont déjà mises à jour dans _parse_metrics()
            # Rien à faire ici, on garde les valeurs reçues de iFogSim
            pass
        else:
            # FALLBACK quand iFogSim non connecté
            import math
            if self.mode_config["fog_enabled"]:
                # Latences approximatives basées sur le ratio fog
                self.metrics.fog_latency = 50.0 * math.exp(-3.0 * fog_ratio)
                self.metrics.fog_latency = max(10.0, min(50.0, self.metrics.fog_latency))
                self.metrics.edge_latency = 8.0 - (fog_ratio * 5.0)
                self.metrics.edge_latency = max(3.0, self.metrics.edge_latency)
                self.metrics.cloud_latency = 250.0
                
                # Distribution approximative
                self.metrics.fog_processing = 10.0 + (fog_ratio * 80.0)
                self.metrics.edge_processing = 75.0 - (fog_ratio * 60.0)
                self.metrics.cloud_processing = max(3.0, 15.0 - (fog_ratio * 20.0))
                
                # Normaliser à 100%
                total_pct = self.metrics.edge_processing + self.metrics.fog_processing + self.metrics.cloud_processing
                if total_pct > 0:
                    self.metrics.edge_processing = (self.metrics.edge_processing / total_pct) * 100
                    self.metrics.fog_processing = (self.metrics.fog_processing / total_pct) * 100
                    self.metrics.cloud_processing = (self.metrics.cloud_processing / total_pct) * 100
            else:
                # Mode Edge+Cloud: pas de fog, beaucoup de cloud
                self.metrics.fog_latency = 0.0
                self.metrics.edge_latency = 3.0
                self.metrics.cloud_latency = 250.0
                self.metrics.fog_processing = 0.0
                self.metrics.edge_processing = 65.0
                self.metrics.cloud_processing = 35.0
    
    def _prepare_dashboard_data(self, vehicles: Dict[str, VehicleState], 
                                 sim_time: float) -> dict:
        """Prépare données pour dashboard"""
        # Phase unique: congestion
        phase = "congestion"
        
        # Récupérer les IDs des véhicules en offloading
        offloading_ids = self.ifogsim.offloading_vehicle_ids if self.ifogsim.connected else set()
        
        return {
            "time": sim_time,
            "phase": phase,
            "mode": {
                "id": self.mode.value,
                "name": self.mode_config["name"] + (f" - {current_fog_density.capitalize()} Density" if self.mode == SimulationMode.FULL_FOG else ""),
                "description": self.mode_config["description"],
                "fog_enabled": self.mode_config["fog_enabled"],
                "cloud_enabled": self.mode_config["cloud_enabled"],
                "scoot_enabled": self.mode_config["scoot_enabled"]
            },
            "vehicles": [
                {
                    "id": v.id,
                    "x": v.x,
                    "y": v.y,
                    "speed": v.speed,
                    "isFog": v.is_fog_node,
                    "isOffloading": v.id in offloading_ids,
                    "rsu": v.nearest_rsu,
                    "type": v.type_id
                }
                for v in vehicles.values()
            ],
            "rsu": [
                {
                    "id": rsu_id,
                    "x": pos[0],
                    "y": pos[1],
                    "vehicles": self.metrics.zone_vehicle_count.get(rsu_id, 0),
                    "congestion": self.metrics.zone_congestion.get(rsu_id, 0)
                }
                for rsu_id, pos in RSU_POSITIONS.items()
            ],
            "metrics": {
                "totalVehicles": self.metrics.total_vehicles,
                "fogNodes": self.metrics.fog_nodes if self.mode_config["fog_enabled"] else 0,
                "tasksProcessed": self.metrics.tasks_processed,
                # Limiter offloadingCount au nombre de véhicules actuels (éviter incohérence)
                "offloadingCount": min(len(offloading_ids), self.metrics.total_vehicles),
                "latency": {
                    "edge": self.metrics.edge_latency,
                    "fog": self.metrics.fog_latency,
                    "cloud": self.metrics.cloud_latency
                },
                "processing": {
                    "edge": self.metrics.edge_processing,
                    "fog": self.metrics.fog_processing,
                    "cloud": self.metrics.cloud_processing
                }
            },
            "fogActions": {
                "trafficLightControl": any(c > 0.7 for c in self.metrics.zone_congestion.values()),
                "vehicleRerouting": any(c > 0.8 for c in self.metrics.zone_congestion.values()),
                "congestedZones": [rsu for rsu, c in self.metrics.zone_congestion.items() if c > 0.7],
                "totalRerouted": self.metrics.total_rerouted,
                "totalTlAdjusted": self.metrics.total_tl_adjusted,
                "incidentActive": self.metrics.incident_active
            },
            "scootData": self._get_scoot_dashboard_data(),
            "mobilityData": self.ifogsim.mobility_stats if self.ifogsim.connected else {},
            "kpiData": self.ifogsim.kpi_stats if self.ifogsim.connected else {}
        }
    
    def _get_scoot_dashboard_data(self) -> dict:
        """Prépare les données SCOOT pour le dashboard"""
        # SCOOT est activé si le mode le permet ET iFogSim est connecté
        scoot_enabled = self.mode_config.get("scoot_enabled", False) and self.ifogsim.connected
        
        # Données SCOOT par défaut
        default_data = {
            "enabled": scoot_enabled,
            "globalCycleTime": 60,
            "performanceIndex": {},
            "splits": {
                "RSU_J1": [25, 5, 20, 5],
                "RSU_J2": [25, 5, 20, 5],
                "RSU_J3": [25, 5, 20, 5],
                "RSU_J4": [25, 5, 20, 5]
            },
            "offsets": {
                "RSU_J1": 0,
                "RSU_J2": 0,
                "RSU_J3": 0,
                "RSU_J4": 0
            },
            "actions": []
        }
        
        # Si pas de données SCOOT reçues, retourner les valeurs par défaut
        if not self.ifogsim.scoot_decisions:
            return default_data
        
        scoot = self.ifogsim.scoot_decisions
        return {
            "enabled": scoot_enabled,
            "globalCycleTime": scoot.get("globalCycleTime", 60),
            "performanceIndex": scoot.get("performanceIndex", {}),
            "splits": scoot.get("splits", default_data["splits"]),
            "offsets": scoot.get("offsets", default_data["offsets"]),
            "actions": scoot.get("actions", [])
        }
    
    def stop(self):
        """Arrête la simulation"""
        self.running = False
        # Écrire le résumé final des métriques
        self.logger.write_summary(self.metrics)
        self.sumo.close()
        self.ifogsim.close()
        print("[Orchestrateur] Simulation terminée")


# Application Flask pour Dashboard
if FLASK_AVAILABLE:
    app = Flask(__name__, static_folder='dashboard', template_folder='dashboard')
    socketio = SocketIO(app, cors_allowed_origins="*")
    orchestrator: Optional[SimulationOrchestrator] = None
    
    @app.route('/')
    def index():
        return send_from_directory('dashboard', 'index.html')
    
    @app.route('/styles.css')
    def styles():
        return send_from_directory('dashboard', 'styles.css')
    
    @app.route('/app.js')
    def appjs():
        return send_from_directory('dashboard', 'app.js')
    
    @app.route('/api/status')
    def status():
        if orchestrator:
            return jsonify(orchestrator.dashboard_data)
        return jsonify({"status": "idle"})
    
    @socketio.on('connect')
    def handle_connect():
        print("[Dashboard] Client connecté")
        emit('status', {'connected': True})
    
    # Variables globales pour le mode et config
    current_mode: SimulationMode = SimulationMode.FULL_FOG
    current_sumo_config = str(SUMO_CONFIG)
    
    def simulation_loop():
        """Boucle simulation en background"""
        global orchestrator, current_mode, current_sumo_config
        
        orchestrator = SimulationOrchestrator(current_sumo_config, use_gui=True, mode=current_mode)
        if not orchestrator.start():
            return
        
        while orchestrator.running:
            data = orchestrator.step()
            socketio.emit('update', data)
            time.sleep(0.5)  # 2 Hz
        
        orchestrator.stop()
    
    def run_dashboard(mode: SimulationMode = SimulationMode.FULL_FOG, fog_density: str = "high"):
        """Lance dashboard web"""
        global current_mode, current_sumo_config
        current_mode = mode
        
        # Sélectionner le bon fichier de config SUMO
        if fog_density == "low":
            current_sumo_config = str(SUMO_CONFIG_DIR / "simulation_low_fog.sumocfg")
        else:
            current_sumo_config = str(SUMO_CONFIG_DIR / "simulation_high_fog.sumocfg")
        
        # Démarrer simulation en thread séparé
        sim_thread = threading.Thread(target=simulation_loop)
        sim_thread.daemon = True
        sim_thread.start()
        
        # Lancer serveur Flask
        print(f"[Dashboard] http://localhost:{DASHBOARD_PORT}")
        socketio.run(app, host='0.0.0.0', port=DASHBOARD_PORT, debug=False)


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simulation Fog Véhiculaire")
    parser.add_argument("--gui", action="store_true", help="Lancer SUMO avec interface graphique")
    parser.add_argument("--no-gui", action="store_true", help="Mode sans interface")
    parser.add_argument("--dashboard", action="store_true", help="Lancer dashboard web")
    parser.add_argument("--test", action="store_true", help="Mode test")
    parser.add_argument("--mode", type=str, default="full_fog",
                       choices=["edge_cloud", "full_fog"],
                       help="Mode de simulation: edge_cloud, full_fog (défaut)")
    parser.add_argument("--fog-density", type=str, default="high",
                       choices=["low", "high"],
                       help="Densité de véhicules fog-capable: low (~15%%), high (~50%%, défaut)")
    
    args = parser.parse_args()
    
    # Convertir string en enum
    mode = SimulationMode(args.mode)
    mode_info = MODE_DESCRIPTIONS[mode]
    fog_density = args.fog_density
    
    # Mettre à jour la variable globale
    global current_fog_density
    current_fog_density = fog_density
    
    # Sélectionner le fichier de routes selon la densité fog
    if fog_density == "low":
        routes_file = SUMO_CONFIG_DIR / "routes_low_fog.rou.xml"
        fog_desc = "PEU de fog nodes (~15%)"
    else:
        routes_file = SUMO_CONFIG_DIR / "routes_high_fog.rou.xml"
        fog_desc = "BEAUCOUP de fog nodes (~50%)"
    
    print("=" * 60)
    print("  Simulation Fog-Assisted Vehicular Computing")
    print("  SUMO + iFogSim + Dashboard Temps Réel")
    print("=" * 60)
    print(f"\n  [MODE] {mode_info['name']}")
    print(f"  [DESC] {mode_info['description']}")
    print(f"  [DENSITY] {fog_desc}")
    print(f"  [Fog] {'ENABLED' if mode_info['fog_enabled'] else 'DISABLED'}")
    print(f"  [Cloud] {'ENABLED' if mode_info['cloud_enabled'] else 'DISABLED'}")
    print(f"  [SCOOT] {'ENABLED' if mode_info['scoot_enabled'] else 'DISABLED'}")
    print("=" * 60)
    
    if args.test:
        print("\n[Test] Vérification composants...")
        print(f"  TraCI disponible: {TRACI_AVAILABLE}")
        print(f"  Flask disponible: {FLASK_AVAILABLE}")
        print(f"  Config SUMO: {SUMO_CONFIG.exists()}")
        return
    
    if args.dashboard and FLASK_AVAILABLE:
        run_dashboard(mode, fog_density)
    else:
        # Mode simple sans dashboard
        use_gui = args.gui or not args.no_gui
        # Sélectionner le bon fichier de config
        if fog_density == "low":
            sumo_cfg = str(SUMO_CONFIG_DIR / "simulation_low_fog.sumocfg")
        else:
            sumo_cfg = str(SUMO_CONFIG_DIR / "simulation_high_fog.sumocfg")
        orchestrator = SimulationOrchestrator(sumo_cfg, use_gui, mode)
        
        if orchestrator.start():
            try:
                while orchestrator.running:
                    data = orchestrator.step()
                    if orchestrator.sumo.step_count % 100 == 0:
                        print(f"[Simulation] t={data.get('time', 0):.0f}s, "
                              f"véhicules={data.get('metrics', {}).get('totalVehicles', 0)}, "
                              f"fog_nodes={data.get('metrics', {}).get('fogNodes', 0)}")
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n[Simulation] Arrêt demandé")
            finally:
                orchestrator.stop()


if __name__ == "__main__":
    main()
