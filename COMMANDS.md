# Commandes d'Exécution des Simulations

## Prérequis

Avant de lancer une simulation, démarrer le serveur iFogSim dans un terminal séparé :

```bash
cd "c:\Users\OUSSAMA\Desktop\simulation fog&edge\ifogsim"
java -cp "out;jars/*" org.fog.test.perfeval.VehicularFogSimulation
```

> **Note** : iFogSim doit rester actif pendant toute la durée de la simulation. Il se reconnecte automatiquement entre les scénarios.

---

## Scénario 1 : Edge + Cloud (sans fog)

- **Fog** : ❌ | **Cloud** : ✅ | **SCOOT** : ❌
- **Fog nodes** : 0%
- **Latence moyenne attendue** : ~90-100 ms

```bash
python server.py --dashboard --gui --mode edge_cloud
```

---

## Scénario 2 : Full Fog — Densité Basse (10%)

- **Fog** : ✅ | **Cloud** : ✅ | **SCOOT** : ✅
- **Fog nodes** : ~10%
- **Latence moyenne attendue** : ~30-35 ms

```bash
python server.py --dashboard --gui --mode full_fog --fog-density low
```

---

## Scénario 3 : Full Fog — Densité Haute (50%)

- **Fog** : ✅ | **Cloud** : ✅ | **SCOOT** : ✅
- **Fog nodes** : ~50%
- **Latence moyenne attendue** : ~15-20 ms

```bash
python server.py --dashboard --gui --mode full_fog --fog-density high
```

---

## Options supplémentaires

| Option | Description |
|--------|-------------|
| `--dashboard` | Active le dashboard web (http://localhost:5000) |
| `--gui` | Ouvre l'interface graphique SUMO |
| `--mode` | `edge_cloud` ou `full_fog` |
| `--fog-density` | `low` (10%) ou `high` (50%) — uniquement avec `full_fog` |

---

## Recompilation iFogSim (si modification du code Java)

```bash
cd "c:\Users\OUSSAMA\Desktop\simulation fog&edge\ifogsim"
javac -cp "jars/*" -d out src/org/fog/test/perfeval/VehicularFogSimulation.java src/org/fog/test/perfeval/SCOOTController.java
```
