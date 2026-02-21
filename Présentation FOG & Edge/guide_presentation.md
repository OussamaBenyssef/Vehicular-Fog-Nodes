# 🎤 Guide de Présentation — Phrases à dire pour chaque slide

---

## Slide 1 : Page de titre
> "Bonjour à tous. Nous allons vous présenter notre projet de Fog-Assisted Vehicular Fog Computing, réalisé dans le cadre du module Fog & Edge Computing. Notre objectif est de montrer comment le Fog Computing peut révolutionner la gestion du trafic routier en temps réel."

---

## Slide 2 : Plan de la Présentation
> "Voici le plan que nous allons suivre. Nous commencerons par la problématique, puis l'objectif, la méthodologie, les paramètres de simulation, les métriques, les résultats, une démonstration en direct, et enfin la discussion et conclusion."

---

## Slide 3 : Contexte — Réseaux Véhiculaires (VANET)
> "Les réseaux véhiculaires, ou VANET, sont des réseaux ad-hoc formés par des véhicules communicants. Ils supportent des communications V2V, V2I et d'autres modes. La particularité de ces réseaux est la mobilité élevée — les véhicules roulent entre 50 et 150 km/h — ce qui rend la topologie très dynamique."
>
> "Les applications critiques comme l'évitement de collision exigent des latences inférieures à 10 ms, et la gestion du trafic nécessite des temps de réponse sous les 100 ms."

---

## Slide 4 : Défis et Limites du Cloud Computing
> "Le problème principal est que le Cloud seul ne peut pas répondre à ces exigences. Avec un RTT d'environ 250 ms, le Cloud est trop lent pour les décisions temps réel. En plus, il crée un point unique de défaillance et consomme beaucoup de bande passante."
>
> "Le constat est clair : il faut rapprocher le calcul des véhicules. C'est là qu'intervient le Fog Computing."

---

## Slide 5 : Objectif du Projet
> "Notre objectif est triple : premièrement, gérer la congestion du trafic en temps réel via le Fog Computing. Deuxièmement, optimiser le task offloading dans un environnement véhiculaire multi-tiers. Et troisièmement, démontrer concrètement l'apport du Fog par rapport au Cloud seul."
>
> "Voici notre architecture 3-tiers : Edge pour le traitement local sur véhicule, Fog pour le traitement coopératif entre véhicules et RSU, et Cloud comme dernier recours. Le résultat clé est une réduction de latence allant jusqu'à 80%."

---

## Slide 6 : Scénarios de Simulation
> "Pour valider notre approche, nous avons défini 3 scénarios comparatifs. Le premier, Edge+Cloud, sert de référence avec 0% de fog et SCOOT désactivé. Le deuxième, Low Fog, a 10% de véhicules fog-capable avec SCOOT activé. Le troisième, High Fog, monte à 50% de fog nodes."
>
> "Le point crucial est que le débit de trafic est identique — 2000 véhicules par heure — dans les trois scénarios. Seule la densité de fog nodes change?. Donc toute différence de performance est uniquement due au fog."

---

## Slide 7 : Stratégie d'Offloading Multi-Critères
> "L'algorithme d'offloading choisit la meilleure destination pour chaque tâche en minimisant une fonction qui combine le temps d'exécution, la latence réseau et le coût énergétique."
>
> "Le temps total d'offloading inclut l'upload, l'exécution et le download. Les coefficients de pondération donnent la priorité à la latence avec un poids de 0.35, suivie de la taille de tâche et la congestion à 0.25 chacune."

---

## Slide 8 : Mécanisme de Capacité RSU et Overflow
> "Un point essentiel de notre modèle : chaque RSU a une capacité limitée d'environ 8 véhicules simultanés. Quand un RSU est surchargé, les tâches sont redirigées vers un véhicule fog voisin, ou en dernier recours vers le Cloud avec une pénalité massive de 250 ms."
>
> "La latence V2V diminue quand la densité fog augmente, ce qui est logique : plus il y a de fog nodes, plus il y a de relais disponibles à proximité."

---

## Slide 9 : Code — Décision d'Offloading
> "Voici le code Java dans iFogSim qui implémente cette décision. D'abord, on vérifie si le RSU est surchargé. Ensuite, on calcule les latences dynamiques en fonction de la densité fog. Puis c'est l'arbre de décision : petite tâche → local, RSU disponible → RSU, sinon fog V2V, et en dernier recours le Cloud."

---

## Slide 10 : Outils et Algorithmes Utilisés
> "Notre plateforme de simulation combine plusieurs outils : SUMO pour la simulation microscopique du trafic, iFogSim pour les calculs de Fog Computing, Python/Flask comme orchestrateur central avec un dashboard temps réel, SCOOT pour le contrôle adaptatif des feux, et TraCI pour le contrôle de SUMO en temps réel."
>
> "La communication se fait ainsi : SUMO communique avec l'orchestrateur Python via TraCI, et l'orchestrateur communique avec iFogSim via un socket TCP sur le port 5555."

---

## Slide 11 : Algorithme SCOOT Adaptatif
> "SCOOT — Split Cycle Offset Optimization Technique — est notre algorithme de contrôle adaptatif des feux. Il mesure les files d'attente en temps réel, ajuste dynamiquement les phases de feux, et optimise par zone RSU."
>
> "Le code montre le calcul du split optimal : on répartit le temps de vert proportionnellement aux files d'attente Nord-Sud et Est-Ouest. Le Performance Index mesure le niveau de saturation."

---

## Slide 12 : Code — Configuration SUMO et TraCI
> "À gauche, la configuration des routes SUMO avec les deux types de véhicules : les voitures standards en bleu et les véhicules fog-capable en vert. À droite, le code Python qui se connecte à SUMO via TraCI, récupère la position et la vitesse de chaque véhicule, et applique les décisions SCOOT aux feux."

---

## Slide 13 : Paramètres de Simulation
> "Voici les paramètres détaillés : notre réseau a 4 RSU aux intersections avec une portée de 300 mètres, des capacités de calcul allant de 500 MIPS pour un véhicule local à 20000 MIPS pour le Cloud, des tâches de 0.5 à 5 Mb, et des latences allant de 5 ms en V2V à 250 ms pour le Cloud."

---

## Slide 14 : Détail des Scénarios de Trafic
> "Ce tableau détaille les trois scénarios. Tous ont le même débit de 2000 véhicules par heure. La différence est dans la proportion de véhicules fog-capable : 0% pour Edge+Cloud, 10% pour Low Fog, et 50% pour High Fog. Fog et SCOOT sont activés uniquement dans les scénarios fog."

---

## Slide 15 : Métriques Évaluées
> "Nous évaluons 6 métriques : la latence moyenne pondérée, la distribution du traitement entre Edge/Fog/Cloud, le nombre de fog nodes actifs, les feux ajustés par SCOOT, les véhicules reroutés, et la congestion maximale par zone."

---

## Slide 16 : Formules des Métriques
> "La latence moyenne est une moyenne pondérée : chaque composant — edge, fog, cloud — contribue à la latence proportionnellement à sa part de traitement. Le niveau de congestion est normalisé : 25 véhicules ou plus dans une zone correspondent à 100% de congestion."

---

## Slide 17 : Résultats — Tableau Comparatif
> "Voici le tableau récapitulatif de nos résultats. Le résultat le plus frappant est la latence moyenne : 90 ms en Edge+Cloud, 35 ms en Low Fog — soit une réduction de 61% — et seulement 18 ms en High Fog, soit une réduction de 80%. Notez aussi les 360 ajustements SCOOT en High Fog contre 0 en Edge+Cloud."

---

## Slide 18 : Résultats — Latence Moyenne
> "Ce graphique montre clairement l'impact du fog. La barre rouge du Edge+Cloud à 90 ms domine, tandis que le High Fog en vert descend à seulement 18 ms. C'est 5 fois moins de latence."

---

## Slide 19 : Résultats — Évolution de la Latence
> "Ce graphique est particulièrement intéressant : il montre que l'écart de latence se creuse à mesure que le nombre de véhicules augmente. Le Edge+Cloud monte jusqu'à 95 ms avec 45 véhicules, tandis que le High Fog reste stable autour de 18-19 ms. La zone verte représente le gain apporté par le fog."

---

## Slide 20 : Résultats — Distribution du Traitement
> "La distribution est révélatrice. En Edge+Cloud, 35% des tâches vont au Cloud. En High Fog, ce n'est que 8% — le fog absorbe 72% des tâches. C'est exactement l'objectif : traiter localement plutôt qu'envoyer au Cloud."

---

## Slide 21 : Résultats — Actions Fog
> "En termes d'actions, le High Fog permet à SCOOT d'ajuster 360 feux et de rerouter plus de 2000 véhicules, contre zéro en Edge+Cloud. Plus de fog nodes signifie plus de décisions locales et plus de réactivité."

---

## Slide 22 : Résultats — Décisions SCOOT en Temps Réel
> "Voici un extrait des logs réels de notre simulation High Fog. On voit SCOOT ajuster le split au carrefour J2, basculer la priorité Nord-Sud au carrefour J1, rerouter 25 véhicules, et étendre les phases vertes. Toutes ces décisions sont prises en moins de 50 ms grâce au traitement fog local."

---

## Slide 23 : Démonstration en Direct
> "Nous allons maintenant lancer les 3 scénarios en direct. Observez sur le dashboard : la latence en temps réel, les ajustements SCOOT, les reroutages, et la distribution du traitement. Vous verrez la différence dramatique entre le scénario Edge+Cloud sans fog et le High Fog."
>
> *(Lancer les démonstrations)*

---

## Slide 24 : Discussion des Résultats
> "En résumé, nous avons démontré 4 observations clés. Premièrement, la réduction de latence peut atteindre 80% avec le High Fog. Deuxièmement, SCOOT est beaucoup plus efficace quand le fog permet des décisions rapides. Troisièmement, les 2077 reroutages en High Fog montrent une gestion proactive de la congestion."
>
> "Un résultat intéressant et contre-intuitif : le High Fog a une congestion maximale plus basse — 63% au lieu de 77% — car SCOOT anticipe et distribue le trafic."

---

## Slide 25 : Avantages et Limites
> "Les avantages sont clairs : latence réduite de 90 à 18 ms, décisions temps réel en moins de 50 ms, pas de point unique de défaillance, et scalabilité proportionnelle au trafic."
>
> "Cependant, nous avons identifié des limites : la performance dépend de la densité fog, la mobilité rend les voisins fog instables, et le déploiement nécessite une infrastructure RSU. Le seuil d'efficacité est d'environ 10% de fog nodes."

---

## Slide 26 : Conclusion
> "Pour conclure, nous avons démontré que le Fog Computing réduit la latence de 80%, que SCOOT optimise les feux en temps réel, et que l'architecture Edge-Fog-Cloud est efficace et scalable pour les VANET."
>
> "Le message clé : le Fog Computing Véhiculaire n'est pas une alternative au Cloud, mais un complément essentiel qui rapproche le calcul des véhicules."

---

## Slide 27 : Perspectives
> "Pour le futur, nous envisageons l'intégration du Machine Learning pour la prédiction de congestion, le support 5G et 6G pour des latences inférieures à 1 ms, et le Federated Learning pour l'apprentissage distribué sur véhicules."

---

## Slide 28 : Références
> "Voici les principales références sur lesquelles nous nous sommes appuyés, notamment les travaux de Bonomi sur le Fog Computing, Hou sur le Vehicular Fog Computing, et les outils iFogSim et SUMO."

---

## Slide 29 : Merci
> "Merci pour votre attention. Nous sommes prêts à répondre à vos questions."

---

## 💡 Conseils Généraux
- **Rythme** : Parler lentement et clairement sur les slides techniques.
- **Pointer** : Utiliser un pointeur pour montrer les éléments clés des graphiques.
- **Interaction** : Regarder l'audience, pas l'écran.
- **Timing** : ~2 min par slide technique, ~1 min pour les slides simples, ~5 min pour la démo.
- **Questions** : Si vous ne savez pas, dites "Bonne question, nous n'avons pas exploré cet aspect mais c'est une piste intéressante."
