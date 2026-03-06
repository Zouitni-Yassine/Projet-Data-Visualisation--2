"""
Projet Data Visualisation #2
Analyse des dynamiques de mobilité urbaine à Bordeaux
Données: TBM (Transports Bordeaux Métropole) - Format GTFS

Auteur: Analyse des transports publics de Bordeaux
Date: Mars 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class AnalyseMobiliteBordeaux:
    """Classe principale pour l'analyse des données de mobilité"""

    def __init__(self, data_path='Data/'):
        """
        Initialise l'analyse avec le chemin vers les données GTFS

        Args:
            data_path (str): Chemin vers le dossier contenant les fichiers GTFS
        """
        self.data_path = data_path
        self.stops = None
        self.routes = None
        self.trips = None
        self.stop_times = None
        self.calendar = None
        self.agency = None

        print("="*70)
        print("ANALYSE DES DYNAMIQUES DE MOBILITÉ URBAINE À BORDEAUX")
        print("="*70)

    def charger_donnees(self):
        """Charge tous les fichiers GTFS en mémoire"""
        print("\n[1/7] Chargement des données GTFS...")

        try:
            # Chargement des fichiers principaux
            self.agency = pd.read_csv(f'{self.data_path}agency.txt')
            self.stops = pd.read_csv(f'{self.data_path}stops.txt')
            self.routes = pd.read_csv(f'{self.data_path}routes.txt')
            self.trips = pd.read_csv(f'{self.data_path}trips.txt')
            self.calendar = pd.read_csv(f'{self.data_path}calendar.txt')

            # Chargement du fichier volumineux stop_times (peut prendre du temps)
            print("   → Chargement de stop_times.txt (2M+ lignes)...")
            self.stop_times = pd.read_csv(f'{self.data_path}stop_times.txt')

            print(f"   ✓ Données chargées avec succès!")
            print(f"     - {len(self.stops):,} arrêts")
            print(f"     - {len(self.routes):,} lignes")
            print(f"     - {len(self.trips):,} trajets")
            print(f"     - {len(self.stop_times):,} horaires d'arrêt")

        except Exception as e:
            print(f"   ✗ Erreur lors du chargement: {e}")
            raise

    def pretraiter_donnees(self):
        """Nettoie et prépare les données pour l'analyse"""
        print("\n[2/7] Pré-traitement des données...")

        # Conversion des horaires
        print("   → Conversion des horaires...")
        self.stop_times['arrival_time'] = pd.to_timedelta(self.stop_times['arrival_time'])
        self.stop_times['departure_time'] = pd.to_timedelta(self.stop_times['departure_time'])

        # Extraction de l'heure (0-23)
        self.stop_times['hour'] = self.stop_times['arrival_time'].dt.components['hours']
        # Gérer les heures > 23 (ex: 25:00 = 1h du matin le lendemain)
        self.stop_times['hour'] = self.stop_times['hour'] % 24

        # Fusion avec les informations d'arrêts
        print("   → Fusion des tables...")
        self.stop_times = self.stop_times.merge(
            self.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']],
            on='stop_id',
            how='left'
        )

        # Fusion avec les informations de trajets et routes
        self.stop_times = self.stop_times.merge(
            self.trips[['trip_id', 'route_id', 'trip_headsign']],
            on='trip_id',
            how='left'
        )

        self.stop_times = self.stop_times.merge(
            self.routes[['route_id', 'route_short_name', 'route_long_name', 'route_type']],
            on='route_id',
            how='left'
        )

        # Suppression des valeurs manquantes critiques
        avant = len(self.stop_times)
        self.stop_times = self.stop_times.dropna(subset=['stop_lat', 'stop_lon', 'hour'])
        apres = len(self.stop_times)

        print(f"   ✓ Pré-traitement terminé")
        print(f"     - {avant - apres:,} lignes supprimées (valeurs manquantes)")
        print(f"     - {apres:,} lignes conservées")

    def analyse_exploratoire(self):
        """Réalise l'analyse exploratoire des données"""
        print("\n[3/7] Analyse exploratoire des données...")

        # 1. Fréquentation par heure
        print("\n   → Analyse temporelle:")
        freq_heure = self.stop_times.groupby('hour').size()
        print(f"     - Heures de pointe: {freq_heure.nlargest(3).index.tolist()}")
        print(f"     - Heures creuses: {freq_heure.nsmallest(3).index.tolist()}")

        # 2. Lignes les plus fréquentées
        print("\n   → Analyse par ligne:")
        freq_ligne = self.stop_times.groupby('route_short_name').size().sort_values(ascending=False)
        print("     - Top 5 lignes les plus fréquentées:")
        for ligne, freq in freq_ligne.head(5).items():
            print(f"       • Ligne {ligne}: {freq:,} passages")

        # 3. Arrêts les plus fréquentés
        print("\n   → Analyse par arrêt:")
        freq_arret = self.stop_times.groupby(['stop_id', 'stop_name']).size().sort_values(ascending=False)
        print("     - Top 5 arrêts les plus fréquentés:")
        for (stop_id, stop_name), freq in freq_arret.head(5).items():
            print(f"       • {stop_name}: {freq:,} passages")

        # 4. Type de transport
        print("\n   → Répartition par type de transport:")
        type_map = {0: 'Tramway', 1: 'Métro', 2: 'Train', 3: 'Bus'}
        freq_type = self.stop_times.groupby('route_type').size()
        for route_type, count in freq_type.items():
            nom_type = type_map.get(route_type, f'Type {route_type}')
            print(f"       • {nom_type}: {count:,} passages ({count/len(self.stop_times)*100:.1f}%)")

        return {
            'freq_heure': freq_heure,
            'freq_ligne': freq_ligne,
            'freq_arret': freq_arret,
            'freq_type': freq_type
        }

    def creer_visualisations(self, stats):
        """Crée les visualisations demandées"""
        print("\n[4/7] Création des visualisations...")

        # 1. Heatmap temporel (affluence par heure)
        print("   → Création de la heatmap temporelle...")
        self._heatmap_temporel(stats['freq_heure'])

        # 2. Graphique des lignes les plus fréquentées
        print("   → Graphique des lignes principales...")
        self._graphique_lignes(stats['freq_ligne'])

        # 3. Distribution horaire
        print("   → Distribution horaire des passages...")
        self._distribution_horaire(stats['freq_heure'])

        # 4. Carte des arrêts
        print("   → Création de la carte interactive...")
        self._carte_arrets()

        print("   ✓ Visualisations créées avec succès!")

    def _heatmap_temporel(self, freq_heure):
        """Crée une heatmap de l'affluence par heure"""
        # Créer une matrice pour la heatmap (jour de la semaine x heure)
        # Pour simplifier, on simule 7 jours avec la même distribution
        heures = range(24)
        jours = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

        # Créer une matrice (on répète le pattern pour chaque jour)
        data = []
        for _ in jours:
            data.append([freq_heure.get(h, 0) for h in heures])

        plt.figure(figsize=(14, 6))
        sns.heatmap(data,
                    xticklabels=heures,
                    yticklabels=jours,
                    cmap='YlOrRd',
                    annot=False,
                    fmt='d',
                    cbar_kws={'label': 'Nombre de passages'})
        plt.title('Heatmap de la fréquentation par heure de la journée',
                  fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Heure de la journée', fontsize=12)
        plt.ylabel('Jour de la semaine', fontsize=12)
        plt.tight_layout()
        plt.savefig('visualisations/heatmap_temporel.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _graphique_lignes(self, freq_ligne):
        """Crée un graphique des lignes les plus fréquentées"""
        top_lignes = freq_ligne.head(15)

        plt.figure(figsize=(12, 6))
        bars = plt.barh(range(len(top_lignes)), top_lignes.values, color='steelblue')
        plt.yticks(range(len(top_lignes)), top_lignes.index)
        plt.xlabel('Nombre de passages', fontsize=12)
        plt.ylabel('Ligne', fontsize=12)
        plt.title('Top 15 des lignes les plus fréquentées à Bordeaux',
                  fontsize=14, fontweight='bold', pad=20)

        # Ajouter les valeurs sur les barres
        for i, (idx, val) in enumerate(top_lignes.items()):
            plt.text(val, i, f' {val:,}', va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig('visualisations/top_lignes.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _distribution_horaire(self, freq_heure):
        """Crée un graphique de distribution horaire"""
        plt.figure(figsize=(14, 6))

        heures = list(range(24))
        valeurs = [freq_heure.get(h, 0) for h in heures]

        plt.plot(heures, valeurs, marker='o', linewidth=2, markersize=8, color='darkblue')
        plt.fill_between(heures, valeurs, alpha=0.3, color='skyblue')

        # Identifier les heures de pointe
        max_idx = valeurs.index(max(valeurs))
        plt.axvline(x=max_idx, color='red', linestyle='--', linewidth=2,
                    label=f'Heure de pointe: {max_idx}h')

        plt.xlabel('Heure de la journée', fontsize=12)
        plt.ylabel('Nombre de passages', fontsize=12)
        plt.title('Distribution de la fréquentation tout au long de la journée',
                  fontsize=14, fontweight='bold', pad=20)
        plt.xticks(heures, [f'{h}h' for h in heures], rotation=45)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig('visualisations/distribution_horaire.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _carte_arrets(self):
        """Crée une carte interactive des arrêts avec folium"""
        # Calculer la fréquentation par arrêt
        freq_arret = self.stop_times.groupby(['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).size().reset_index()
        freq_arret.columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'frequentation']

        # Filtrer les arrêts valides
        freq_arret = freq_arret.dropna(subset=['stop_lat', 'stop_lon'])

        # Centre de Bordeaux
        center_lat = freq_arret['stop_lat'].mean()
        center_lon = freq_arret['stop_lon'].mean()

        # Créer la carte
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )

        # Ajouter une heatmap de la fréquentation
        heat_data = [[row['stop_lat'], row['stop_lon'], row['frequentation']]
                     for idx, row in freq_arret.iterrows()]
        HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(m)

        # Ajouter les top arrêts comme marqueurs
        top_arrets = freq_arret.nlargest(50, 'frequentation')
        marker_cluster = MarkerCluster().add_to(m)

        for idx, row in top_arrets.iterrows():
            folium.Marker(
                location=[row['stop_lat'], row['stop_lon']],
                popup=f"<b>{row['stop_name']}</b><br>{row['frequentation']:,} passages",
                tooltip=row['stop_name'],
                icon=folium.Icon(color='red', icon='bus', prefix='fa')
            ).add_to(marker_cluster)

        # Sauvegarder
        m.save('visualisations/carte_arrets_bordeaux.html')

    def creer_dashboard_interactif(self):
        """Crée un dashboard interactif avec Plotly"""
        print("\n[5/7] Création du dashboard interactif...")

        # Préparer les données
        freq_heure = self.stop_times.groupby('hour').size().reset_index()
        freq_heure.columns = ['hour', 'count']

        freq_ligne = self.stop_times.groupby('route_short_name').size().reset_index()
        freq_ligne.columns = ['ligne', 'count']
        freq_ligne = freq_ligne.sort_values('count', ascending=False).head(20)

        # Créer le graphique interactif
        fig = go.Figure()

        # Graphique de distribution horaire
        fig.add_trace(go.Scatter(
            x=freq_heure['hour'],
            y=freq_heure['count'],
            mode='lines+markers',
            name='Fréquentation horaire',
            line=dict(color='royalblue', width=3),
            marker=dict(size=10),
            hovertemplate='<b>Heure:</b> %{x}h<br><b>Passages:</b> %{y:,}<extra></extra>'
        ))

        fig.update_layout(
            title='Dashboard Interactif - Mobilité Urbaine à Bordeaux',
            xaxis_title='Heure de la journée',
            yaxis_title='Nombre de passages',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )

        fig.write_html('visualisations/dashboard_interactif.html')

        # Créer un second graphique pour les lignes
        fig2 = px.bar(
            freq_ligne,
            x='ligne',
            y='count',
            title='Top 20 des lignes les plus fréquentées',
            labels={'ligne': 'Ligne', 'count': 'Nombre de passages'},
            color='count',
            color_continuous_scale='Viridis'
        )

        fig2.update_layout(
            xaxis_title='Ligne de transport',
            yaxis_title='Nombre de passages',
            template='plotly_white',
            height=600
        )

        fig2.write_html('visualisations/dashboard_lignes.html')

        print("   ✓ Dashboards interactifs créés!")
        print("     - dashboard_interactif.html")
        print("     - dashboard_lignes.html")

    def generer_recommandations(self, stats):
        """Génère des recommandations basées sur l'analyse"""
        print("\n[6/7] Génération des recommandations...")

        recommandations = []

        # 1. Heures de pointe
        freq_heure = stats['freq_heure']
        heure_pointe = freq_heure.idxmax()
        val_pointe = freq_heure.max()
        val_creuse = freq_heure.min()
        ratio = val_pointe / val_creuse

        recommandations.append({
            'categorie': 'Optimisation temporelle',
            'observation': f"L'heure de pointe est à {heure_pointe}h avec {val_pointe:,} passages, soit {ratio:.1f}x plus que l'heure creuse",
            'recommandation': f"Augmenter la fréquence des bus/trams entre {heure_pointe-1}h et {heure_pointe+1}h pour réduire la surcharge"
        })

        # 2. Lignes surchargées
        freq_ligne = stats['freq_ligne']
        top_3_lignes = freq_ligne.head(3)

        recommandations.append({
            'categorie': 'Optimisation des lignes',
            'observation': f"Les lignes {', '.join(map(str, top_3_lignes.index))} concentrent une part importante du trafic",
            'recommandation': "Envisager d'ajouter des véhicules supplémentaires sur ces lignes ou créer des lignes express parallèles"
        })

        # 3. Arrêts critiques
        freq_arret = stats['freq_arret']
        top_arret = freq_arret.head(1)

        recommandations.append({
            'categorie': 'Infrastructure',
            'observation': f"L'arrêt '{top_arret.index[0][1]}' est le plus fréquenté avec {top_arret.values[0]:,} passages",
            'recommandation': "Améliorer l'infrastructure de cet arrêt (abris, bancs, affichage en temps réel) et vérifier sa capacité"
        })

        # 4. Équilibre du réseau
        ecart_type = freq_ligne.std()
        moyenne = freq_ligne.mean()
        cv = ecart_type / moyenne

        recommandations.append({
            'categorie': 'Équilibre du réseau',
            'observation': f"Coefficient de variation de {cv:.2f} indique {'une forte' if cv > 0.5 else 'une faible'} dispersion de la fréquentation entre lignes",
            'recommandation': "Rééquilibrer le réseau en réduisant la fréquence des lignes peu utilisées et en renforçant les lignes principales"
        })

        # Sauvegarder les recommandations
        with open('recommandations.txt', 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("RECOMMANDATIONS D'OPTIMISATION DU RÉSEAU TBM BORDEAUX\n")
            f.write("="*70 + "\n\n")

            for i, rec in enumerate(recommandations, 1):
                f.write(f"\n{i}. {rec['categorie']}\n")
                f.write("-" * 70 + "\n")
                f.write(f"Observation: {rec['observation']}\n")
                f.write(f"Recommandation: {rec['recommandation']}\n")

        print("   ✓ Recommandations générées et sauvegardées dans 'recommandations.txt'")

        return recommandations

    def generer_rapport(self, stats, recommandations):
        """Génère un rapport final en Markdown"""
        print("\n[7/7] Génération du rapport final...")

        with open('RAPPORT_FINAL.md', 'w', encoding='utf-8') as f:
            f.write("# Analyse des dynamiques de mobilité urbaine à Bordeaux\n\n")
            f.write("## Projet Data Visualisation #2\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%d/%m/%Y')}\n\n")
            f.write("**Source des données:** TBM (Transports Bordeaux Métropole) - Format GTFS\n\n")

            f.write("---\n\n")
            f.write("## 1. Problématique\n\n")
            f.write("Ce projet vise à analyser les schémas temporels et géographiques de la fréquentation des transports publics à Bordeaux. ")
            f.write("L'objectif est d'identifier les zones et lignes connaissant des surcharges ou des creux, ")
            f.write("et de proposer des scénarios d'optimisation des lignes et horaires.\n\n")

            f.write("---\n\n")
            f.write("## 2. Données utilisées\n\n")
            f.write("Les données GTFS incluent:\n\n")
            f.write(f"- **{len(self.stops):,}** arrêts de bus/tramway\n")
            f.write(f"- **{len(self.routes):,}** lignes de transport\n")
            f.write(f"- **{len(self.trips):,}** trajets différents\n")
            f.write(f"- **{len(self.stop_times):,}** horaires de passage\n\n")

            f.write("---\n\n")
            f.write("## 3. Résultats de l'analyse\n\n")

            # Heures de pointe
            f.write("### 3.1 Analyse temporelle\n\n")
            freq_heure = stats['freq_heure']
            top_3_heures = freq_heure.nlargest(3)
            f.write("**Heures de pointe:**\n\n")
            for h, v in top_3_heures.items():
                f.write(f"- {h}h: {v:,} passages\n")

            # Lignes principales
            f.write("\n### 3.2 Lignes les plus fréquentées\n\n")
            freq_ligne = stats['freq_ligne']
            top_5_lignes = freq_ligne.head(5)
            f.write("| Ligne | Nombre de passages |\n")
            f.write("|-------|-------------------|\n")
            for ligne, freq in top_5_lignes.items():
                f.write(f"| {ligne} | {freq:,} |\n")

            # Arrêts principaux
            f.write("\n### 3.3 Arrêts les plus fréquentés\n\n")
            freq_arret = stats['freq_arret']
            top_5_arrets = freq_arret.head(5)
            f.write("| Arrêt | Nombre de passages |\n")
            f.write("|-------|-------------------|\n")
            for (stop_id, stop_name), freq in top_5_arrets.items():
                f.write(f"| {stop_name} | {freq:,} |\n")

            f.write("\n---\n\n")
            f.write("## 4. Visualisations\n\n")
            f.write("Les visualisations suivantes ont été générées:\n\n")
            f.write("1. **Heatmap temporel** - `visualisations/heatmap_temporel.png`\n")
            f.write("2. **Top lignes** - `visualisations/top_lignes.png`\n")
            f.write("3. **Distribution horaire** - `visualisations/distribution_horaire.png`\n")
            f.write("4. **Carte interactive** - `visualisations/carte_arrets_bordeaux.html`\n")
            f.write("5. **Dashboard interactif** - `visualisations/dashboard_interactif.html`\n\n")

            f.write("---\n\n")
            f.write("## 5. Recommandations\n\n")
            for i, rec in enumerate(recommandations, 1):
                f.write(f"### 5.{i} {rec['categorie']}\n\n")
                f.write(f"**Observation:** {rec['observation']}\n\n")
                f.write(f"**Recommandation:** {rec['recommandation']}\n\n")

            f.write("---\n\n")
            f.write("## 6. Limites de l'analyse\n\n")
            f.write("- Les données GTFS représentent les horaires théoriques, pas la fréquentation réelle des passagers\n")
            f.write("- Absence de données sur le nombre de passagers par trajet\n")
            f.write("- Pas de données sur les retards ou les perturbations du service\n")
            f.write("- L'analyse temporelle ne distingue pas les jours de semaine des week-ends\n\n")

            f.write("---\n\n")
            f.write("## 7. Conclusion\n\n")
            f.write("Cette analyse a permis d'identifier les patterns de mobilité urbaine à Bordeaux. ")
            f.write("Les visualisations et recommandations fournies peuvent aider TBM à optimiser ")
            f.write("son réseau de transport pour mieux répondre aux besoins des usagers.\n\n")

        print("   ✓ Rapport final généré: RAPPORT_FINAL.md")

    def executer_analyse_complete(self):
        """Exécute l'analyse complète du début à la fin"""
        # Créer le dossier visualisations
        import os
        os.makedirs('visualisations', exist_ok=True)

        # Étapes de l'analyse
        self.charger_donnees()
        self.pretraiter_donnees()
        stats = self.analyse_exploratoire()
        self.creer_visualisations(stats)
        self.creer_dashboard_interactif()
        recommandations = self.generer_recommandations(stats)
        self.generer_rapport(stats, recommandations)

        print("\n" + "="*70)
        print("ANALYSE TERMINÉE AVEC SUCCÈS!")
        print("="*70)
        print("\nFichiers générés:")
        print("  📊 Visualisations: dossier 'visualisations/'")
        print("  📝 Rapport: RAPPORT_FINAL.md")
        print("  💡 Recommandations: recommandations.txt")
        print("\nOuvrez 'visualisations/carte_arrets_bordeaux.html' dans votre navigateur")
        print("pour explorer la carte interactive!\n")


if __name__ == "__main__":
    # Exécution de l'analyse
    analyse = AnalyseMobiliteBordeaux(data_path='Data/')
    analyse.executer_analyse_complete()
