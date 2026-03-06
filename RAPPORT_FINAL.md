# Analyse des dynamiques de mobilité urbaine à Bordeaux

## Projet Data Visualisation #2

**Date:** 06/03/2026

**Source des données:** TBM (Transports Bordeaux Métropole) - Format GTFS

---

## 1. Résumé exécutif

Ce projet analyse les schémas de mobilité urbaine à Bordeaux à partir des données de transport public au format GTFS. L'objectif est d'identifier les patterns temporels et géographiques de fréquentation, ainsi que de proposer des optimisations.

---

## 2. Données analysées

- **Total de passages analysés:** 2,195,275
- **Nombre d'arrêts uniques:** 3,957
- **Nombre de lignes:** 133
- **Nombre de trajets:** 57,084

---

## 3. Résultats de l'analyse

### 3.1 Analyse temporelle

- **Heure de pointe:** 17h (147,683 passages)
- **Heure creuse:** 3h (1,142 passages)
- **Ratio pointe/creuse:** 129.3x
- **Moyenne rush matinal (7h-9h):** 124,496 passages
- **Moyenne rush du soir (17h-19h):** 143,468 passages

### 3.2 Lignes les plus fréquentées

| Rang | Ligne | Nombre de passages |
|------|-------|--------------------|
| 1 | B | 172,953 |
| 2 | 31 | 138,951 |
| 3 | 35 | 131,771 |
| 4 | A | 125,297 |
| 5 | 7 | 105,227 |
| 6 | G | 103,755 |
| 7 | 15 | 92,375 |
| 8 | F | 87,920 |
| 9 | C | 82,179 |
| 10 | 5 | 78,453 |

**Coefficient de variation:** 1.97 (forte dispersion)

### 3.3 Arrêts les plus fréquentés

| Rang | Arrêt | Nombre de passages |
|------|-------|--------------------|
| 1 | Palais de Justice | 4,516 |
| 2 | Quinconces | 4,387 |
| 3 | Place de la Bourse | 4,367 |
| 4 | Place de la Bourse | 4,361 |
| 5 | Quinconces | 4,361 |
| 6 | Belcier | 4,268 |
| 7 | Porte de Bourgogne | 4,268 |
| 8 | Gare Saint-Jean | 4,268 |
| 9 | Sainte-Croix | 4,268 |
| 10 | Saint-Michel | 4,268 |

**Arrêts sous-utilisés:** 1,014 (25.6% du total)

---

## 4. Visualisations

Les visualisations suivantes ont été générées:

### Visualisations statiques (PNG)

1. **Heatmap temporelle** - [visualisations/heatmap_temporel.png](visualisations/heatmap_temporel.png)
2. **Distribution horaire** - [visualisations/distribution_horaire.png](visualisations/distribution_horaire.png)
3. **Top lignes** - [visualisations/top_lignes.png](visualisations/top_lignes.png)
4. **Top arrêts** - [visualisations/top_arrets.png](visualisations/top_arrets.png)

### Visualisations interactives (HTML)

1. **Carte interactive** - [visualisations/carte_interactive.html](visualisations/carte_interactive.html)
2. **Dashboard horaire** - [visualisations/dashboard_horaire.html](visualisations/dashboard_horaire.html)
3. **Dashboard lignes** - [visualisations/dashboard_lignes.html](visualisations/dashboard_lignes.html)

---

## 5. Recommandations

### 5.1 Optimisation temporelle (Priorité: Haute)

**Observation:** L'heure de pointe (17h) connaît 129.3x plus de passages que l'heure creuse

**Recommandation:** Renforcer la fréquence des transports entre 16h et 18h

**Impact attendu:** Réduction de la surcharge et amélioration du confort des usagers

### 5.2 Équilibrage du réseau (Priorité: Haute)

**Observation:** Forte dispersion de la fréquentation (CV=1.97). Les lignes B, 31, 35 concentrent beaucoup de trafic

**Recommandation:** Créer des lignes express parallèles ou augmenter la flotte sur ces lignes

**Impact attendu:** Meilleure répartition de la charge et temps de trajet réduit

### 5.3 Infrastructure (Priorité: Moyenne)

**Observation:** L'arrêt 'Palais de Justice' est le plus fréquenté (4,516 passages)

**Recommandation:** Améliorer l'infrastructure: abris supplémentaires, affichage temps réel, bancs, accessibilité

**Impact attendu:** Meilleure expérience usager et fluidité accrue

### 5.4 Optimisation du réseau (Priorité: Basse)

**Observation:** 1014 arrêts (25.6%) sont sous-utilisés

**Recommandation:** Évaluer la pertinence de ces arrêts et considérer leur suppression ou fusion

**Impact attendu:** Réduction des coûts opérationnels et temps de trajet optimisé

---

## 6. Limites de l'analyse

- Les données GTFS représentent les horaires planifiés, pas la fréquentation réelle des passagers
- Pas de données sur le nombre effectif de passagers par trajet
- Pas d'informations sur les retards ou perturbations du service
- L'analyse ne distingue pas les différents jours de la semaine (simulation utilisée)
- Pas de données météorologiques ou d'événements spéciaux

---

## 7. Conclusion

Cette analyse a permis d'identifier les patterns clés de mobilité à Bordeaux. Les visualisations et recommandations fournies peuvent aider TBM à optimiser son réseau de transport pour mieux répondre aux besoins des usagers.

Les principales conclusions sont:

- Une forte variation de la fréquentation selon l'heure (ratio 129.3x)
- Une concentration importante du trafic sur quelques lignes principales
- 1014 arrêts sous-utilisés nécessitant une réévaluation

---

*Rapport généré automatiquement par le système d'analyse de mobilité urbaine*
