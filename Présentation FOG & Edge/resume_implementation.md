# 📋 Résumé de l'Implémentation — Démonstration

## Vue d'ensemble

Notre simulation combine **3 outils** qui communiquent en temps réel pour simuler un système de Fog Computing véhiculaire :

```
SUMO (trafic routier) ←→ Python/Flask (orchestrateur) ←→ iFogSim (fog computing)
                              ↓
                     Dashboard Web (temps réel)
```

---

## Architecture Technique

### 1. SUMO — Simulation du Trafic
- **Fichier réseau** : `grid_network.net.xml` — grille 4 intersections (J0-J3) avec RSU
- **Fichiers routes** : 3 fichiers `.rou.xml`, un par scénario :
  - `routes.rou.xml` → Edge+Cloud (100% voitures standard)
  - `routes_low_fog.rou.xml` → Low Fog (90% standard + 10% fog-capable)
  - `routes_high_fog.rou.xml` → High Fog (50% standard + 50% fog-capable)
- **Débit** : 2000 véhicules/heure, identique dans les 3 scénarios
- **Durée** : 300 secondes par simulation
- **Types de véhicules** :
  - `car` (bleu) : véhicule standard, traitement local uniquement
  - `fog_capable` (vert) : véhicule avec capacité fog, peut servir de relai

### 2. Python/Flask — Orchestrateur Central (`server.py`)
- **TraCI** : Contrôle SUMO en temps réel (positions, vitesses, types, feux)
- **Socket TCP (5555)** : Communication bidirectionnelle avec iFogSim
- **SCOOT Controller** : Algorithme adaptatif de gestion des feux
  - Mesure files d'attente Nord-Sud et Est-Ouest par intersection
  - Calcule le split optimal et ajuste les phases
  - Décide les reroutages quand congestion détectée
- **Dashboard Socket.IO** : Envoie les métriques au dashboard web en temps réel

### 3. iFogSim — Moteur Fog Computing (Java)
- **Fichier principal** : `VehicularFogSimulation.java`
- **Réception** : données véhicules via socket TCP depuis Python
- **Calcul de l'offloading** : pour chaque véhicule, décide où traiter la tâche :
  - **LOCAL** (3 ms) : petite tâche, faible charge CPU
  - **RSU** (7-15 ms) : véhicule dans la zone RSU, RSU non surchargé
  - **FOG_VEHICLE** (5-20 ms) : RSU surchargé mais voisin fog disponible
  - **CLOUD** (250 ms) : dernier recours, pénalité massive
- **Retour** : envoie les décisions et métriques (latences, distribution) au Python

### 4. Dashboard Web
- **Interface** : page HTML avec graphiques en temps réel
- **Affichage** :
  - Mode de simulation (Edge+Cloud / Low Fog / High Fog)
  - Nombre de véhicules actifs et fog nodes détectés
  - Latence moyenne en temps réel
  - Distribution du traitement (Edge / Fog / Cloud)
  - Statut SCOOT (actif/inactif, feux ajustés, reroutages)
  - Niveau de congestion par zone

---

## Les 3 Scénarios de la Démonstration

### 🔴 Scénario 1 : Edge + Cloud (Référence)
- **Fog** : 0% — aucun véhicule fog-capable
- **SCOOT** : Désactivé — feux statiques
- **Résultat attendu** :
  - Latence moyenne ~90 ms (beaucoup de tâches vont au Cloud à 250 ms)
  - 0 ajustement de feux, 0 reroutage
  - Congestion maximale ~77%
- **Ce qu'on observe** : trafic non optimisé, latence élevée, Cloud surchargé

### 🟠 Scénario 2 : Low Fog (10% fog nodes)
- **Fog** : 10% — 1 véhicule sur 10 est fog-capable
- **SCOOT** : Activé — feux adaptatifs
- **Résultat attendu** :
  - Latence moyenne ~35 ms (réduction de 61%)
  - ~18 ajustements de feux, ~445 reroutages
  - Le fog absorbe une partie du trafic, le Cloud diminue
- **Ce qu'on observe** : première amélioration visible, SCOOT commence à agir

### 🟢 Scénario 3 : High Fog (50% fog nodes)
- **Fog** : 50% — 1 véhicule sur 2 est fog-capable
- **SCOOT** : Activé — feux adaptatifs
- **Résultat attendu** :
  - Latence moyenne ~18 ms (réduction de 80% !)
  - ~360 ajustements de feux, ~2077 reroutages
  - 72% des tâches traitées par le fog, seulement 8% au Cloud
  - Congestion réduite à ~63%
- **Ce qu'on observe** : différence spectaculaire, trafic fluide, décisions en <50 ms

---

## Comment Lancer la Démonstration

### Étape 1 : Lancer iFogSim (Terminal Java)
```bash
cd "c:\Users\OUSSAMA\Desktop\simulation fog&edge\ifogsim"
java -cp "out;jars/*" org.fog.test.perfeval.VehicularFogSimulation
```
> iFogSim écoute sur le port 5555 et attend les connexions de Python.

### Étape 2 : Lancer le serveur Python + SUMO
```bash
cd "c:\Users\OUSSAMA\Desktop\simulation fog&edge"
python server.py --scenario edge_cloud     # Scénario 1
python server.py --scenario low_fog        # Scénario 2
python server.py --scenario high_fog       # Scénario 3
```
> SUMO-GUI s'ouvre automatiquement. Le dashboard est accessible sur `http://localhost:5000`.

### Étape 3 : Observer le Dashboard
- Ouvrir le navigateur sur `http://localhost:5000`
- Observer les métriques en temps réel pendant la simulation de 300 secondes

---

## Points Clés à Montrer pendant la Démo

| Métrique | Edge+Cloud | Low Fog | High Fog |
|----------|-----------|---------|----------|
| Latence moyenne | ~90 ms | ~35 ms | ~18 ms |
| Fog Nodes actifs | 0 | ~5 | ~18 |
| Feux ajustés | 0 | 18 | 360 |
| Véhicules reroutés | 0 | 445 | 2,077 |
| Cloud usage | 35% | 20% | 8% |
| Congestion max | 77% | 77% | 63% |

---

## Algorithmes Implémentés

### 1. Offloading Multi-Critères
- **Entrées** : charge CPU, taille tâche, congestion zone, disponibilité fog
- **Sortie** : destination optimale (LOCAL / RSU / FOG_VEHICLE / CLOUD)
- **Logique** : arbre de décision basé sur capacité RSU → overflow fog → dernier recours Cloud

### 2. SCOOT (Split Cycle Offset Optimization)
- **Entrées** : files d'attente N-S et E-W par intersection
- **Sorties** : ajustements split, extensions de vert, reroutages
- **Calcul** : Performance Index = Q_max / Q_capacity
- **Seuil** : Si PI > 0.5, action de reroutage

### 3. Latence Dynamique
- **V2V** : L = max(5, 20 - ρ_fog × 30) ms → diminue avec densité fog
- **RSU** : L = max(7, 15 - ρ_fog × 8) + (d_RSU/300) × 5 ms
- **Cloud** : 250 ms fixe (RTT incompressible)

---

## Technologies Utilisées

| Technologie | Rôle | Langage |
|-------------|------|---------|
| SUMO | Simulation trafic microscopique | XML / Config |
| iFogSim | Moteur Fog Computing | Java |
| Python/Flask | Orchestrateur + API | Python 3 |
| TraCI | Interface SUMO ↔ Python | Python |
| Socket.IO | Dashboard temps réel | JavaScript |
| Matplotlib | Génération des graphiques | Python |
| LaTeX/Beamer | Présentation | LaTeX |
