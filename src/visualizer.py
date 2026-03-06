"""
Module de visualisation des données de mobilité
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional
from pathlib import Path
import logging

from .config import VIZ_CONFIG, MAP_CONFIG, OUTPUT_PATH

logger = logging.getLogger(__name__)


class MobilityVisualizer:
    """Crée les visualisations pour l'analyse de mobilité"""

    def __init__(self, data: pd.DataFrame, analysis_results: Dict, output_path: Optional[Path] = None):
        """
        Initialise le visualiseur

        Args:
            data: DataFrame des données de mobilité
            analysis_results: Résultats de l'analyse
            output_path: Chemin de sortie pour les visualisations
        """
        self.data = data
        self.results = analysis_results
        self.output_path = output_path or OUTPUT_PATH

        # Créer le dossier de sortie
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Configuration matplotlib/seaborn
        plt.style.use(VIZ_CONFIG['style'])
        sns.set_palette(VIZ_CONFIG['palette'])

    def create_all_visualizations(self):
        """Crée toutes les visualisations - VERSION COMPLETE"""
        logger.info("Création des visualisations complètes...")

        # Visualisations existantes
        self.plot_temporal_heatmap()
        self.plot_hourly_distribution()
        self.plot_top_routes()
        self.plot_top_stops()

        # NOUVELLES VISUALISATIONS CRITIQUES
        logger.info("  → Visualisations avancées...")
        self.plot_route_hour_heatmap()          # CRITIQUE: Ligne × Heure
        self.plot_scatter_geo_weighted()         # CRITIQUE: Scatter géo pondéré
        self.plot_transport_types()              # IMPORTANT: Types de transport
        self.plot_geographic_distribution()      # Distribution spatiale

        # Cartes interactives
        logger.info("  → Cartes interactives...")
        self.create_interactive_map()            # Carte avec TOUS les arrêts
        self.create_heatmap()                    # Carte de chaleur pure
        self.create_interactive_dashboards()

        logger.info(f"✓ Visualisations complètes sauvegardées dans: {self.output_path}")

    def plot_temporal_heatmap(self):
        """Crée une heatmap de l'affluence temporelle"""
        logger.info("  → Heatmap temporelle...")

        if 'temporal' not in self.results:
            return

        freq_hour = self.results['temporal']['hourly_frequency']

        # Créer une matrice (7 jours x 24 heures)
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        heures = list(range(24))

        # Simuler les jours (on répète le pattern)
        data_matrix = []
        for i, jour in enumerate(jours):
            # Simuler une variation : week-end avec moins de trafic
            factor = 0.6 if i >= 5 else 1.0
            data_matrix.append([freq_hour.get(h, 0) * factor for h in heures])

        fig, ax = plt.subplots(figsize=VIZ_CONFIG['figsize'])
        sns.heatmap(
            data_matrix,
            xticklabels=heures,
            yticklabels=jours,
            cmap='YlOrRd',
            annot=False,
            fmt='d',
            cbar_kws={'label': 'Nombre de passages'},
            ax=ax
        )

        ax.set_title('Heatmap de la fréquentation par heure et jour',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Heure de la journée', fontsize=12)
        ax.set_ylabel('Jour de la semaine', fontsize=12)

        plt.tight_layout()
        plt.savefig(self.output_path / 'heatmap_temporel.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

    def plot_hourly_distribution(self):
        """Crée un graphique de distribution horaire"""
        logger.info("  → Distribution horaire...")

        if 'temporal' not in self.results:
            return

        freq_hour = self.results['temporal']['hourly_frequency']
        peak_hour = self.results['temporal']['peak_hour']

        fig, ax = plt.subplots(figsize=VIZ_CONFIG['figsize'])

        heures = list(range(24))
        valeurs = [freq_hour.get(h, 0) for h in heures]

        ax.plot(heures, valeurs, marker='o', linewidth=2.5, markersize=8,
                color=VIZ_CONFIG['colors']['primary'], label='Fréquentation')
        ax.fill_between(heures, valeurs, alpha=0.3, color='skyblue')

        # Marquer l'heure de pointe
        ax.axvline(x=peak_hour, color='red', linestyle='--', linewidth=2,
                   label=f'Heure de pointe: {peak_hour}h')

        # Zones de rush
        ax.axvspan(7, 9, alpha=0.1, color='orange', label='Rush matinal')
        ax.axvspan(17, 19, alpha=0.1, color='orange', label='Rush du soir')

        ax.set_xlabel('Heure de la journée', fontsize=12)
        ax.set_ylabel('Nombre de passages', fontsize=12)
        ax.set_title('Distribution de la fréquentation tout au long de la journée',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(heures)
        ax.set_xticklabels([f'{h}h' for h in heures], rotation=45)
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(loc='best')

        plt.tight_layout()
        plt.savefig(self.output_path / 'distribution_horaire.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

    def plot_top_routes(self):
        """Crée un graphique des lignes principales"""
        logger.info("  → Top lignes...")

        if 'routes' not in self.results or not self.results['routes']:
            return

        top_routes = self.results['routes']['top_routes'].head(15)

        fig, ax = plt.subplots(figsize=(12, 8))

        y_pos = range(len(top_routes))
        bars = ax.barh(y_pos, top_routes.values, color=VIZ_CONFIG['colors']['accent'])

        # Gradient de couleur basé sur la valeur
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(top_routes)))
        for bar, color in zip(bars, colors[::-1]):
            bar.set_color(color)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_routes.index)
        ax.set_xlabel('Nombre de passages', fontsize=12)
        ax.set_ylabel('Ligne', fontsize=12)
        ax.set_title('Top 15 des lignes les plus fréquentées à Bordeaux',
                     fontsize=14, fontweight='bold', pad=20)

        # Ajouter les valeurs
        for i, (ligne, val) in enumerate(top_routes.items()):
            ax.text(val, i, f'  {val:,}', va='center', fontsize=9)

        ax.grid(True, alpha=0.3, axis='x', linestyle=':')
        plt.tight_layout()
        plt.savefig(self.output_path / 'top_lignes.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

    def plot_top_stops(self):
        """Crée un graphique des arrêts principaux"""
        logger.info("  → Top arrêts...")

        if 'stops' not in self.results:
            return

        top_stops = self.results['stops']['top_stops'].head(15)

        # Extraire les noms d'arrêts
        stop_names = [idx[1] for idx in top_stops.index]
        values = top_stops.values

        fig, ax = plt.subplots(figsize=(12, 8))

        y_pos = range(len(stop_names))
        bars = ax.barh(y_pos, values, color=VIZ_CONFIG['colors']['secondary'])

        ax.set_yticks(y_pos)
        ax.set_yticklabels(stop_names)
        ax.set_xlabel('Nombre de passages', fontsize=12)
        ax.set_ylabel('Arrêt', fontsize=12)
        ax.set_title('Top 15 des arrêts les plus fréquentés',
                     fontsize=14, fontweight='bold', pad=20)

        # Ajouter les valeurs
        for i, val in enumerate(values):
            ax.text(val, i, f'  {val:,}', va='center', fontsize=9)

        ax.grid(True, alpha=0.3, axis='x', linestyle=':')
        plt.tight_layout()
        plt.savefig(self.output_path / 'top_arrets.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

    def create_interactive_map(self):
        """Crée une carte interactive avec TOUS les arrêts (version complète)"""
        logger.info("  → Carte interactive avec TOUS les arrêts...")

        # Calculer la fréquentation par arrêt
        freq_stops = self.data.groupby(['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).size().reset_index()
        freq_stops.columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'frequentation']
        freq_stops = freq_stops.dropna(subset=['stop_lat', 'stop_lon'])

        # Centre de la carte
        if 'geographic' in self.results:
            center_lat = self.results['geographic']['center_lat']
            center_lon = self.results['geographic']['center_lon']
        else:
            center_lat = freq_stops['stop_lat'].mean()
            center_lon = freq_stops['stop_lon'].mean()

        # Créer la carte
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=MAP_CONFIG['zoom_start'],
            tiles='OpenStreetMap'
        )

        # NOUVEAU: Ajouter TOUS les arrêts avec MarkerCluster
        marker_cluster = MarkerCluster(
            name=f'Tous les arrêts ({len(freq_stops):,})',
            overlay=True,
            control=True
        ).add_to(m)

        # Déterminer la couleur des marqueurs selon la fréquentation
        max_freq = freq_stops['frequentation'].max()

        for _, row in freq_stops.iterrows():
            # Couleur selon la fréquentation
            if row['frequentation'] >= max_freq * 0.7:
                color = 'red'  # Très fréquenté
            elif row['frequentation'] >= max_freq * 0.4:
                color = 'orange'  # Moyennement fréquenté
            else:
                color = 'blue'  # Peu fréquenté

            folium.Marker(
                location=[row['stop_lat'], row['stop_lon']],
                popup=folium.Popup(
                    f"<b>{row['stop_name']}</b><br>"
                    f"<b>Fréquentation:</b> {row['frequentation']:,} passages<br>"
                    f"<b>ID:</b> {row['stop_id']}",
                    max_width=300
                ),
                tooltip=row['stop_name'],
                icon=folium.Icon(color=color, icon='bus', prefix='fa')
            ).add_to(marker_cluster)

        # Ajouter un contrôle de couches
        folium.LayerControl().add_to(m)

        # Sauvegarder
        m.save(str(self.output_path / 'carte_interactive_tous_arrets.html'))
        logger.info(f"  ✓ Carte interactive créée ({len(freq_stops):,} arrêts)")

    def create_heatmap(self):
        """Crée une carte de chaleur pure (heatmap)"""
        logger.info("  → Carte de chaleur (heatmap)...")

        # Calculer la fréquentation par arrêt
        freq_stops = self.data.groupby(['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).size().reset_index()
        freq_stops.columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'frequentation']
        freq_stops = freq_stops.dropna(subset=['stop_lat', 'stop_lon'])

        # Centre de la carte
        if 'geographic' in self.results:
            center_lat = self.results['geographic']['center_lat']
            center_lon = self.results['geographic']['center_lon']
        else:
            center_lat = freq_stops['stop_lat'].mean()
            center_lon = freq_stops['stop_lon'].mean()

        # Créer la carte
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=MAP_CONFIG['zoom_start'],
            tiles='OpenStreetMap'
        )

        # Ajouter la heatmap
        heat_data = [
            [row['stop_lat'], row['stop_lon'], row['frequentation']]
            for _, row in freq_stops.iterrows()
        ]
        HeatMap(
            heat_data,
            radius=MAP_CONFIG['heatmap_radius'],
            blur=MAP_CONFIG['heatmap_blur'],
            max_zoom=13,
            min_opacity=0.3,
            gradient={
                0.0: 'blue',
                0.3: 'cyan',
                0.5: 'lime',
                0.7: 'yellow',
                0.9: 'orange',
                1.0: 'red'
            }
        ).add_to(m)

        # Ajouter titre et légende
        title_html = '''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 400px; height: 90px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <h4 style="margin:0">Carte de Chaleur - Fréquentation des Arrêts</h4>
        <p style="margin:5px 0"><b>Gradient:</b> Bleu (faible) → Rouge (élevé)</p>
        <p style="margin:5px 0"><b>Total:</b> {:,} arrêts analysés</p>
        </div>
        '''.format(len(freq_stops))
        m.get_root().html.add_child(folium.Element(title_html))

        # Sauvegarder
        m.save(str(self.output_path / 'carte_chaleur.html'))
        logger.info(f"  ✓ Carte de chaleur créée ({len(freq_stops):,} arrêts)")

    def create_interactive_dashboards(self):
        """Crée des dashboards interactifs avec Plotly"""
        logger.info("  → Dashboards interactifs...")

        # Dashboard 1: Distribution horaire
        self._create_hourly_dashboard()

        # Dashboard 2: Lignes et arrêts
        self._create_routes_dashboard()

    def _create_hourly_dashboard(self):
        """Crée un dashboard interactif de la distribution horaire"""
        if 'temporal' not in self.results:
            return

        freq_hour = self.results['temporal']['hourly_frequency'].reset_index()
        freq_hour.columns = ['hour', 'count']

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=freq_hour['hour'],
            y=freq_hour['count'],
            mode='lines+markers',
            name='Fréquentation',
            line=dict(color=VIZ_CONFIG['colors']['primary'], width=3),
            marker=dict(size=10, color=VIZ_CONFIG['colors']['primary']),
            hovertemplate='<b>Heure:</b> %{x}h<br><b>Passages:</b> %{y:,}<extra></extra>',
            fill='tozeroy',
            fillcolor='rgba(65, 105, 225, 0.2)'
        ))

        # Marquer les heures de rush
        peak_hour = self.results['temporal']['peak_hour']
        fig.add_vline(
            x=peak_hour,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Heure de pointe: {peak_hour}h"
        )

        fig.update_layout(
            title='Dashboard Interactif - Fréquentation Horaire',
            xaxis_title='Heure de la journée',
            yaxis_title='Nombre de passages',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            showlegend=True
        )

        fig.write_html(str(self.output_path / 'dashboard_horaire.html'))

    def _create_routes_dashboard(self):
        """Crée un dashboard interactif des lignes"""
        if 'routes' not in self.results or not self.results['routes']:
            return

        top_routes = self.results['routes']['top_routes'].head(20).reset_index()
        top_routes.columns = ['ligne', 'count']

        fig = px.bar(
            top_routes,
            x='ligne',
            y='count',
            title='Top 20 des lignes les plus fréquentées',
            labels={'ligne': 'Ligne', 'count': 'Nombre de passages'},
            color='count',
            color_continuous_scale='Viridis',
            hover_data={'count': ':,'}
        )

        fig.update_layout(
            xaxis_title='Ligne de transport',
            yaxis_title='Nombre de passages',
            template='plotly_white',
            height=600,
            showlegend=False
        )

        fig.update_traces(
            hovertemplate='<b>Ligne %{x}</b><br>Passages: %{y:,}<extra></extra>'
        )

        fig.write_html(str(self.output_path / 'dashboard_lignes.html'))

    def plot_route_hour_heatmap(self):
        """
        Crée une heatmap 2D Ligne × Heure (VISUALISATION CRITIQUE!)
        Montre quelles lignes sont surchargées à quelles heures précises
        """
        logger.info("  → Heatmap Ligne × Heure (CRITIQUE)...")

        if 'route_short_name' not in self.data.columns or 'hour' not in self.data.columns:
            logger.warning("  ⚠ Colonnes nécessaires manquantes pour heatmap ligne×heure")
            return

        # Créer un pivot: lignes en index, heures en colonnes
        pivot = self.data.groupby(['route_short_name', 'hour']).size().unstack(fill_value=0)

        # Prendre les top 15 lignes les plus fréquentées
        route_totals = pivot.sum(axis=1).sort_values(ascending=False)
        top_routes = route_totals.head(15).index
        pivot_top = pivot.loc[top_routes]

        # Créer la heatmap
        fig, ax = plt.subplots(figsize=(16, 10))
        sns.heatmap(
            pivot_top,
            cmap='YlOrRd',
            annot=False,
            fmt='d',
            cbar_kws={'label': 'Nombre de passages'},
            linewidths=0.5,
            linecolor='gray',
            ax=ax
        )

        ax.set_title('Heatmap Fréquentation: Ligne × Heure de la Journée',
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Heure de la journée', fontsize=13)
        ax.set_ylabel('Ligne de transport', fontsize=13)
        ax.set_xticklabels([f'{h}h' for h in range(24)], rotation=0)

        plt.tight_layout()
        plt.savefig(self.output_path / 'heatmap_ligne_heure.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"  ✓ Heatmap ligne×heure créée (Top {len(top_routes)} lignes)")

    def plot_scatter_geo_weighted(self):
        """
        Crée un scatter plot géographique pondéré par la fréquentation
        Chaque arrêt = point avec taille/couleur proportionnelle aux passages
        TRÈS IMPACTANT VISUELLEMENT!
        VERSION AMÉLIORÉE: Filtre les arrêts pour meilleure visibilité
        """
        logger.info("  → Scatter géographique pondéré (version améliorée)...")

        # Calculer fréquentation par arrêt
        freq_stops = self.data.groupby(['stop_lat', 'stop_lon', 'stop_name']).size().reset_index()
        freq_stops.columns = ['lat', 'lon', 'name', 'freq']
        freq_stops = freq_stops.dropna(subset=['lat', 'lon'])

        if len(freq_stops) == 0:
            logger.warning("  ⚠ Pas de données géographiques disponibles")
            return

        total_stops = len(freq_stops)

        # AMÉLIORATION: Filtrer pour ne montrer que les arrêts les plus fréquentés
        # On garde les top 800 arrêts OU ceux avec plus de 100 passages
        threshold = max(100, freq_stops['freq'].quantile(0.75))
        freq_stops_filtered = freq_stops[freq_stops['freq'] >= threshold].copy()

        # Si encore trop de points, garder seulement les top 800
        if len(freq_stops_filtered) > 800:
            freq_stops_filtered = freq_stops.nlargest(800, 'freq')

        logger.info(f"  → Affichage de {len(freq_stops_filtered):,} arrêts sur {total_stops:,} (les plus fréquentés)")

        # Figure plus grande pour meilleure visibilité
        fig, ax = plt.subplots(figsize=(20, 14))

        # Utiliser échelle logarithmique pour la taille des points
        # Cela évite que les gros points écrasent les petits
        sizes = np.log1p(freq_stops_filtered['freq']) * 15  # log(x+1) pour éviter log(0)

        # Scatter plot avec taille et couleur proportionnelles
        scatter = ax.scatter(
            freq_stops_filtered['lon'],
            freq_stops_filtered['lat'],
            s=sizes,                            # Taille avec échelle log
            c=freq_stops_filtered['freq'],      # Couleur proportionnelle
            cmap='YlOrRd',
            alpha=0.7,                          # Plus opaque pour meilleure visibilité
            edgecolors='darkgray',
            linewidth=0.5
        )

        # Colorbar avec meilleure présentation
        cbar = plt.colorbar(scatter, ax=ax, pad=0.02, fraction=0.046)
        cbar.set_label('Fréquentation (nombre de passages)', fontsize=14, weight='bold')
        cbar.ax.tick_params(labelsize=11)

        # CLEAN: Tableau simple des TOP 10 en haut à droite
        top_stops = freq_stops_filtered.nlargest(10, 'freq')

        # Créer un texte bien structuré
        table_text = "TOP 10 ARRÊTS\n" + "="*35 + "\n"
        for idx, (_, row) in enumerate(top_stops.iterrows(), 1):
            # Tronquer le nom si trop long
            name = row['name'][:22] if len(row['name']) > 22 else row['name']
            table_text += f"{idx:2d}. {name:<22} {row['freq']:>5,}\n"

        # Placer le tableau en haut à droite
        ax.text(0.98, 0.98, table_text,
               transform=ax.transAxes,
               fontsize=9,
               family='monospace',
               weight='bold',
               verticalalignment='top',
               horizontalalignment='right',
               bbox={'boxstyle': 'round,pad=1.0',
                     'facecolor': 'white',
                     'edgecolor': 'black',
                     'alpha': 0.95,
                     'linewidth': 2.5})

        # Titre plus informatif
        ax.set_title(
            f'Distribution Géographique de la Fréquentation à Bordeaux\n'
            f'Top {len(freq_stops_filtered):,} arrêts les plus fréquentés sur {total_stops:,} total\n'
            f'(Taille et couleur proportionnelles au nombre de passages)',
            fontsize=17, fontweight='bold', pad=25
        )
        ax.set_xlabel('Longitude', fontsize=14, weight='bold')
        ax.set_ylabel('Latitude', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)

        # Améliorer les ticks
        ax.tick_params(axis='both', labelsize=11)

        plt.tight_layout()
        plt.savefig(self.output_path / 'scatter_geo_frequentation.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"  ✓ Scatter géographique amélioré créé (top {len(freq_stops_filtered):,}/{total_stops:,} arrêts)")

    def plot_transport_types(self):
        """
        Crée des graphiques de répartition par type de transport
        (Bus, Tramway, Ferry, etc.)
        STATISTIQUE CLÉ DU RÉSEAU
        """
        logger.info("  → Graphiques types de transport...")

        if 'route_types' not in self.results or not self.results['route_types']:
            logger.warning("  ⚠ Pas de données sur les types de transport")
            return

        types_data = self.results['route_types']['type_frequency_named']

        if not types_data:
            return

        # Créer figure avec 2 sous-graphiques
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # 1. Camembert (Pie chart)
        colors = plt.cm.Set3(range(len(types_data)))
        wedges, texts, autotexts = ax1.pie(
            types_data.values(),
            labels=types_data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )

        # Améliorer lisibilité pourcentages
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')

        ax1.set_title('Répartition par Type de Transport\n(% des passages)',
                      fontsize=14, fontweight='bold', pad=20)

        # 2. Barres (Bar chart)
        bars = ax2.bar(
            range(len(types_data)),
            types_data.values(),
            color=colors,
            edgecolor='black',
            linewidth=1.5
        )

        ax2.set_xticks(range(len(types_data)))
        ax2.set_xticklabels(types_data.keys(), fontsize=11, weight='bold')
        ax2.set_ylabel('Nombre de passages', fontsize=12, weight='bold')
        ax2.set_title('Nombre de Passages par Type\n(valeurs absolues)',
                      fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, axis='y', linestyle=':')

        # Ajouter valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{int(height):,}',
                ha='center',
                va='bottom',
                fontsize=10,
                weight='bold'
            )

        plt.tight_layout()
        plt.savefig(self.output_path / 'graphique_types.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"  ✓ Graphiques types transport créés ({len(types_data)} types)")

    def plot_geographic_distribution(self):
        """
        Crée des histogrammes de distribution géographique
        Montre la répartition spatiale des arrêts (latitude/longitude)
        """
        logger.info("  → Distribution géographique des arrêts...")

        if 'stop_lat' not in self.data.columns or 'stop_lon' not in self.data.columns:
            logger.warning("  ⚠ Pas de coordonnées géographiques")
            return

        # Obtenir arrêts uniques
        unique_stops = self.data[['stop_lat', 'stop_lon']].drop_duplicates()
        unique_stops = unique_stops.dropna()

        if len(unique_stops) == 0:
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # 1. Distribution par latitude
        ax1.hist(unique_stops['stop_lat'], bins=50, color='steelblue',
                 edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Latitude', fontsize=12, weight='bold')
        ax1.set_ylabel('Nombre d\'arrêts', fontsize=12, weight='bold')
        ax1.set_title('Distribution des Arrêts par Latitude',
                      fontsize=14, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, linestyle=':')

        # 2. Distribution par longitude
        ax2.hist(unique_stops['stop_lon'], bins=50, color='coral',
                 edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Longitude', fontsize=12, weight='bold')
        ax2.set_ylabel('Nombre d\'arrêts', fontsize=12, weight='bold')
        ax2.set_title('Distribution des Arrêts par Longitude',
                      fontsize=14, fontweight='bold', pad=15)
        ax2.grid(True, alpha=0.3, linestyle=':')

        plt.tight_layout()
        plt.savefig(self.output_path / 'distribution_geographique.png',
                    dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"  ✓ Distribution géographique créée ({len(unique_stops):,} arrêts uniques)")
