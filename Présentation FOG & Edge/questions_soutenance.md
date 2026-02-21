# ❓ Questions & Réponses — Préparation Soutenance

---

## 🔷 PARTIE 1 : Questions Théoriques (Fog & Edge Computing)

---

### Q1 : Quelle est la différence entre le Fog Computing et l'Edge Computing ?
> **Réponse** : L'Edge Computing traite les données directement sur l'appareil terminal (le véhicule dans notre cas), avec des ressources très limitées. Le Fog Computing est une couche intermédiaire entre l'Edge et le Cloud : il utilise des nœuds intermédiaires (RSU, véhicules fog-capable) pour traiter les données plus près de la source, mais avec plus de puissance que l'Edge. Dans notre architecture, l'Edge c'est le véhicule lui-même (500 MIPS), le Fog c'est le RSU (5000 MIPS) et les véhicules fog-capable (1500 MIPS), et le Cloud c'est le serveur distant (20000 MIPS).

---

### Q2 : Pourquoi ne pas tout traiter localement sur le véhicule (Edge) ?
> **Réponse** : Les véhicules ont des ressources de calcul limitées (500 MIPS). Certaines tâches sont trop lourdes pour être traitées localement, notamment quand la charge CPU dépasse 50-60%. De plus, certaines décisions comme le contrôle des feux ou le reroutage nécessitent une vue globale du trafic qu'un seul véhicule ne possède pas. Le Fog permet de mutualiser les ressources : un véhicule fog-capable peut aider ses voisins en traitant leurs tâches.

---

### Q3 : Qu'est-ce qu'un VANET et pourquoi est-ce différent d'un réseau classique ?
> **Réponse** : Un VANET (Vehicular Ad-hoc Network) est un réseau formé dynamiquement par des véhicules communicants. Il diffère d'un réseau classique par : (1) la mobilité très élevée (50-150 km/h) qui rend la topologie instable, (2) les connexions éphémères — un véhicule peut quitter la portée en quelques secondes, (3) les exigences temps réel strictes — l'évitement de collision demande moins de 10 ms, et (4) la densité variable — beaucoup de nœuds en ville, très peu en zone rurale.

---

### Q4 : Qu'est-ce que le task offloading et pourquoi est-ce important ?
> **Réponse** : Le task offloading consiste à décharger une tâche de calcul d'un appareil à ressources limitées vers un autre plus puissant. Dans notre contexte, un véhicule peut envoyer une tâche trop lourde vers un RSU, un véhicule fog voisin, ou le Cloud. C'est important car cela permet de respecter les contraintes de latence : une tâche qui prendrait 100 ms en local peut être exécutée en 7 ms sur un RSU. Mais le choix de la destination est crucial — envoyer au Cloud prend 250 ms à cause du RTT réseau.

---

### Q5 : Expliquez l'algorithme SCOOT. Pourquoi l'avez-vous choisi ?
> **Réponse** : SCOOT (Split Cycle Offset Optimization Technique) est un algorithme de contrôle adaptatif des feux de circulation développé à l'origine par le TRL britannique. Il optimise 3 paramètres : le **split** (répartition du temps vert entre directions), le **cycle** (durée totale d'un cycle de feux), et l'**offset** (synchronisation entre intersections adjacentes). Nous l'avons choisi car : (1) il est adaptatif — il réagit en temps réel aux files d'attente, (2) il est bien documenté dans la littérature, et (3) il se prête bien au Fog Computing car il nécessite des données locales (files d'attente par intersection).

---

### Q6 : Quelle est la différence entre V2V, V2I et V2N ?
> **Réponse** : 
> - **V2V** (Vehicle-to-Vehicle) : communication directe entre véhicules, portée ~100m, latence 5-20 ms. Utilisé pour le fog computing coopératif.
> - **V2I** (Vehicle-to-Infrastructure) : communication entre véhicule et RSU (infrastructure routière), portée ~300m, latence 7-15 ms. Utilisé pour le traitement RSU et SCOOT.
> - **V2N** (Vehicle-to-Network) : communication via réseau cellulaire vers le Cloud, latence ~250 ms. Utilisé comme dernier recours quand les options locales sont saturées.

---

### Q7 : Pourquoi 250 ms pour le Cloud ? C'est réaliste ?
> **Réponse** : Oui, c'est réaliste et même optimiste. Les 250 ms incluent : le temps de transmission montante (~50 ms), le RTT réseau vers un data center distant (~100-150 ms), le temps de traitement, et le temps de transmission descendante. En réalité, avec la congestion réseau et les pics de charge, ça peut dépasser 300-500 ms. Des études comme celles de Bonomi (2012) et Hou (2016) confirment que le RTT Cloud typique pour les applications véhiculaires est de 100-300 ms, ce qui est inacceptable pour le temps réel.

---

### Q8 : Qu'est-ce que la densité fog (ρ_fog) et pourquoi est-elle importante ?
> **Réponse** : La densité fog est le ratio entre le nombre de véhicules fog-capable et le nombre total de véhicules : ρ_fog = fog_nodes / total_vehicles. Elle est cruciale car elle détermine directement les latences V2V et RSU dans notre modèle. Plus ρ_fog est élevé, plus il y a de relais disponibles, donc plus la latence V2V diminue (de 20 ms à 5 ms). C'est un paramètre multiplicateur : à 10% on réduit déjà la latence de 61%, et à 50% on atteint 80%.

---

### Q9 : Qu'est-ce qu'iFogSim ? Pourquoi l'avoir choisi ?
> **Réponse** : iFogSim est un simulateur open-source développé par l'Université de Melbourne, spécifiquement conçu pour modéliser le Fog Computing. Il étend CloudSim pour gérer les nœuds fog, les politiques de placement des modules, et les topologies Edge-Fog-Cloud. Nous l'avons choisi car : (1) il est la référence dans la littérature Fog Computing, (2) il permet de modéliser les latences réseau et les capacités de calcul (MIPS), et (3) il est en Java, ce qui facilite l'intégration avec notre orchestrateur via socket TCP.

---

### Q10 : Qu'est-ce que SUMO et TraCI ?
> **Réponse** : SUMO (Simulation of Urban MObility) est un simulateur microscopique de trafic routier open-source développé par le DLR allemand. Il simule chaque véhicule individuellement avec sa position, vitesse et trajectoire. TraCI (Traffic Control Interface) est l'API Python qui permet de contrôler SUMO en temps réel : récupérer les positions des véhicules, changer les feux, ajouter ou rerouter des véhicules. C'est le pont entre notre simulation de trafic et notre logique Fog Computing.

---

## 🔶 PARTIE 2 : Questions sur l'Implémentation / Démonstration

---

### Q11 : Comment fonctionne la communication entre SUMO, Python et iFogSim ?
> **Réponse** : Le flux est le suivant :
> 1. **SUMO ↔ Python (TraCI)** : À chaque pas de simulation (1 seconde), Python récupère via TraCI les positions, vitesses et types de tous les véhicules.
> 2. **Python → iFogSim (Socket TCP 5555)** : Python envoie ces données à iFogSim qui calcule les décisions d'offloading.
> 3. **iFogSim → Python** : iFogSim renvoie les décisions (destination + latence) et les métriques.
> 4. **Python → SUMO** : Python applique les décisions SCOOT (changement de feux, reroutages) via TraCI.
> 5. **Python → Dashboard** : Les métriques sont envoyées en temps réel au dashboard via Socket.IO.

---

### Q12 : Comment l'algorithme d'offloading choisit-il la destination ?
> **Réponse** : C'est un arbre de décision en cascade basé sur la capacité RSU :
> 1. Si la tâche est petite (CPU < seuil bas ET taille < 0.3) → **LOCAL** (3 ms)
> 2. Si le véhicule est dans une zone RSU ET le RSU n'est pas surchargé (< 8 véhicules) → **RSU** (7-15 ms)
> 3. Si le RSU est surchargé MAIS un véhicule fog est à proximité → **FOG_VEHICLE** (5-20 ms)
> 4. Sinon → **CLOUD** (250 ms)
>
> C'est le mécanisme d'overflow qui crée la différence : en Edge+Cloud, sans fog nodes, le cas 3 n'existe pas et les tâches vont directement au Cloud.

---

### Q13 : Pourquoi la latence diminue quand la densité fog augmente ?
> **Réponse** : Deux raisons. Premièrement, avec plus de fog nodes, il y a plus de véhicules qui peuvent traiter les tâches localement via V2V (5-20 ms) au lieu de les envoyer au Cloud (250 ms). Deuxièmement, notre modèle de latence dynamique fait que la latence V2V elle-même diminue avec la densité fog : L_V2V = max(5, 20 - ρ_fog × 30). À 50% de fog, L_V2V ≈ 5 ms. C'est logique physiquement : plus il y a de relais, plus le relai le plus proche est proche.

---

### Q14 : Comment fonctionne le mécanisme d'overflow RSU ?
> **Réponse** : Chaque RSU a une capacité maximale d'environ 8 véhicules simultanés. Au-delà, nous considérons le RSU comme surchargé (congestion normalisée > 0.32). Quand un RSU est surchargé :
> - La latence RSU augmente proportionnellement à la congestion
> - Les nouvelles tâches sont redirigées vers un véhicule fog voisin (si disponible)
> - Si aucun fog n'est disponible, la tâche va au Cloud (250 ms)
>
> Ce mécanisme est la clé de la différenciation entre les scénarios : en Edge+Cloud, pas de fog = overflow direct vers le Cloud.

---

### Q15 : Le SCOOT est désactivé en Edge+Cloud. Pourquoi ?
> **Réponse** : C'est un choix de design pour montrer l'impact du Fog. Dans le scénario Edge+Cloud, sans fog nodes, les décisions SCOOT ne pourraient pas être exécutées en temps réel car la latence Cloud (250 ms) est trop élevée pour ajuster les feux de manière réactive. Avec le fog, les décisions SCOOT sont traitées en moins de 50 ms, ce qui permet des ajustements quasi instantanés. Cela dit, on pourrait activer SCOOT en Edge+Cloud mais ses décisions seraient retardées et moins efficaces.

---

### Q16 : Comment interprétez-vous le fait que le High Fog a MOINS de congestion (63%) que Edge+Cloud (77%) ?
> **Réponse** : C'est un résultat contre-intuitif mais logique. En High Fog, SCOOT est très actif : il effectue 360 ajustements de feux et 2077 reroutages. Il anticipe la congestion avant qu'elle n'atteigne son pic en redistribuant les véhicules sur des routes alternatives. C'est de la gestion proactive vs réactive. En Edge+Cloud, sans SCOOT, les véhicules suivent leurs routes initiales et s'accumulent aux intersections congestionnées sans qu'aucune action corrective ne soit prise.

---

### Q17 : Que signifie le Performance Index (PI) dans SCOOT ?
> **Réponse** : Le PI mesure le niveau de saturation d'une intersection. PI = Q_max / Q_capacity, où Q_max est la file d'attente maximale (entre N-S et E-W) et Q_capacity est la capacité de l'intersection.
> - PI = 0 → intersection fluide, pas d'intervention nécessaire
> - PI = 0.5 → modérément chargé, ajustement du split
> - PI = 1 → saturé, actions urgentes : reroutage + extension de phase
>
> SCOOT intervient quand PI dépasse un seuil, en ajustant la répartition du vert.

---

### Q18 : Pourquoi avez-vous choisi ces valeurs de MIPS spécifiques ?
> **Réponse** : Les valeurs sont basées sur la littérature et des benchmarks réalistes :
> - **500 MIPS** (Edge) : correspond à un processeur embarqué basique (type ARM Cortex-A7)
> - **1500 MIPS** (Fog vehicle) : processeur plus puissant (type ARM Cortex-A53 ou équivalent)
> - **5000 MIPS** (RSU) : serveur embarqué de bord de route (type Intel Atom ou petit Xeon)
> - **20000 MIPS** (Cloud) : serveur cloud classique (type Xeon multi-cœur)
>
> Ces valeurs créent un gradient réaliste qui justifie l'offloading : un véhicule a intérêt à décharger une tâche lourde vers un RSU 10× plus puissant.

---

### Q19 : Les résultats sont-ils reproductibles ?
> **Réponse** : Oui, la simulation est déterministe si on utilise les mêmes fichiers de routes et la même seed aléatoire. Les 3 scénarios utilisent le même réseau (grid_network.net.xml), le même débit (2000 veh/h) et la même durée (300s). Seule la proportion de véhicules fog-capable change. On peut relancer chaque scénario et obtenir des résultats très proches.

---

### Q20 : Quelles sont les limites de votre simulation ?
> **Réponse** : 
> 1. **Réseau simplifié** : Notre grille à 4 intersections est petite par rapport à un réseau urbain réel.
> 2. **Trafic uniforme** : Le débit est constant (2000 veh/h), en réalité le trafic fluctue.
> 3. **Pas de pertes de paquets** : Nous ne simulons pas les pertes de communication V2V/V2I.
> 4. **Fog statique** : La proportion de fog est fixe, en réalité elle varie dynamiquement.
> 5. **Pas de sécurité** : Nous n'implémentons pas l'authentification des nœuds fog (risque de nœuds malveillants).
> 6. **Pas de mobilité fog** : Un véhicule fog quittant la zone n'est pas modélisé finement.

---

### Q21 : Pourquoi avoir utilisé un socket TCP plutôt qu'une API REST entre Python et iFogSim ?
> **Réponse** : Le socket TCP est plus rapide qu'une API REST car il évite l'overhead HTTP (headers, parsing JSON complet, connexion/déconnexion). Dans notre cas, la communication est très fréquente — à chaque pas de simulation (toutes les secondes) — et les données sont structurées de manière simple. Le socket TCP permet une communication persistante avec une latence minimale, ce qui est essentiel pour ne pas ralentir la simulation.

---

### Q22 : Quelle est la différence entre DSRC et C-V2X ?
> **Réponse** : DSRC (Dedicated Short-Range Communications) est la technologie actuelle basée sur IEEE 802.11p, avec une latence de 20-50 ms, un débit de 27 Mbps et une portée de 300 m. C-V2X (Cellular Vehicle-to-Everything) utilise le réseau cellulaire 5G/6G, avec une latence potentielle de 1-10 ms en 5G et <1 ms en 6G, des débits bien supérieurs (1 Gbps), et une portée de 1-10 km. Notre simulation utilise des paramètres proches du DSRC actuel, mais les perspectives incluent la migration vers C-V2X.

---

### Q23 : Comment votre système gère-t-il un véhicule fog qui quitte la zone ?
> **Réponse** : Dans notre implémentation actuelle, à chaque pas de simulation, Python réévalue la liste des véhicules fog-capable via TraCI. Si un véhicule fog quitte la portée V2V (100 m), il n'est plus considéré comme voisin fog disponible. La prochaine tâche sera alors dirigée vers le RSU ou le Cloud. C'est une limite : en réalité, une tâche en cours de traitement sur un fog qui part pourrait être perdue. La solution serait d'implémenter un mécanisme de migration de tâches.

---

### Q24 : Pourquoi avoir choisi 10% et 50% pour les scénarios fog ?
> **Réponse** : Ces deux valeurs représentent des cas réalistes à court et long terme :
> - **10%** : correspond à un déploiement initial où seuls les véhicules récents (haut de gamme) sont fog-capable. C'est réaliste à 3-5 ans.
> - **50%** : correspond à un déploiement mature où la moitié du parc automobile est fog-capable. C'est réaliste à 10-15 ans avec la démocratisation des processeurs embarqués.
>
> L'écart montre que même 10% suffit pour un gain significatif (-61%), ce qui encourage le déploiement progressif.

---

### Q25 : Pourrait-on appliquer cette approche à d'autres domaines que le trafic routier ?
> **Réponse** : Absolument. L'architecture Edge-Fog-Cloud avec offloading multi-critères est applicable à :
> - **Drones** : Fog Computing entre drones pour la surveillance ou la livraison
> - **IoT industriel** : Usines avec des capteurs qui déchargent vers des gateways fog
> - **Smart City** : Gestion de l'éclairage, des déchets, de l'énergie
> - **Santé** : Monitoring de patients avec traitement local urgent et analyse cloud différée
>
> Le principe est le même : rapprocher le calcul de la source de données pour réduire la latence.

---

## 🔴 PARTIE 3 : Questions Pièges / Difficiles

---

### Q26 : Votre simulation prouve-t-elle que le Fog Computing est toujours meilleur que le Cloud ?
> **Réponse** : Non, et ce n'est pas notre thèse. Le Fog est un **complément** au Cloud, pas un remplacement. Le Cloud reste nécessaire pour : (1) les tâches lourdes nécessitant 20000+ MIPS, (2) le stockage massif de données, (3) l'analyse batch non temps réel. Notre simulation montre que pour les **applications temps réel** avec des contraintes de latence strictes, le Fog est supérieur. Mais même en High Fog, 8% des tâches vont encore au Cloud.

---

### Q27 : Vos résultats sont-ils biaisés par le fait que SCOOT est désactivé en Edge+Cloud ?
> **Réponse** : C'est une critique légitime. En effet, désactiver SCOOT dans Edge+Cloud pénalise ce scénario. Cependant, le choix est justifié : dans un scénario sans fog, les décisions SCOOT reposeraient sur le Cloud avec 250 ms de latence, ce qui les rendrait trop lentes pour être efficaces. On pourrait faire un scénario Edge+Cloud+SCOOT pour comparaison, mais SCOOT avec 250 ms de latence aurait un impact très limité car les feux auraient déjà changé de phase avant que la décision n'arrive.

---

### Q28 : Pourquoi ne pas avoir utilisé un réseau réel au lieu d'une grille artificielle ?
> **Réponse** : La grille simplifiée permet d'isoler l'effet du Fog Computing. Avec un réseau réel (OpenStreetMap), il y aurait trop de variables confondantes : géométrie des routes, feux de types différents, priorités complexes. Notre grille à 4 intersections est un benchmark contrôlé qui permet une comparaison équitable. Cela dit, pour un travail futur, l'extension à un réseau réel serait une étape importante.

---

### Q29 : Comment garantissez-vous la sécurité des communications V2V ?
> **Réponse** : Honnêtement, notre simulation **ne traite pas** la sécurité. C'est une limite identifiée. Dans un déploiement réel, il faudrait implémenter : (1) des certificats PKI véhiculaires (standard IEEE 1609.2), (2) l'authentification des nœuds fog pour éviter les nœuds malveillants, (3) le chiffrement des données offloadées, et (4) des mécanismes de détection d'intrusion. C'est l'une de nos perspectives futures.

---

### Q30 : Que se passe-t-il si tous les fog nodes sont surchargés ?
> **Réponse** : C'est géré par notre mécanisme d'overflow en cascade. Si les fog nodes sont surchargés, le système tombe sur le cas final : **CLOUD** (250 ms). C'est le comportement de dégradation gracieuse — le système ne plante jamais, il se dégrade vers le Cloud. En pratique, avec 50% de fog nodes, cela arrive très rarement car la capacité agrégée des fog nodes est largement suffisante pour absorber la charge.

---

## 💡 Conseils pour répondre aux questions

1. **Structure** : Commencez toujours par une réponse courte (1 phrase), puis développez.
2. **Honnêteté** : Si vous ne savez pas, dites "C'est une excellente question. Nous n'avons pas exploré cet aspect, mais c'est une perspective intéressante."
3. **Chiffres** : Appuyez vos réponses avec des chiffres de la simulation (90 ms → 18 ms, -80%, etc.)
4. **Limites** : Ne jamais dire que votre travail est parfait. Montrer que vous connaissez les limites est un signe de maturité.
5. **Références** : Citez les auteurs quand possible (Bonomi 2012, Hou 2016) pour montrer votre connaissance de la littérature.
