# CONTENU ACADÉMIQUE - PRÉSENTATION FOG COMPUTING VÉHICULAIRE
## Niveau Master - Contenu Détaillé par Slide

---

# SLIDE 1 : PAGE DE TITRE
**Titre :** Fog-Assisted Vehicular Fog Computing
**Sous-titre :** Architecture, Implémentation et Démonstration
**Auteur :** Master 2 - Fog & Edge Computing
**Date :** Janvier 2026

---

# SLIDE 2 : PLAN
1. Contexte, Motivation et Concepts de Base
2. Architecture Fog-Assisted Vehicular Computing
3. Vehicular Fog Nodes et Fonctionnement Interne
4. Gestion des Ressources, Mobilité et Sécurité
5. Cas Pratique : Notre Simulation
6. Avantages, Limites et Comparaison
7. Perspectives et Conclusion

---

# SLIDE 3 : PROBLÉMATIQUE DU CLOUD VÉHICULAIRE

## Limitations du Cloud Computing pour les Applications Véhiculaires

Les véhicules modernes génèrent environ **25 Go de données par heure** (capteurs LiDAR, caméras 360°, radar). Le traitement centralisé dans le Cloud présente des limitations critiques :

**Latence élevée (100-200 ms)** : Le temps aller-retour vers un datacenter distant est incompatible avec les applications temps réel. À 130 km/h, un véhicule parcourt 3,6 mètres pendant 100 ms de latence.

**Congestion du backbone** : Des millions de véhicules connectés saturent les infrastructures réseau existantes, créant des goulots d'étranglement.

**Dépendance à la connectivité** : Les zones à faible couverture (tunnels, zones rurales) rendent le Cloud inaccessible.

**Coûts prohibitifs** : La transmission de 25 Go/h × millions de véhicules représente des coûts de bande passante considérables.

## Exigences des Applications V2X (ETSI ITS)

| Application | Latence requise | Fiabilité |
|-------------|-----------------|-----------|
| Freinage coopératif | < 10 ms | 99.999% |
| Évitement de collision | < 20 ms | 99.999% |
| Gestion du trafic | < 100 ms | 99.9% |
| Infotainment | < 500 ms | 99% |

**Conclusion :** Le paradigme Cloud-centric ne peut satisfaire les exigences de latence sub-20ms des applications de sécurité véhiculaire.

**[IMAGE] Prompt :**
```
Academic infographic comparing Cloud limitations vs V2X requirements. Left panel (red): datacenter with long latency path (100-200ms arrow), congestion icon, connectivity issues. Right panel (green): car with checkmarks showing <20ms requirement, 99.999% reliability badge. Scientific diagram style, IEEE publication quality, clean white background.
```

---

# SLIDE 4 : INTRODUCTION AU FOG COMPUTING

## Définition Formelle

Le **Fog Computing** (Bonomi et al., 2012) est un paradigme distribué qui étend les services Cloud vers la périphérie du réseau, en positionnant des ressources de calcul, stockage et réseau entre les dispositifs terminaux et les datacenters Cloud.

**Caractéristiques fondamentales (OpenFog Consortium) :**

| Caractéristique | Description | Application véhiculaire |
|-----------------|-------------|------------------------|
| Proximité | Traitement à 1-2 sauts réseau | RSU à l'intersection locale |
| Distribution géographique | Nœuds dispersés | Couverture urbaine continue |
| Faible latence | 5-50 ms | Compatible freinage d'urgence |
| Hétérogénéité | Ressources variées | Véhicules + RSU + Edge servers |
| Conscience du contexte | Localisation, mobilité | Prédiction trajectoire |

## Positionnement dans le Continuum Cloud-Edge

```
Cloud (Datacenter) ←——— Fog (RSU/MEC) ←——— Edge (Véhicule)
    100-200 ms              10-50 ms            <5 ms
    Ressources ∞            Ressources moyennes  Ressources limitées
```

**Référence :** Bonomi, F., Milito, R., Zhu, J., & Addepalli, S. (2012). Fog computing and its role in the internet of things. MCC workshop on Mobile cloud computing.

**[IMAGE] Prompt :**
```
Academic three-layer architecture diagram. Top: large cloud symbol labeled "Cloud Layer (100-200ms)". Middle: multiple fog nodes (small clouds) labeled "Fog Layer (5-50ms)". Bottom: IoT devices and vehicles labeled "Edge Layer (<5ms)". Bidirectional arrows between layers. Latency gradient color (red to green). IEEE/ACM publication style, vector graphics quality.
```

---

# SLIDE 5 : RÉSEAUX VÉHICULAIRES (VANET)

## Définition et Caractéristiques

Un **VANET** (Vehicular Ad-hoc Network) est un sous-ensemble des MANETs (Mobile Ad-hoc Networks) caractérisé par :

**Topologie hautement dynamique :** Les liens entre véhicules changent en quelques secondes (durée de contact : 3-30s à 50 km/h).

**Mouvement prévisible :** Contrairement aux MANETs classiques, les véhicules suivent des routes définies, permettant la prédiction de trajectoire.

**Ressources énergétiques non contraintes :** La batterie 12V du véhicule élimine les problèmes d'économie d'énergie des réseaux de capteurs.

**Densité variable :** De 10 véhicules/km² (rural) à 1000 véhicules/km² (centre-ville).

## Standards de Communication

| Standard | Organisme | Fréquence | Débit | Portée |
|----------|-----------|-----------|-------|--------|
| IEEE 802.11p | IEEE | 5.9 GHz | 6-27 Mbps | 300-1000m |
| IEEE 1609 (DSRC) | IEEE/SAE | 5.9 GHz | 6-27 Mbps | 300-1000m |
| ETSI ITS-G5 | ETSI | 5.9 GHz | 6-27 Mbps | 300-1000m |
| 3GPP C-V2X | 3GPP | LTE/5G | Up to 1 Gbps | 500m+ |

**[IMAGE] Prompt :**
```
Top-down aerial view of highway interchange showing VANET topology. Multiple vehicle icons connected by dashed lines representing wireless links. Different colors for different communication types. Network topology overlay. Technical diagram style suitable for IEEE Transactions publication.
```

---

# SLIDE 6 : TYPES DE COMMUNICATION V2X

## Taxonomie V2X (Vehicle-to-Everything)

**V2V (Vehicle-to-Vehicle) :**
- Communication directe entre véhicules via 802.11p
- Latence : 1-10 ms (1 saut)
- Applications : freinage coopératif, platooning, évitement de collision
- Portée : 100-300 m (communication fiable)

**V2I (Vehicle-to-Infrastructure) :**
- Communication véhicule-RSU
- Latence : 10-50 ms
- Applications : gestion feux intelligents, collecte données trafic
- Portée : 300-1000 m selon équipement RSU

**V2N (Vehicle-to-Network) :**
- Communication via infrastructure cellulaire vers Cloud
- Latence : 50-200 ms
- Applications : navigation, streaming, mises à jour OTA
- Portée : illimitée (couverture cellulaire)

**V2P (Vehicle-to-Pedestrian) :**
- Communication véhicule-smartphone piéton
- Latence : 1-10 ms (critique)
- Applications : alerte collision piéton, zones scolaires
- Portée : 50 m

## Tableau Comparatif

| Type | Latence | Portée | Criticité | Technologie |
|------|---------|--------|-----------|-------------|
| V2V | 1-10 ms | 100-300 m | Très haute | 802.11p, C-V2X PC5 |
| V2I | 10-50 ms | 300-1000 m | Haute | 802.11p, C-V2X PC5 |
| V2N | 50-200 ms | Illimitée | Moyenne | LTE, 5G |
| V2P | 1-10 ms | 50 m | Très haute | 802.11p, C-V2X |

**[IMAGE] Prompt :**
```
V2X communication diagram showing all four types. Road scene with two vehicles (V2V arrow between them), RSU tower (V2I arrow to vehicle), cloud (V2N arrow from RSU), pedestrian with smartphone (V2P arrow to vehicle). Each arrow color-coded with latency annotation. Clean technical illustration, IEEE paper quality.
```

---

# SLIDE 7 : ARCHITECTURE 3-TIERS FOG VÉHICULAIRE

## Modèle Hiérarchique

**Couche Cloud (Tier 3) :**
- Localisation : Datacenter distant (>100 km)
- Ressources : MIPS ≈ 10⁶, RAM > 100 GB
- Latence : 100-200 ms
- Fonctions : ML training, analytics globales, stockage historique

**Couche Fog/RSU (Tier 2) :**
- Localisation : Intersections (0-1 km)
- Ressources : MIPS ≈ 10³, RAM 4-16 GB
- Latence : 10-50 ms
- Fonctions : agrégation, cache, contrôle trafic local

**Couche Edge/Véhicule (Tier 1) :**
- Localisation : Embarqué
- Ressources : MIPS ≈ 10², RAM 2-16 GB
- Latence : <5 ms
- Fonctions : traitement capteurs, décisions urgentes

## Distribution du Traitement

| Couche | % Données | Type de traitement |
|--------|-----------|-------------------|
| Edge | 70% | Temps réel critique |
| Fog | 25% | Coordination zonale |
| Cloud | 5% | Analyse globale |

**[IMAGE] Prompt :**
```
Three-tier hierarchical architecture diagram. Top rectangle: "CLOUD LAYER" with server icons, specs "MIPS: 10^6, RAM: 100GB+, Latency: 100-200ms". Middle rectangle: "FOG LAYER (RSU)" with 4 RSU boxes, specs "MIPS: 10^3, RAM: 4-16GB, Latency: 10-50ms". Bottom rectangle: "EDGE LAYER" with vehicle icons, specs "MIPS: 10^2, RAM: 2-16GB, Latency: <5ms". Bidirectional arrows. Academic publication style.
```

---

# SLIDE 8 : CONFIGURATION COUCHE CLOUD

## Paramètres Techniques (iFogSim)

```java
FogDevice cloud = createFogDevice("cloud", 
    44800,   // MIPS
    40000,   // RAM (MB)
    100,     // Uplink BW (Mbps)
    10000    // Downlink BW (Mbps)
);
```

## Fonctions Cloud

1. **Entraînement ML distribué** : Modèles de prédiction trafic (LSTM, Transformer)
2. **Stockage historique** : Conformité RGPD, analyse post-incident
3. **Optimisation globale** : Routage ville entière, load balancing RSU
4. **Déploiement OTA** : Mises à jour firmware, patches sécurité

---

# SLIDE 9 : CONFIGURATION COUCHE FOG (RSU)

## Spécifications IEEE 802.11p

| Paramètre | Valeur |
|-----------|--------|
| Fréquence | 5.850-5.925 GHz |
| Largeur canal | 10 MHz |
| Modulation | OFDM (BPSK à 64-QAM) |
| Débit | 6-27 Mbps |
| Portée | 300-1000 m |
| Délai accès | <50 μs |

## Configuration Simulation

```java
FogDevice rsu = createFogDevice("RSU_J1",
    2800,    // MIPS
    4000,    // RAM (MB)
    10000,   // Uplink BW
    10000    // Downlink BW
);
```

**Positions RSU :** J1(200,200), J2(400,200), J3(200,400), J4(400,400)

**Capacité :** 30 véhicules/RSU (limite CSMA/CA)

**[IMAGE] Prompt :**
```
Technical RSU diagram. Pole-mounted unit with antenna array showing 300m radius coverage circle. Specifications panel: frequency, bandwidth, range. Intersection background. Engineering blueprint style.
```

---

# SLIDE 10 : COUCHE EDGE - TYPES VÉHICULES

## Classification des Véhicules

| Type | Vitesse | MIPS | RAM | Fog-capable |
|------|---------|------|-----|-------------|
| car | 50 km/h | 500 | 2 GB | Conditionnel |
| fog_capable | 50 km/h | 1000 | 8 GB | Oui |
| bus | 40 km/h | 1500 | 16 GB | Oui |
| truck | 35 km/h | 800 | 4 GB | Conditionnel |

## Critère Fog Node

```python
is_fog_node = (
    type == "fog_capable" or
    type == "bus" or
    speed < 8.33  # 30 km/h
)
```

**Justification vitesse :** À v < 30 km/h, le véhicule reste ~36s dans zone RSU (300m), assurant stabilité connexion.

---

# SLIDE 11 : ALGORITHMES DE COOPÉRATION

## Sélection Partenaire de Calcul

**Score de sélection :**
$$score(v) = \alpha \cdot \frac{1}{charge_v} + \beta \cdot \frac{1}{dist_v} + \gamma \cdot stabilité_v$$

Avec : α=0.4, β=0.3, γ=0.3

## Mécanismes

1. **Task Partitioning** : Division DAG en sous-tâches parallélisables
2. **Load Balancing** : Répartition dynamique selon charge CPU
3. **Proximity Clustering** : Formation clusters k-means spatiotemporels
4. **Cooperative Caching** : LRU distribué avec invalidation

---

# SLIDE 12 : MODÈLE D'OFFLOADING

## Décision d'Offloading

$$T_{total} = T_{local} \quad vs \quad T_{upload} + T_{exec}^{remote} + T_{download}$$

**Composantes :**
$$T_{upload} = \frac{D_{in}}{BW_{up}}$$
$$T_{exec} = \frac{Instructions}{MIPS_{target}}$$
$$T_{download} = \frac{D_{out}}{BW_{down}}$$

**Critère de décision :**
$$destination = \arg\min_{d \in \{local, fog, cloud\}} (T_d + \alpha L_d + \beta E_d)$$

---

# SLIDE 13 : MODÈLE DE LATENCE DYNAMIQUE

## Formules

$$L_{edge} = 5.2 + congestion \times 3 \text{ ms}$$
$$L_{fog} = 22.4 + congestion \times 10 \text{ ms}$$
$$L_{cloud} = 125.3 + congestion \times 25 \text{ ms}$$

## Calcul Congestion

$$congestion = \min\left(\frac{N_{véhicules}}{30}, 1.0\right)$$

| Niveau | Base (ms) | Impact congestion | Raison |
|--------|-----------|-------------------|--------|
| Edge | 5.2 | ×3 | Contention CPU |
| Fog | 22.4 | ×10 | Collisions CSMA/CA |
| Cloud | 125.3 | ×25 | Saturation backhaul |

---

# SLIDE 14 : GESTION DE LA MOBILITÉ

## Défis

- **Handover fréquent** : Changement RSU toutes les 30-60s
- **Continuité de service** : Migration tâches en cours
- **Prédiction** : Anticipation trajectoire

## Affectation RSU

```python
def find_nearest_rsu(x, y):
    for rsu_id, (rx, ry) in RSU_POSITIONS.items():
        if sqrt((x-rx)**2 + (y-ry)**2) < RSU_RANGE:
            return rsu_id
    return None
```

## Trigger Handover

$$handover = RSSI_{current} < RSSI_{threshold} + hystérésis$$

Avec : threshold = -85 dBm, hystérésis = 3 dB

---

# SLIDE 15 : SÉCURITÉ VANET

## Menaces

| Attaque | Description | Impact |
|---------|-------------|--------|
| Sybil | Fausses identités multiples | Manipulation consensus |
| MITM | Interception messages | Vol données |
| DoS | Saturation canal | Indisponibilité |
| Replay | Réenvoi anciens messages | Confusion |
| False Info | Faux messages sécurité | Accidents |

## Contre-mesures (IEEE 1609.2)

- **PKI/Certificats** : ECDSA P-256
- **Pseudonymes rotatifs** : Changement toutes les 5 min
- **Timestamp/Nonce** : Fraîcheur messages
- **Vérification plausibilité** : Cohérence physique

---

# SLIDE 16 : OUTILS DE SIMULATION

## Justification des Choix

| Outil | Alternatives | Raison du choix |
|-------|--------------|-----------------|
| SUMO | NS-3, VISSIM | Microsimulation trafic, open-source, TraCI |
| Python | Java, C++ | TraCI bindings, Flask, développement rapide |
| iFogSim | EdgeCloudSim, YAFS | Modèle 3-tiers, basé CloudSim validé |

## Architecture Logicielle

```
SUMO-GUI ←—TraCI—→ server.py ←—Socket—→ iFogSim
                      ↓
                  WebSocket
                      ↓
                  Dashboard
```

**Ports :** SUMO:8813, Flask:5000, iFogSim:5555

---

# SLIDE 17 : CONFIGURATION SUMO

## Fichiers

```xml
<configuration>
    <input>
        <net-file value="network.net.xml"/>
        <route-files value="routes.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="900"/>
        <step-length value="1"/>
    </time>
</configuration>
```

## Phases de Trafic

| Phase | Temps (s) | Véhicules | Description |
|-------|-----------|-----------|-------------|
| Normal | 0-300 | ~50 | Trafic fluide |
| Congestion | 300-600 | ~150 | Saturation |
| Récupération | 600-900 | ~80 | Décongestion |

---

# SLIDE 18 : RÉSULTATS COMPARATIFS

## Cloud-Only vs Fog-Assisted

| Métrique | Cloud-Only | Fog-Assisted | Amélioration |
|----------|------------|--------------|--------------|
| Latence moyenne | 125 ms | 16-20 ms | **-85%** |
| BP Cloud | 100% | 5% | **-95%** |
| Scalabilité | Limitée | Élevée | ++ |
| Tolérance pannes | Faible | Élevée | ++ |

## Latence Moyenne Pondérée

$$L_{avg} = \frac{L_{edge} \times 70 + L_{fog} \times 25 + L_{cloud} \times 5}{100}$$

**[IMAGE] Prompt :**
```
Bar chart comparing Cloud-Only vs Fog-Assisted metrics. Bars for latency (red vs green), bandwidth (gray vs light gray). Percentage improvements annotated. Clean academic chart style, publication quality.
```

---

# SLIDE 19 : AVANTAGES DU FOG VÉHICULAIRE

**Performance :**
- Latence < 20 ms (compatible sécurité)
- Traitement temps réel
- Réduction congestion backbone

**Résilience :**
- Pas de SPOF (Single Point of Failure)
- Fonctionnement mode dégradé
- Distribution géographique

**Économie :**
- Réduction 90% coûts Cloud
- Utilisation ressources existantes

---

# SLIDE 20 : LIMITES ET DÉFIS

**Techniques :**
- Ressources véhiculaires limitées
- Instabilité due à mobilité
- Hétérogénéité équipements

**Organisationnels :**
- Coût déploiement RSU
- Standardisation en cours (DSRC vs C-V2X)
- Modèle économique incertain

---

# SLIDE 21 : PERSPECTIVES 5G/6G

## Évolution Technologique

| Paramètre | DSRC | 5G C-V2X | 6G |
|-----------|------|----------|-----|
| Latence | 20-50 ms | 1-10 ms | <1 ms |
| Débit | 27 Mbps | 1 Gbps | 1 Tbps |
| Portée | 300 m | 500 m | 1 km |
| Capacité | 30 véh | 100 véh | 1000 véh |

---

# SLIDE 22 : CONCLUSION

1. Le **Fog Computing** répond aux exigences de latence véhiculaire (<20 ms)
2. L'architecture **3-tiers** optimise distribution du traitement
3. Notre simulation **SUMO + iFogSim** valide le concept
4. **Réduction 85%** latence vs Cloud-only

**Message clé :** Le Fog Computing Véhiculaire est un complément essentiel au Cloud pour les applications temps réel critiques.

---

# SLIDE 23 : RÉFÉRENCES

1. Bonomi, F. et al. (2012). "Fog Computing and Its Role in the Internet of Things." MCC Workshop.
2. Hou, X. et al. (2016). "Vehicular Fog Computing: A Viewpoint of Vehicles as the Infrastructures." IEEE VTC.
3. Gupta, H. et al. (2017). "iFogSim: A toolkit for modeling and simulation of resource management." Softw Pract Exper.
4. IEEE 802.11p-2010. "Wireless Access in Vehicular Environments."
5. 3GPP Release 16. "C-V2X Technology Overview."

---

# SLIDE 24 : MERCI

**Merci pour votre attention**

**Questions ?**
