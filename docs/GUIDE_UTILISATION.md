# Guide d'Utilisation - Analyse Mobilité Urbaine Bordeaux

## 🎯 Projet Réalisé avec Succès!

Toutes les analyses et visualisations ont été générées avec succès à partir des données TBM de Bordeaux.

## 📊 Résultats Clés

### Données Analysées
- **2,195,275 passages** de bus/tramway
- **3,957 arrêts** uniques
- **133 lignes** de transport
- **57,084 trajets** différents

### Insights Principaux

#### 🕐 Patterns Temporels
- **Heure de pointe**: 17h (147,683 passages)
- **Heure creuse**: 3h (1,142 passages)
- **Ratio**: 129.3x plus de trafic en pointe!
- **Rush matinal**: 7h-9h (avg 124,496 passages/heure)
- **Rush du soir**: 17h-19h (avg 143,468 passages/heure)

#### 🚌 Lignes Principales
**Top 5:**
1. Ligne B (Tramway) - 172,953 passages
2. Ligne 31 (Bus) - 138,951 passages
3. Ligne 35 (Bus) - 131,771 passages
4. Ligne A (Tramway) - 125,297 passages
5. Ligne 7 (Bus) - 105,227 passages

#### 🚏 Arrêts Stratégiques
**Top 5:**
1. Palais de Justice - 4,516 passages
2. Quinconces - 4,387 passages
3. Place de la Bourse - 4,367 passages
4. Belcier - 4,268 passages
5. Porte de Bourgogne - 4,268 passages

## 📁 Fichiers Générés

### 📝 Rapports et Recommandations
- `docs/RAPPORT_FINAL.md` - Rapport complet de l'analyse (5KB)
- `docs/recommandations.txt` - 4 recommandations concrètes d'optimisation (1.8KB)
- `docs/GUIDE_UTILISATION.md` - Ce guide (6.3KB)

### 📊 Visualisations Statiques (PNG - Haute Résolution)
**Total: 8 visualisations** dans [visualisations/](visualisations/)

1. **heatmap_temporel.png** (150KB) - Heatmap jour × heure
2. **distribution_horaire.png** (309KB) - Distribution 24h avec zones de rush
3. **top_lignes.png** (173KB) - Top 15 lignes les plus fréquentées
4. **top_arrets.png** (207KB) - Top 15 arrêts les plus fréquentés
5. **heatmap_ligne_heure.png** (169KB) ⭐ - Heatmap 2D Ligne × Heure
6. **scatter_geo_frequentation.png** (1.4MB) ⭐ - Scatter géographique pondéré (Top 800 arrêts)
7. **graphique_types.png** (194KB) ⭐ - Répartition par type de transport (Bus/Tramway/Ferry)
8. **distribution_geographique.png** (175KB) ⭐ - Distributions latitude/longitude

### 🌐 Visualisations Interactives (HTML)
**Total: 5 cartes/dashboards** - Ouvrir dans un navigateur web

1. **carte_interactive_tous_arrets.html** (5.3MB) ⭐
   - Carte Folium avec TOUS les 3,957 arrêts
   - Clusters intelligents avec couleurs par fréquentation (rouge/orange/bleu)
   - Popups détaillés sur chaque arrêt

2. **carte_chaleur.html** (115KB) ⭐
   - Heatmap pure de la fréquentation
   - Gradient 6 couleurs (bleu → rouge)
   - Légende intégrée

3. **dashboard_horaire.html** (4.7MB)
   - Graphique Plotly interactif de la distribution horaire
   - Zoom, pan, export d'image

4. **dashboard_lignes.html** (4.7MB)
   - Top 20 lignes interactif avec Plotly

3. **dashboard_lignes.html** (4.7MB)
   - Barres interactives des top 20 lignes
   - Couleurs dynamiques
   - Filtrable et zoomable

## 💻 Comment Explorer les Résultats

### 1. Lire le Rapport
```bash
# Ouvrir avec votre éditeur Markdown préféré
code RAPPORT_FINAL.md
# ou dans le navigateur (si vous avez un lecteur MD)
```

### 2. Consulter les Recommandations
```bash
cat recommandations.txt
# ou
notepad recommandations.txt
```

### 3. Visualisations Statiques
```bash
# Ouvrir toutes les images
cd visualisations/
# Sous Windows
start heatmap_temporel.png
start distribution_horaire.png
start top_lignes.png
start top_arrets.png
```

### 4. Visualisations Interactives
```bash
# Ouvrir dans le navigateur par défaut
start visualisations/carte_interactive.html
start visualisations/dashboard_horaire.html
start visualisations/dashboard_lignes.html
```

### 5. Exploration avec Jupyter
```bash
jupyter notebook notebooks/exploration_interactive.ipynb
```

## 🔧 Relancer l'Analyse

Si vous souhaitez modifier l'analyse ou l'exécuter avec d'autres paramètres:

```bash
# Méthode 1: Script principal (automatique)
python main.py

# Méthode 2: Personnalisée (programmatique)
python
>>> from src.data_loader import GTFSDataLoader
>>> from src.analyzer import MobilityAnalyzer
>>> # ... votre code personnalisé
```

## 📦 Structure du Projet

```
Data_Vise_V2/
├── src/                        # Code source modulaire
│   ├── data_loader.py         # Chargement GTFS
│   ├── preprocessor.py        # Nettoyage/enrichissement
│   ├── analyzer.py            # Analyses statistiques
│   ├── visualizer.py          # Création visualisations
│   └── config.py              # Configuration centrale
├── Data/                       # Données GTFS de TBM
├── visualisations/            # Outputs générés ✅
├── notebooks/                 # Jupyter pour exploration
├── main.py                    # Point d'entrée
├── RAPPORT_FINAL.md          # Rapport complet ✅
├── recommandations.txt       # Recommandations ✅
└── README.md                 # Documentation projet
```

## 💡 Recommandations Générées

L'analyse a produit **4 recommandations** concrètes:

### ⚡ Priorité Haute
1. **Optimisation temporelle**: Renforcer la fréquence 16h-18h (heure de pointe 17h)
2. **Équilibrage réseau**: Lignes express parallèles pour B, 31, 35 (forte concentration)

### 🔧 Priorité Moyenne
3. **Infrastructure**: Améliorer arrêt "Palais de Justice" (le plus fréquenté)

### 📉 Priorité Basse
4. **Rationalisation**: 1,014 arrêts sous-utilisés (25.6%) à réévaluer

Voir [recommandations.txt](recommandations.txt) pour les détails complets.

## 🎓 Livrables du Projet Data Visualisation #2

✅ Toutes les exigences ont été remplies:

- [x] **Définition problématique** - Optimisation mobilité urbaine Bordeaux
- [x] **Collecte données** - GTFS TBM (2.2M passages)
- [x] **Prétraitement** - Nettoyage, fusion, enrichissement
- [x] **Analyse exploratoire** - Patterns temporels, géographiques, par ligne/arrêt
- [x] **Visualisations avancées** - Cartes, heatmaps, dashboards interactifs
- [x] **Rapport final** - RAPPORT_FINAL.md (Markdown)
- [x] **Recommandations** - 4 scénarios d'optimisation concrets
- [x] **Code source documenté** - Architecture clean, modulaire
- [x] **Dashboard interactif** - 3 dashboards HTML (Folium + Plotly)

## 📧 Support

Pour toute question sur l'utilisation:
- Consulter le [README.md](README.md) principal
- Explorer le code source dans `src/`

---


*Analyse des dynamiques de mobilité urbaine à Bordeaux - TBM*
