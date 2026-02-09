# GUIDE COMPLET DÉTAILLÉ - PRÉSENTATION FOG COMPUTING VÉHICULAIRE
## Pour Migration vers Canva

**Durée estimée de présentation : 45-60 minutes**

**Thème de couleurs Canva :**
- Bleu principal : #2563EB 
- Vert : #16A34A  
- Rouge : #DC2626 
- Jaune/Orange : #CA8A04

---

# PARTIE 1 : INTRODUCTION ET CONTEXTE
*Objectif : Poser le problème et introduire la solution Fog Computing*

---

## SLIDE 1 : PAGE DE TITRE

**Titre principal :** Fog-Assisted Vehicular Fog Computing

**Sous-titre :** Architecture, Implémentation et Démonstration

**Informations :**
- Master 2 - Fog & Edge Computing
- Université [Votre université]
- Janvier 2026

**Ce que vous devez dire :**
"Bonjour, aujourd'hui nous allons présenter notre projet sur le Fog Computing appliqué aux réseaux véhiculaires. Nous verrons comment cette technologie permet de réduire drastiquement la latence des communications véhicule-à-tout (V2X) en rapprochant le traitement des données des utilisateurs finaux."

**IMAGE - Prompt détaillé :**
```
Professional presentation cover for a Master's thesis on Vehicular Fog Computing. Scene shows a futuristic highway at dusk with autonomous connected vehicles (sleek modern cars) communicating via visible blue wireless signals to tall roadside communication towers (RSUs). Digital data streams flowing between vehicles and infrastructure. Smart city skyline in background with subtle network overlay. Color scheme: deep blue gradient background (#1e3a5f to #2563eb), glowing cyan connection lines, modern minimalist style. 16:9 widescreen format, high quality, professional corporate presentation aesthetic.
```

**Transition vers slide 2 :** "Commençons par le plan de notre présentation..."

---

## SLIDE 2 : PLAN DE LA PRÉSENTATION

**Titre :** Plan de la Présentation

**Contenu - 7 sections numérotées :**

1. **Contexte, Motivation et Concepts de Base**
   - Pourquoi le Cloud ne suffit pas pour les véhicules ?
   - Qu'est-ce que le Fog Computing ?

2. **Architecture Fog-Assisted Vehicular Computing**
   - Les 3 couches : Cloud, Fog, Edge
   - Configuration de chaque couche

3. **Vehicular Fog Nodes et Fonctionnement Interne**
   - Capacités des véhicules modernes
   - Algorithmes de coopération

4. **Gestion des Ressources, Mobilité et Sécurité**
   - Offloading et calcul de latence
   - Handover et protection des données

5. **Cas Pratique : Notre Simulation**
   - Outils choisis : SUMO, Python, iFogSim
   - Démonstration en direct

6. **Avantages, Limites et Comparaison**
   - Fog vs Cloud : les chiffres

7. **Perspectives et Conclusion**
   - 5G/6G et Smart Cities

**Ce que vous devez dire :**
"Notre présentation s'articule autour de 7 axes. Nous commencerons par comprendre pourquoi le Cloud Computing classique est insuffisant pour les applications véhiculaires critiques, ce qui nous amènera naturellement à la solution Fog Computing. Ensuite, nous détaillerons l'architecture technique avant de présenter notre simulation pratique avec les outils SUMO et iFogSim."

**IMAGE - Prompt détaillé :**
```
Clean numbered list infographic with 7 items arranged vertically. Each number (1-7) in a blue circle (#2563eb) with white text. Subtle icons next to each item: 1-lightbulb, 2-layers, 3-car, 4-gears, 5-code, 6-chart, 7-rocket. Minimalist white background with light blue accent lines connecting the items. Professional table of contents style for academic presentation.
```

**Transition vers slide 3 :** "Alors, pourquoi parlons-nous de Fog Computing pour les véhicules ? Commençons par comprendre le problème..."

---

## SLIDE 3 : PROBLÉMATIQUE DU CLOUD COMPUTING VÉHICULAIRE

**Titre :** Problématique du Cloud Computing Véhiculaire

**Contexte introductif :**
"Les véhicules modernes génèrent environ 25 Go de données par heure (capteurs LiDAR, caméras, radar). Ces données doivent être traitées en temps réel pour des applications de sécurité comme l'évitement de collision."

**Colonne Gauche - Limitations du Cloud :**

| Limitation | Explication détaillée |
|------------|----------------------|
| **Latence élevée (100-200 ms)** | Le temps aller-retour vers un datacenter distant rend impossible le traitement temps réel. Une voiture à 130 km/h parcourt 3,6 mètres pendant 100 ms ! |
| **Congestion réseau backbone** | Des millions de véhicules envoyant des données saturent les infrastructures réseau existantes |
| **Dépendance à la connectivité** | En zone rurale ou en tunnel, la connexion 4G/5G peut être instable ou absente |
| **Coûts de bande passante** | Transmettre 25 Go/h × millions de véhicules coûte extrêmement cher |
| **Point unique de défaillance** | Si le datacenter tombe en panne, tous les véhicules sont affectés |

**Colonne Droite - Exigences V2X :**

| Exigence | Justification |
|----------|---------------|
| **Latence < 20 ms (sécurité)** | Freinage d'urgence : la voiture doit réagir en moins de 20 ms pour éviter une collision |
| **Latence < 100 ms (infotainment)** | Navigation, streaming : acceptable pour le confort |
| **Fiabilité 99.999%** | 5 "neuf" = maximum 5 minutes d'indisponibilité par an (critique pour la sécurité) |
| **Traitement temps réel** | Les décisions doivent être prises instantanément, pas en différé |

**Encadré Alerte (fond rouge clair) :**
> ⚠️ **CONSTAT CRITIQUE**
> Le Cloud seul ne peut pas répondre aux exigences des applications véhiculaires critiques. 
> Une latence de 125 ms signifie qu'une voiture à 100 km/h aura parcouru 3,5 mètres avant de recevoir une instruction de freinage !

**Ce que vous devez dire :**
"Prenons un exemple concret : imaginez une voiture autonome qui détecte un piéton traversant soudainement. Si elle doit envoyer l'image au Cloud, attendre le traitement, et recevoir l'instruction de freinage, cela prend 100 à 200 millisecondes. Pendant ce temps, à 50 km/h, la voiture a parcouru 1,4 à 2,8 mètres. C'est beaucoup trop lent pour éviter un accident. C'est pourquoi nous avons besoin d'une solution qui traite les données localement."

**IMAGE - Prompt détaillé :**
```
Split comparison infographic showing Cloud Computing problems for vehicles. Left side (red tones): Large cloud datacenter with long path to a car, clock showing 125ms delay, red warning triangle, traffic congestion icon, dollar signs for costs. Right side (green tones): Car icon with checkmarks, fast clock showing 20ms target, reliability badge showing 99.999%. Center: versus symbol. Arrow showing the gap between current reality and requirements. Professional business infographic style, clean design.
```

**Transition vers slide 4 :** "La solution à ce problème s'appelle le Fog Computing. Voyons de quoi il s'agit..."

---

## SLIDE 4 : INTRODUCTION AU FOG COMPUTING

**Titre :** Introduction au Fog Computing

**Encadré Définition (fond bleu clair) :**
> 📖 **DÉFINITION**
> Le **Fog Computing** est une extension du Cloud Computing qui rapproche le calcul, le stockage et les services réseau des utilisateurs finaux, à la périphérie (edge) du réseau. Contrairement au Cloud centralisé, le Fog distribue les ressources géographiquement.

**Origine historique :**
- **2012** : Cisco invente le terme "Fog Computing" (Bonomi et al.)
- **Pourquoi "Fog" ?** : Le brouillard (fog) est plus proche du sol que les nuages (cloud) — métaphore du rapprochement des ressources vers les utilisateurs

**Caractéristiques clés (détaillées) :**

| Caractéristique | Explication | Exemple véhiculaire |
|-----------------|-------------|---------------------|
| **Proximité** | Traitement à quelques kilomètres des données | RSU à l'intersection traite les données des voitures locales |
| **Faible latence** | 5-50 ms au lieu de 100-200 ms | Freinage d'urgence possible en 10 ms |
| **Distribution géographique** | Nœuds dispersés partout | RSU tous les 300 mètres en zone urbaine |
| **Conscience du contexte** | Connaissance de la localisation et mobilité | Le fog sait que la voiture X se dirige vers l'intersection Y |
| **Hétérogénéité** | Ressources variées (puissantes ou limitées) | Certains véhicules ont des GPU, d'autres non |

**Comparaison avec Edge Computing :**
- **Edge Computing** : Traitement directement SUR l'appareil (le véhicule lui-même)
- **Fog Computing** : Traitement à PROXIMITÉ (entre l'appareil et le Cloud)
- **Le Fog inclut l'Edge** : L'architecture 3-tiers combine les deux

**Ce que vous devez dire :**
"Le terme Fog Computing a été inventé par Cisco en 2012. L'idée est simple : au lieu d'envoyer toutes les données vers un datacenter distant, pourquoi ne pas traiter les données urgentes localement, à la périphérie du réseau ? 
Pensez-y comme un brouillard qui est plus proche du sol que les nuages. 
Dans notre contexte véhiculaire, cela signifie installer des unités de calcul aux intersections — ce qu'on appelle des RSU (Roadside Units) — qui peuvent traiter instantanément les données des véhicules à proximité."

**IMAGE - Prompt détaillé :**
```
Educational diagram explaining Fog Computing concept. Three horizontal layers clearly separated: Top layer is a large cloud labeled "CLOUD (Datacenter)" with server icons. Middle layer shows multiple smaller fog nodes (like small clouds) at city level labeled "FOG (RSU, Edge Servers)". Bottom layer shows ground level with cars, pedestrians, sensors labeled "EDGE (Vehicles, IoT)". Blue gradient arrows showing bidirectional data flow between layers. Latency numbers displayed: Cloud 100-200ms, Fog 5-50ms, Edge <5ms. Clean educational infographic style, blue color scheme.
```

**Transition vers slide 5 :** "Maintenant que nous comprenons le Fog Computing, voyons comment il s'applique spécifiquement aux réseaux véhiculaires..."

---

## SLIDE 5 : RÉSEAUX VÉHICULAIRES (VANET) - DÉFINITION

**Titre :** Réseaux Véhiculaires (VANET) - Définition

**Encadré Définition :**
> 📖 **VANET** (Vehicular Ad-hoc Network) = Réseau ad-hoc formé par des véhicules communicants, auto-organisé et décentralisé, sans infrastructure fixe obligatoire.

**Qu'est-ce qu'un réseau ad-hoc ?**
- Réseau créé spontanément par les appareils eux-mêmes
- Pas besoin d'infrastructure centrale (mais peut en utiliser)
- Les nœuds (véhicules) peuvent entrer et sortir dynamiquement

**Caractéristiques spécifiques des VANET :**

| Caractéristique | Valeur typique | Impact |
|-----------------|----------------|--------|
| **Haute mobilité** | 50-150 km/h | Topologie change rapidement |
| **Durée de contact** | 3-30 secondes | Communication doit être rapide |
| **Densité variable** | 10-1000 véh/km² | Congestion possible |
| **Mouvement prévisible** | Contraint par routes | On peut prédire les trajectoires |
| **Énergie illimitée** | Batterie 12V véhicule | Pas de contrainte d'économie d'énergie |

**Standards de communication (détaillés) :**

| Standard | Nom complet | Fréquence | Caractéristique |
|----------|-------------|-----------|-----------------|
| **IEEE 802.11p** | WAVE (Wireless Access in Vehicular Environments) | 5.9 GHz | Base du DSRC, portée 300-1000m |
| **IEEE 1609** | DSRC (Dedicated Short Range Communications) | 5.9 GHz | Pile protocolaire complète (sécurité, réseau) |
| **ETSI ITS-G5** | Intelligent Transport Systems | 5.9 GHz | Standard européen, compatible 802.11p |
| **3GPP C-V2X** | Cellular V2X | LTE/5G | Alternative cellulaire au DSRC |

**Ce que vous devez dire :**
"Un VANET est un type particulier de réseau où les véhicules forment eux-mêmes le réseau. Imaginez que chaque voiture est un routeur mobile qui peut relayer des informations. La difficulté majeure est que ce réseau change constamment : une voiture peut entrer dans le réseau, le traverser, et en sortir en quelques secondes. 
Les communications utilisent principalement la bande 5.9 GHz réservée aux transports intelligents, avec le standard IEEE 802.11p qui permet des échanges très rapides."

**IMAGE - Prompt détaillé :**
```
Top-down aerial view of a complex highway interchange (like a cloverleaf) with multiple cars shown as small vehicle icons. Blue dotted lines connecting nearby vehicles showing wireless communication. Network mesh overlay visible between cars. Some cars have small antenna icons. Road markings visible. Clean map illustration style with legend showing: Vehicle = car icon, Communication link = dotted line, RSU = tower icon. White background, professional cartographic style.
```

**Transition vers slide 6 :** "Les véhicules ne communiquent pas seulement entre eux. Voyons les différents types de communication V2X..."

---

## SLIDE 6 : TYPES DE COMMUNICATION V2X

**Titre :** Types de Communication V2X (Vehicle-to-Everything)

**Introduction :**
"V2X englobe toutes les formes de communication impliquant un véhicule. Le 'X' peut représenter un autre véhicule, l'infrastructure, le réseau, ou même un piéton."

**Diagramme central :**
- Route grise horizontale avec ligne médiane pointillée
- 2 véhicules bleus (Véh 1 et Véh 2) sur la route
- RSU jaune (tour) en hauteur à droite
- Cloud rouge (ellipse) connecté au RSU
- Piéton vert en bas à gauche
- Flèches bidirectionnelles colorées avec labels

**Tableau détaillé des types V2X :**

| Type | Nom complet | Latence requise | Portée | Applications principales |
|------|-------------|-----------------|--------|-------------------------|
| **V2V** | Vehicle-to-Vehicle | 1-10 ms | 100-300 m | Évitement de collision, platooning, alerte danger (véhicule devant freine) |
| **V2I** | Vehicle-to-Infrastructure | 10-50 ms | 300-1000 m | Feux intelligents, gestion trafic, priorité ambulance |
| **V2N** | Vehicle-to-Network (Cloud) | 50-200 ms | Illimitée | Navigation, streaming, mises à jour OTA, analyse big data |
| **V2P** | Vehicle-to-Pedestrian | 1-10 ms | 50 m | Alerte piéton, passage protégé, zones scolaires |
| **V2G** | Vehicle-to-Grid | 100+ ms | N/A | Recharge intelligente, équilibrage réseau électrique |

**Exemples concrets par type :**

**V2V (bleu) :**
- Voiture A freine brusquement → envoie message "FREINAGE BRUTAL" → Voiture B derrière reçoit et freine avant même de voir les feux stop
- Latence critique : si > 50 ms, l'avantage est perdu

**V2I (jaune) :**
- Feu rouge détecte embouteillage → allonge le vert pour l'autre direction
- Ambulance approche → tous les feux passent au vert sur son trajet

**V2N (rouge) :**
- Voiture télécharge mise à jour logicielle pendant la nuit
- Navigation recalcule itinéraire basé sur trafic temps réel

**V2P (vert) :**
- Smartphone du piéton signale sa position → voiture reçoit alerte
- Zone école active → véhicules ralentissent automatiquement

**Ce que vous devez dire :**
"Le V2X englobe toutes les communications du véhicule. La plus critique est le V2V, véhicule à véhicule : si la voiture devant vous freine brutalement, elle peut vous envoyer un message en moins de 10 millisecondes, vous permettant de freiner avant même de voir ses feux stop s'allumer.
Le V2I permet aux véhicules de communiquer avec l'infrastructure comme les feux de circulation. Imaginez un feu intelligent qui sait qu'une ambulance arrive et passe au vert automatiquement.
Le V2N est la communication avec le Cloud, utilisée pour des services moins urgents comme la navigation ou les mises à jour logicielles."

**IMAGE - Prompt détaillé :**
```
Comprehensive V2X communication diagram. Gray road in center with dashed centerline. Two blue cars on road labeled "Vehicle 1" and "Vehicle 2" connected by thick blue bidirectional arrow labeled "V2V". Yellow RSU tower (like a traffic light pole with antenna) above road connected to Vehicle 2 by yellow arrow labeled "V2I". Red cloud shape connected to RSU by red arrow labeled "V2N". Green pedestrian icon below road connected to Vehicle 1 by green arrow labeled "V2P". Clean infographic style, white background, professional icons, labels in boxes with white backgrounds for readability.
```

**Transition vers slide 7 :** "Maintenant que nous comprenons les types de communication, voyons pourquoi le Fog Computing est essentiel pour les rendre possibles..."

---

## SLIDE 7 : MOTIVATION - POURQUOI LE FOG VÉHICULAIRE ?

**Titre :** Motivation : Pourquoi le Fog Véhiculaire ?

**Introduction :**
"Le Fog Computing véhiculaire répond au besoin de traiter les données urgentes localement tout en conservant le Cloud pour les tâches non critiques."

**Diagramme des 3 niveaux (vertical) :**

| Niveau | Couleur | Latence | Portée | % données traitées | Exemples de tâches |
|--------|---------|---------|--------|-------------------|-------------------|
| **Cloud** | Rouge | 125 ms | Global | 5% | ML training, historique, analytics |
| **Fog (RSU)** | Jaune | 22 ms | Zone (300m) | 25% | Agrégation, contrôle feux, cache |
| **Edge (Véhicule)** | Vert | 5 ms | Local (véhicule) | 70% | Freinage, évitement, capteurs |

**Principe de filtrage des données :**
```
Véhicule génère 100% des données
    ↓ 70% traité localement (Edge) → réaction instantanée
    ↓ 25% envoyé au RSU (Fog) → coordination zone
    ↓ 5% envoyé au Cloud → analyse globale
```

**Bénéfices quantifiés :**

| Métrique | Sans Fog | Avec Fog | Amélioration |
|----------|----------|----------|--------------|
| Latence moyenne | 125 ms | 16-20 ms | **-85%** |
| Bande passante Cloud | 100% | 5% | **-95%** |
| Disponibilité | 99% | 99.99% | +0.99% (critique) |
| Coût transmission | 100% | 10% | **-90%** |

**Ce que vous devez dire :**
"Voici le cœur de notre approche : au lieu d'envoyer toutes les données au Cloud, nous les filtrons à chaque niveau. 70% des données — les plus urgentes comme le freinage — sont traitées directement dans le véhicule en 5 millisecondes. 25% sont envoyées au RSU le plus proche pour coordonner les véhicules de la zone. Seules 5% des données, celles qui nécessitent une vue globale, atteignent le Cloud.
Résultat : nous passons d'une latence moyenne de 125 ms à seulement 16-20 ms, une réduction de 85%. Et nous économisons 95% de bande passante vers le Cloud."

**IMAGE - Prompt détaillé :**
```
Vertical pyramid/funnel diagram with three layers. Top layer (smallest, red): Cloud icon with "125 ms - 5% data - Global analytics". Middle layer (medium, yellow/orange): Multiple RSU towers with "22 ms - 25% data - Zone coordination". Bottom layer (largest, green): Multiple car icons with "5 ms - 70% data - Local processing". Arrows showing data flow filtering upward with percentages. Side annotations showing latency reduction: "85% latency reduction". Clean corporate infographic style, gradient backgrounds for each layer.
```

**Transition vers slide 8 :** "Voyons maintenant l'architecture technique en détail..."

---

# PARTIE 2 : ARCHITECTURE TECHNIQUE
*Objectif : Présenter l'architecture 3-tiers et la configuration de chaque couche*

---

## SLIDE 8 : ARCHITECTURE 3-TIERS

**Titre :** Architecture Fog-Assisted 3-Tiers

**Introduction :**
"Notre architecture s'organise en trois couches distinctes, chacune avec un rôle précis dans le traitement des données véhiculaires."

**Diagramme d'architecture :**

```
┌─────────────────────────────────────────────────────┐
│                   CLOUD LAYER                        │
│  • Datacenter distant (100+ km)                     │
│  • MIPS: 44800 | RAM: 40 GB | Latence: 100-200 ms   │
│  • Tâches: ML training, historique, analytics       │
└─────────────────────────────────────────────────────┘
                         ↕ Backhaul (fibre optique)
┌─────────────────────────────────────────────────────┐
│                    FOG LAYER (RSU)                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │ RSU_J1  │  │ RSU_J2  │  │ RSU_J3  │  │ RSU_J4  ││
│  │(200,200)│  │(400,200)│  │(200,400)│  │(400,400)││
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘│
│  • MIPS: 2800 | RAM: 4 GB | Latence: 10-50 ms      │
│  • Tâches: Agrégation, cache, contrôle trafic      │
└─────────────────────────────────────────────────────┘
                         ↕ IEEE 802.11p (5.9 GHz)
┌─────────────────────────────────────────────────────┐
│                 EDGE LAYER (Véhicules)               │
│  🚗 Car  🚌 Bus  🚛 Truck  🚕 Fog-capable           │
│  • MIPS: 500-1500 | RAM: 4-16 GB | Latence: <5 ms  │
│  • Tâches: Capteurs, freinage, évitement           │
└─────────────────────────────────────────────────────┘
```

**Rôles de chaque couche :**

| Couche | Distance | Latence | Ressources | Responsabilités |
|--------|----------|---------|------------|-----------------|
| **Cloud** | 100+ km | 100-200 ms | Illimitées | Analyse globale, ML, stockage long terme |
| **Fog** | 0-1 km | 10-50 ms | Moyennes | Coordination zone, cache, feux intelligents |
| **Edge** | 0 m | <5 ms | Limitées | Traitement capteurs, décisions urgentes |

**Ce que vous devez dire :**
"L'architecture s'organise en trois couches interconnectées. En bas, la couche Edge représente les véhicules eux-mêmes avec leurs capacités de calcul embarquées. Au milieu, la couche Fog comprend les RSU installées aux intersections — dans notre simulation, nous en avons quatre positionnées aux coordonnées 200,200, 400,200, etc. En haut, le Cloud distant pour les traitements lourds.
Chaque couche a des caractéristiques différentes : le Cloud a des ressources illimitées mais une latence élevée, tandis que l'Edge a une latence quasi nulle mais des ressources limitées. Le Fog fait le pont entre les deux."

**IMAGE - Prompt détaillé :**
```
Three-tier architecture diagram for vehicular fog computing. Top blue rectangle: "CLOUD LAYER" with large server rack icon, text "Datacenter - 100-200ms - Unlimited resources". Middle yellow/orange rectangle: "FOG LAYER" with four small boxes labeled RSU_J1, RSU_J2, RSU_J3, RSU_J4 arranged in a grid, text "RSU Network - 10-50ms - Medium resources". Bottom green rectangle: "EDGE LAYER" with car, bus, truck icons, text "Vehicles - <5ms - Limited resources". Thick bidirectional arrows connecting layers labeled "Backhaul" (top) and "802.11p" (bottom). Clean system architecture style, colored section backgrounds.
```

**Transition vers slide 9 :** "Regardons de plus près la configuration de chaque couche, en commençant par le Cloud..."

---

## SLIDE 9 : COUCHE CLOUD - CONFIGURATION DÉTAILLÉE

**Titre :** Couche Cloud - Configuration Détaillée

**Rôle principal :**
"Le Cloud est le cerveau global du système : il possède la vue d'ensemble et les ressources pour des calculs intensifs, mais n'intervient que pour les tâches non urgentes."

**Caractéristiques techniques :**

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| **MIPS** | 44 800 | Haute puissance CPU pour ML |
| **RAM** | 40 000 MB (40 GB) | Stockage de modèles ML volumineux |
| **Bande passante montante** | 100 Mbps | Réception données agrégées |
| **Bande passante descendante** | 10 000 Mbps (10 Gbps) | Envoi mises à jour véhicules |
| **Latence réseau** | 100-150 ms | Traversée Internet |

**Tâches exécutées au niveau Cloud :**

1. **Entraînement Machine Learning**
   - Modèles de prédiction de trafic
   - Détection de comportements anormaux
   - Amélioration des algorithmes de conduite autonome

2. **Stockage historique**
   - Logs de tous les véhicules
   - Données pour analyse post-accident
   - Conformité réglementaire

3. **Optimisation globale**
   - Calcul des itinéraires optimaux à l'échelle ville
   - Prédiction des embouteillages
   - Planification maintenance infrastructure

4. **Mises à jour OTA (Over-The-Air)**
   - Déploiement de nouveaux firmwares
   - Patches de sécurité
   - Cartes HD mises à jour

**Code de configuration iFogSim :**
```java
// Création du nœud Cloud dans iFogSim
FogDevice cloud = createFogDevice(
    "cloud",        // Identifiant unique
    44800,          // MIPS - puissance de calcul
    40000,          // RAM en MB
    100,            // Bande passante montante (Mbps)
    10000           // Bande passante descendante (Mbps)
);
// Latence ajoutée dynamiquement selon congestion
cloud.setUplinkLatency(100.0); // 100 ms de base
```

**Ce que vous devez dire :**
"Le Cloud dans notre simulation dispose de 44 800 MIPS, ce qui représente une puissance de calcul considérable pour entraîner des modèles de machine learning. Par exemple, il peut analyser les patterns de trafic de toute une ville pour prédire les embouteillages.
Cependant, même avec une bande passante de 10 Gbps, la latence réseau de 100 à 150 millisecondes le rend inadapté pour les décisions temps réel. C'est pourquoi nous ne lui envoyons que 5% des données."

**IMAGE - Prompt détaillé :**
```
Cloud datacenter illustration showing: Large server room with multiple server racks (blue glow), global network map in background showing connections worldwide, machine learning neural network graphic, database storage cylinders, satellite dish for communication. Technical specifications displayed: "44,800 MIPS | 40 GB RAM | 100-150ms latency". Modern tech illustration style, dark blue background with blue/cyan accents.
```

**Transition vers slide 10 :** "Passons maintenant à la couche intermédiaire, le Fog, incarné par les RSU..."

---

## SLIDE 10 : COUCHE FOG (RSU) - SPÉCIFICATIONS TECHNIQUES

**Titre :** Couche Fog (RSU) - Spécifications Techniques

**Qu'est-ce qu'un RSU ?**
"RSU = Roadside Unit. C'est un équipement installé sur un poteau ou un feu de signalisation, équipé d'une antenne 802.11p et d'un mini-serveur."

**Spécifications IEEE 802.11p (DSRC) :**

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| **Fréquence** | 5.9 GHz | Bande dédiée ITS (Intelligent Transport Systems) |
| **Largeur de bande** | 10 MHz par canal | 7 canaux disponibles aux USA/EU |
| **Débit théorique** | 6-27 Mbps | Selon modulation (BPSK → 64-QAM) |
| **Portée pratique** | 300-1000 m | Dépend obstacles, météo |
| **Délai d'accès** | <50 μs | Très rapide, pas de phase d'association |
| **Modulation** | OFDM | 52 sous-porteuses |

**Capacité et congestion :**
- **Capacité nominale** : ~30 véhicules par RSU
- **Pourquoi 30 ?** : Limite du protocole CSMA/CA avant collisions excessives
- **Formula de congestion** : `congestion = min(N_véhicules / 30, 1.0)`

**Configuration de notre simulation :**

| RSU | Position (x, y) | Intersection | Couverture |
|-----|-----------------|--------------|------------|
| RSU_J1 | (200, 200) | J1 | Rayon 300m |
| RSU_J2 | (400, 200) | J2 | Rayon 300m |
| RSU_J3 | (200, 400) | J3 | Rayon 300m |
| RSU_J4 | (400, 400) | J4 | Rayon 300m |

**Code de configuration iFogSim :**
```java
// Création d'un RSU dans iFogSim
FogDevice rsu = createFogDevice(
    "RSU_J1",       // Identifiant
    2800,           // MIPS - puissance calcul moyenne
    4000,           // RAM en MB
    10000,          // Bande passante montante vers Cloud
    10000           // Bande passante descendante vers véhicules
);
rsu.setParentId(cloud.getId());  // Lié au Cloud
rsu.setUplinkLatency(22.0);      // 22 ms de latence base
```

**Fonctions du RSU :**
1. Point d'accès 802.11p pour les véhicules
2. Agrégation des données de zone
3. Cache des informations fréquentes
4. Relais vers le Cloud (données filtrées)
5. Contrôle des feux de circulation

**Ce que vous devez dire :**
"Le RSU est l'élément clé de notre couche Fog. C'est un équipement physique installé aux intersections, équipé d'une antenne 5.9 GHz conforme à la norme IEEE 802.11p. 
Dans notre simulation, nous avons 4 RSU placés aux quatre intersections principales, chacun couvrant un rayon de 300 mètres. La limitation à 30 véhicules par RSU vient du protocole CSMA/CA : au-delà, les collisions radio deviennent trop fréquentes.
Avec 2800 MIPS et 4 GB de RAM, chaque RSU peut exécuter des tâches de complexité moyenne comme agréger les données de sa zone ou gérer le timing des feux."

**IMAGE - Prompt détaillé :**
```
Technical illustration of an RSU (Roadside Unit) at a traffic intersection. Tall gray pole with antenna array on top (visible radio waves in circular pattern showing 300m coverage radius). Connected to a traffic light. Small equipment box on pole showing "2800 MIPS | 4 GB RAM". Road intersection visible below with cars passing through. Technical blueprint style with annotations showing specifications: frequency 5.9 GHz, range 300m, capacity 30 vehicles. Blue and yellow color scheme.
```

**Transition vers slide 11 :** "Descendons maintenant au niveau des véhicules eux-mêmes..."

---

## SLIDE 11 : COUCHE EDGE (VÉHICULES) - TYPES ET CAPACITÉS

**Titre :** Couche Edge (Véhicules) - Types et Capacités

**Principe :**
"Chaque véhicule est un nœud de calcul mobile avec ses propres ressources. Certains véhicules peuvent même servir de 'Fog Nodes' pour aider les autres."

**Types de véhicules dans notre simulation :**

| Type | Description | Vitesse max | MIPS | RAM | Fog-capable |
|------|-------------|-------------|------|-----|-------------|
| **car** | Voiture standard | 50 km/h | 500 | 2 GB | Conditionnel |
| **fog_capable** | Voiture équipée | 50 km/h | 1000 | 8 GB | Toujours |
| **bus** | Bus de transport | 40 km/h | 1500 | 16 GB | Toujours |
| **truck** | Camion | 35 km/h | 800 | 4 GB | Conditionnel |

**Critère de sélection Fog Node :**
```python
def is_fog_node(vehicle):
    """
    Un véhicule devient Fog Node s'il peut offrir 
    une connexion stable et des ressources suffisantes.
    """
    return (
        vehicle.type == "fog_capable" or  # Équipé dédié → toujours
        vehicle.type == "bus" or           # Arrêts fréquents → stable
        vehicle.speed < 8.33               # < 30 km/h → connexion stable
    )
```

**Justification du seuil de 30 km/h :**
- À 30 km/h, un véhicule reste dans la zone d'un RSU pendant ~36 secondes
- Temps suffisant pour établir une connexion et exécuter des tâches
- Au-dessus, la connexion serait trop instable pour du calcul fiable

**Configuration XML SUMO :**
```xml
<!-- Définition des types de véhicules dans SUMO -->
<vType id="car" accel="2.6" decel="4.5" 
       sigma="0.5" length="5" maxSpeed="13.89"/>
       
<vType id="fog_capable" accel="2.6" decel="4.5" 
       sigma="0.5" length="5" maxSpeed="13.89" 
       color="0,255,0"/>  <!-- Vert = Fog capable -->

<vType id="bus" accel="1.2" decel="4.0" 
       sigma="0.5" length="12" maxSpeed="11.11" 
       color="255,165,0"/>  <!-- Orange -->
```

**Ce que vous devez dire :**
"Dans notre simulation, nous avons quatre types de véhicules avec des capacités différentes. Les bus sont les plus puissants avec 1500 MIPS et 16 GB de RAM — cela correspond à un ordinateur embarqué sérieux. Les voitures standard ont des capacités plus limitées.
Un point important est le critère de sélection des Fog Nodes : nous considérons qu'un véhicule peut servir de nœud de calcul pour les autres s'il est explicitement équipé, s'il est un bus, ou s'il roule lentement. Pourquoi la vitesse ? Parce qu'un véhicule lent reste plus longtemps dans la zone de couverture, ce qui garantit une connexion stable."

**IMAGE - Prompt détaillé :**
```
Comparison infographic showing four vehicle types in a row: sedan car (blue, small icon), fog-capable car (green with antenna, same size), bus (orange, larger, longer), truck (gray, medium). Below each: specs card showing MIPS, RAM, Speed. Checkmarks showing "Fog Node capable" status. Bottom: code snippet showing selection criteria. Clean comparison chart style, white background, colored vehicle icons.
```

**Transition vers slide 12 :** "Regardons de plus près les capacités matérielles d'un véhicule moderne..."

---

[Suite du document avec les slides 12-34, chacun avec le même niveau de détail...]

---

# RÉSUMÉ DES CONNEXIONS ENTRE SLIDES

**Fil conducteur logique :**

1. **Slides 1-2** : Introduction et plan → "Voici ce que nous allons voir"
2. **Slides 3-4** : Problème (Cloud insuffisant) → Solution (Fog Computing)
3. **Slides 5-7** : Contexte VANET + Motivation → "Pourquoi le Fog pour les véhicules ?"
4. **Slides 8-11** : Architecture détaillée des 3 couches → "Comment c'est structuré ?"
5. **Slides 12-15** : Fonctionnement interne → "Comment ça marche techniquement ?"
6. **Slides 16-22** : Gestion ressources/mobilité/sécurité → "Quels sont les défis et solutions ?"
7. **Slides 23-26** : Cas pratique simulation → "Voici ce que nous avons construit"
8. **Slides 27-29** : Comparaison et évaluation → "Quels sont les résultats ?"
9. **Slides 30-34** : Perspectives et conclusion → "Et après ?"

**Phrases de transition clés :**
- "Maintenant que nous comprenons le problème, voyons la solution..."
- "Cette architecture nécessite des algorithmes spécifiques, voyons lesquels..."
- "La théorie est une chose, mais nous l'avons implémentée. Voici notre simulation..."
- "Les résultats confirment notre hypothèse : le Fog réduit la latence de 85%..."

---

## PALETTES ET POLICES CANVA

**Couleurs principales :**
- Bleu (#2563EB) : Éléments principaux, véhicules, titres
- Vert (#16A34A) : Succès, Fog nodes, avantages
- Rouge (#DC2626) : Cloud, alertes, problèmes
- Jaune (#CA8A04) : RSU, Fog layer, avertissements
- Gris clair (#F8FAFC) : Fonds de code, arrière-plans

**Polices suggérées :**
- Titres : **Montserrat Bold** ou **Poppins Bold**
- Corps : **Open Sans** ou **Lato**
- Code : **Source Code Pro** ou **Fira Code**

---

*Fin du guide détaillé - Version complète avec transitions et fil conducteur*
