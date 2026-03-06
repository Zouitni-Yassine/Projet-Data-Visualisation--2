# 🚌 Analyse des dynamiques de mobilité urbaine à Bordeaux

## Projet Data Visualisation #2

Ce projet analyse les schémas de mobilité urbaine à Bordeaux à partir des données de transport public (GTFS) de TBM (Transports Bordeaux Métropole).

## 📋 Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Résultats](#résultats)
- [Technologies](#technologies)
- [Auteurs](#auteurs)

## 📖 À propos

L'objectif de ce projet est d'analyser les patterns de mobilité urbaine pour répondre aux questions suivantes:

- Quels sont les schémas temporels de fréquentation des transports publics?
- Quelles zones et lignes connaissent des surcharges ou des creux?
- Quels scénarios d'optimisation peuvent être proposés?

## ✨ Fonctionnalités

### Analyse des données
- ✅ Chargement et validation des données GTFS
- ✅ Prétraitement et enrichissement des données
- ✅ Analyse temporelle (heures de pointe, patterns horaires)
- ✅ Analyse par ligne de transport
- ✅ Analyse par arrêt
- ✅ Analyse géographique

### Visualisations
- 📊 **Heatmap temporelle** - Visualisation de la fréquentation par heure et jour
- 📈 **Distribution horaire** - Évolution de la fréquentation sur 24h
- 🏆 **Top lignes** - Classement des lignes les plus fréquentées
- 🚏 **Top arrêts** - Classement des arrêts principaux
- 🗺️ **Carte interactive** - Heatmap géographique avec marqueurs (Folium)
- 💻 **Dashboards interactifs** - Visualisations Plotly exploratoires

### Livrables
- 📝 Rapport final (Markdown)
- 💡 Recommandations d'optimisation
- 📊 Visualisations statiques (PNG haute résolution)
- 🌐 Visualisations interactives (HTML)
- 📓 Notebook Jupyter pour exploration

## 📁 Structure du projet

```
Data_Vise_V2/
├── src/                        # Code source
│   ├── __init__.py
│   ├── config.py              # Configuration du projet
│   ├── data_loader.py         # Chargement des données GTFS
│   ├── preprocessor.py        # Prétraitement des données
│   ├── analyzer.py            # Analyse exploratoire
│   └── visualizer.py          # Création des visualisations
├── Data/                       # Données GTFS (non incluses)
│   ├── agency.txt
│   ├── stops.txt
│   ├── routes.txt
│   ├── trips.txt
│   ├── stop_times.txt
│   └── ...
├── visualisations/            # Outputs (générés automatiquement)
│   ├── heatmap_temporel.png
│   ├── distribution_horaire.png
│   ├── top_lignes.png
│   ├── top_arrets.png
│   ├── carte_interactive.html
│   ├── dashboard_horaire.html
│   └── dashboard_lignes.html
├── notebooks/                 # Notebooks Jupyter
│   └── exploration_interactive.ipynb
├── main.py                    # Point d'entrée principal
├── requirements.txt           # Dépendances Python
├── RAPPORT_FINAL.md          # Rapport d'analyse (généré)
├── recommandations.txt       # Recommandations (généré)
├── analysis.log              # Logs d'exécution (généré)
└── README.md                 # Ce fichier

```

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip

### Étapes

1. Cloner ou télécharger le projet

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Placer les données GTFS dans le dossier `Data/`
   - Télécharger depuis [Mobility Database](https://mobilitydatabase.org/) ou [data.gouv.fr](https://www.data.gouv.fr/)
   - Fichiers requis: `agency.txt`, `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`

## 💻 Utilisation

### Analyse complète (recommandé)

Exécutez le script principal qui effectue toute l'analyse:

```bash
python main.py
```

Ce script va:
1. Charger les données GTFS
2. Prétraiter et enrichir les données
3. Effectuer l'analyse exploratoire
4. Créer toutes les visualisations
5. Générer le rapport et les recommandations

### Exploration interactive

Utilisez le notebook Jupyter pour une exploration personnalisée:

```bash
jupyter notebook notebooks/exploration_interactive.ipynb
```

### Utilisation programmatique

```python
from src.data_loader import GTFSDataLoader
from src.preprocessor import GTFSPreprocessor
from src.analyzer import MobilityAnalyzer
from src.visualizer import MobilityVisualizer

# Charger les données
loader = GTFSDataLoader()
data = loader.load_all()

# Prétraiter
preprocessor = GTFSPreprocessor(data)
data_enriched = preprocessor.preprocess_all()

# Analyser
analyzer = MobilityAnalyzer(data_enriched)
results = analyzer.analyze_all()

# Visualiser
visualizer = MobilityVisualizer(data_enriched, results)
visualizer.create_all_visualizations()
```

## 📊 Résultats

Après exécution, vous trouverez:

### Visualisations statiques (PNG)
- `visualisations/heatmap_temporel.png` - Heatmap jour/heure
- `visualisations/distribution_horaire.png` - Courbe de fréquentation
- `visualisations/top_lignes.png` - Barres des lignes principales
- `visualisations/top_arrets.png` - Barres des arrêts principaux

### Visualisations interactives (HTML)
- `visualisations/carte_interactive.html` - Carte Folium avec heatmap
- `visualisations/dashboard_horaire.html` - Dashboard Plotly horaire
- `visualisations/dashboard_lignes.html` - Dashboard Plotly lignes

### Rapports
- `RAPPORT_FINAL.md` - Rapport complet en Markdown
- `recommandations.txt` - Liste des recommandations d'optimisation
- `analysis.log` - Logs détaillés de l'exécution

## 🛠️ Technologies

### Langages et frameworks
- **Python 3.8+** - Langage principal
- **Pandas** - Manipulation de données
- **NumPy** - Calculs numériques

### Visualisation
- **Matplotlib** - Graphiques statiques
- **Seaborn** - Graphiques statistiques
- **Plotly** - Visualisations interactives
- **Folium** - Cartes interactives

### Outils
- **Jupyter** - Notebooks interactifs
- **GTFS** - Format de données de transport

## 📈 Exemples de résultats

### Insights typiques obtenus:

- **Heures de pointe**: Identification des périodes de forte affluence
- **Lignes critiques**: 20% des lignes concentrent 80% du trafic
- **Zones denses**: Cartographie des zones à forte fréquentation
- **Optimisations**: Recommandations concrètes pour améliorer le service

### Recommandations types:

1. **Optimisation temporelle**: Renforcer la fréquence aux heures de pointe
2. **Équilibrage du réseau**: Créer des lignes express parallèles
3. **Infrastructure**: Améliorer les arrêts principaux
4. **Rationalisation**: Optimiser ou supprimer les arrêts sous-utilisés

## 🤝 Contribution

Ce projet a été développé dans le cadre du **Projet Data Visualisation #2** sur l'analyse de la mobilité urbaine.

### Améliorations possibles:

- [ ] Ajouter l'analyse par jour de la semaine (utiliser calendar.txt)
- [ ] Intégrer des données de fréquentation réelle
- [ ] Ajouter des modèles prédictifs (ML)
- [ ] Créer un dashboard web complet (Dash/Streamlit)
- [ ] Comparer avec d'autres villes

## 📝 License

Ce projet est développé à des fins éducatives dans le cadre d'un projet académique.

## 🙏 Remerciements

- **TBM** (Transports Bordeaux Métropole) pour les données GTFS
- **Mobility Database** pour l'agrégation des données de transport
- La communauté Python pour les bibliothèques open-source

## 📧 Contact

Pour toute question ou suggestion concernant ce projet, n'hésitez pas à ouvrir une issue.

---

*Généré dans le cadre du Projet Data Visualisation #2 - Mars 2026*
