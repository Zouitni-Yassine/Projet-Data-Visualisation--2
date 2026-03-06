"""
Module d'analyse exploratoire des données de mobilité
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging

from .config import ROUTE_TYPES, ANALYSIS_CONFIG

logger = logging.getLogger(__name__)


class MobilityAnalyzer:
    """Analyse les patterns de mobilité urbaine"""

    def __init__(self, data: pd.DataFrame):
        """
        Initialise l'analyseur

        Args:
            data: DataFrame enrichi des données de mobilité
        """
        self.data = data
        self.results = {}

    def analyze_all(self) -> Dict:
        """
        Exécute toutes les analyses

        Returns:
            Dictionnaire contenant tous les résultats d'analyse
        """
        logger.info("Début de l'analyse exploratoire...")

        self.results['temporal'] = self.analyze_temporal_patterns()
        self.results['routes'] = self.analyze_routes()
        self.results['stops'] = self.analyze_stops()
        self.results['geographic'] = self.analyze_geographic_distribution()
        self.results['route_types'] = self.analyze_route_types()

        logger.info("✓ Analyse exploratoire terminée")
        self._print_insights()

        return self.results

    def analyze_temporal_patterns(self) -> Dict:
        """
        Analyse les patterns temporels de fréquentation

        Returns:
            Dictionnaire avec les statistiques temporelles
        """
        logger.info("  → Analyse temporelle...")

        freq_hour = self.data.groupby('hour').size()

        peak_hour = freq_hour.idxmax()
        peak_value = freq_hour.max()
        off_peak_hour = freq_hour.idxmin()
        off_peak_value = freq_hour.min()

        # Identifier les périodes
        morning_rush = freq_hour[(freq_hour.index >= 7) & (freq_hour.index <= 9)].mean()
        evening_rush = freq_hour[(freq_hour.index >= 17) & (freq_hour.index <= 19)].mean()
        night_time = freq_hour[(freq_hour.index >= 22) | (freq_hour.index <= 5)].mean()

        results = {
            'hourly_frequency': freq_hour,
            'peak_hour': peak_hour,
            'peak_value': peak_value,
            'off_peak_hour': off_peak_hour,
            'off_peak_value': off_peak_value,
            'peak_to_offpeak_ratio': peak_value / off_peak_value if off_peak_value > 0 else 0,
            'morning_rush_avg': morning_rush,
            'evening_rush_avg': evening_rush,
            'night_time_avg': night_time
        }

        return results

    def analyze_routes(self) -> Dict:
        """
        Analyse les lignes de transport

        Returns:
            Statistiques sur les lignes
        """
        logger.info("  → Analyse des lignes...")

        if 'route_short_name' not in self.data.columns:
            logger.warning("  ⚠ Colonne 'route_short_name' non trouvée")
            return {}

        freq_routes = self.data.groupby('route_short_name').size().sort_values(ascending=False)

        top_n = ANALYSIS_CONFIG['top_n_routes']
        top_routes = freq_routes.head(top_n)
        bottom_routes = freq_routes.tail(top_n)

        # Statistiques
        mean_freq = freq_routes.mean()
        median_freq = freq_routes.median()
        std_freq = freq_routes.std()
        cv = std_freq / mean_freq if mean_freq > 0 else 0

        results = {
            'route_frequency': freq_routes,
            'top_routes': top_routes,
            'bottom_routes': bottom_routes,
            'total_routes': len(freq_routes),
            'mean_frequency': mean_freq,
            'median_frequency': median_freq,
            'std_frequency': std_freq,
            'coefficient_of_variation': cv
        }

        return results

    def analyze_stops(self) -> Dict:
        """
        Analyse les arrêts

        Returns:
            Statistiques sur les arrêts
        """
        logger.info("  → Analyse des arrêts...")

        freq_stops = self.data.groupby(['stop_id', 'stop_name', 'stop_lat', 'stop_lon']).size()
        freq_stops = freq_stops.sort_values(ascending=False)

        top_n = ANALYSIS_CONFIG['top_n_stops']
        top_stops = freq_stops.head(top_n)

        # Identifier les arrêts sous-utilisés (1er quartile)
        q1 = freq_stops.quantile(0.25)
        underutilized_stops = freq_stops[freq_stops <= q1]

        results = {
            'stop_frequency': freq_stops,
            'top_stops': top_stops,
            'total_stops': len(freq_stops),
            'underutilized_stops': underutilized_stops,
            'mean_frequency': freq_stops.mean(),
            'median_frequency': freq_stops.median()
        }

        return results

    def analyze_geographic_distribution(self) -> Dict:
        """
        Analyse la distribution géographique

        Returns:
            Statistiques géographiques
        """
        logger.info("  → Analyse géographique...")

        # Calculer la densité par zone géographique
        # On divise la zone en grille
        lat_bins = np.linspace(
            self.data['stop_lat'].min(),
            self.data['stop_lat'].max(),
            20
        )
        lon_bins = np.linspace(
            self.data['stop_lon'].min(),
            self.data['stop_lon'].max(),
            20
        )

        self.data['lat_bin'] = pd.cut(self.data['stop_lat'], bins=lat_bins)
        self.data['lon_bin'] = pd.cut(self.data['stop_lon'], bins=lon_bins)

        density_grid = self.data.groupby(['lat_bin', 'lon_bin']).size()

        # Identifier les zones à forte densité
        high_density_threshold = density_grid.quantile(0.9)
        high_density_zones = density_grid[density_grid >= high_density_threshold]

        results = {
            'density_grid': density_grid,
            'high_density_zones': high_density_zones,
            'center_lat': self.data['stop_lat'].mean(),
            'center_lon': self.data['stop_lon'].mean(),
            'bounds': {
                'min_lat': self.data['stop_lat'].min(),
                'max_lat': self.data['stop_lat'].max(),
                'min_lon': self.data['stop_lon'].min(),
                'max_lon': self.data['stop_lon'].max()
            }
        }

        return results

    def analyze_route_types(self) -> Dict:
        """
        Analyse les types de transport

        Returns:
            Statistiques par type de transport
        """
        logger.info("  → Analyse des types de transport...")

        if 'route_type' not in self.data.columns:
            logger.warning("  ⚠ Colonne 'route_type' non trouvée")
            return {}

        freq_types = self.data.groupby('route_type').size()

        # Mapper les types
        freq_types_named = {}
        for route_type, count in freq_types.items():
            type_name = ROUTE_TYPES.get(route_type, f'Type {route_type}')
            freq_types_named[type_name] = count

        total = sum(freq_types_named.values())
        percentages = {k: v/total*100 for k, v in freq_types_named.items()}

        results = {
            'type_frequency': freq_types,
            'type_frequency_named': freq_types_named,
            'type_percentages': percentages,
            'dominant_type': max(freq_types_named, key=freq_types_named.get)
        }

        return results

    def _print_insights(self):
        """Affiche les insights clés de l'analyse"""
        logger.info("\n" + "="*70)
        logger.info("INSIGHTS CLÉS")
        logger.info("="*70)

        # Temporal
        if 'temporal' in self.results:
            t = self.results['temporal']
            logger.info(f"\n📊 Analyse temporelle:")
            logger.info(f"  - Heure de pointe: {t['peak_hour']}h ({t['peak_value']:,} passages)")
            logger.info(f"  - Heure creuse: {t['off_peak_hour']}h ({t['off_peak_value']:,} passages)")
            logger.info(f"  - Ratio pointe/creuse: {t['peak_to_offpeak_ratio']:.1f}x")

        # Routes
        if 'routes' in self.results and self.results['routes']:
            r = self.results['routes']
            logger.info(f"\n🚌 Lignes:")
            logger.info(f"  - Total: {r['total_routes']} lignes")
            logger.info(f"  - CV: {r['coefficient_of_variation']:.2f} (dispersion {'forte' if r['coefficient_of_variation'] > 0.5 else 'faible'})")
            logger.info(f"  - Top 3: {', '.join(map(str, r['top_routes'].head(3).index))}")

        # Stops
        if 'stops' in self.results:
            s = self.results['stops']
            logger.info(f"\n🚏 Arrêts:")
            logger.info(f"  - Total: {s['total_stops']} arrêts uniques")
            logger.info(f"  - Arrêt le plus fréquenté: {s['top_stops'].index[0][1]} ({s['top_stops'].iloc[0]:,} passages)")
            logger.info(f"  - Arrêts sous-utilisés: {len(s['underutilized_stops'])}")

        # Route types
        if 'route_types' in self.results and self.results['route_types']:
            rt = self.results['route_types']
            logger.info(f"\n🚊 Types de transport:")
            for type_name, pct in rt['type_percentages'].items():
                logger.info(f"  - {type_name}: {pct:.1f}%")

        logger.info("\n" + "="*70 + "\n")

    def generate_recommendations(self) -> List[Dict]:
        """
        Génère des recommandations basées sur l'analyse

        Returns:
            Liste de recommandations
        """
        logger.info("Génération des recommandations...")

        recommendations = []

        # Recommandation 1: Heures de pointe
        if 'temporal' in self.results:
            t = self.results['temporal']
            recommendations.append({
                'category': 'Optimisation temporelle',
                'priority': 'Haute',
                'observation': f"L'heure de pointe ({t['peak_hour']}h) connaît {t['peak_to_offpeak_ratio']:.1f}x plus de passages que l'heure creuse",
                'recommendation': f"Renforcer la fréquence des transports entre {t['peak_hour']-1}h et {t['peak_hour']+1}h",
                'expected_impact': 'Réduction de la surcharge et amélioration du confort des usagers'
            })

        # Recommandation 2: Lignes surchargées
        if 'routes' in self.results and self.results['routes']:
            r = self.results['routes']
            if r['coefficient_of_variation'] > 0.5:
                top_3 = ', '.join(map(str, r['top_routes'].head(3).index))
                recommendations.append({
                    'category': 'Équilibrage du réseau',
                    'priority': 'Haute',
                    'observation': f"Forte dispersion de la fréquentation (CV={r['coefficient_of_variation']:.2f}). Les lignes {top_3} concentrent beaucoup de trafic",
                    'recommendation': "Créer des lignes express parallèles ou augmenter la flotte sur ces lignes",
                    'expected_impact': 'Meilleure répartition de la charge et temps de trajet réduit'
                })

        # Recommandation 3: Infrastructure
        if 'stops' in self.results:
            s = self.results['stops']
            top_stop_name = s['top_stops'].index[0][1]
            top_stop_freq = s['top_stops'].iloc[0]

            recommendations.append({
                'category': 'Infrastructure',
                'priority': 'Moyenne',
                'observation': f"L'arrêt '{top_stop_name}' est le plus fréquenté ({top_stop_freq:,} passages)",
                'recommendation': "Améliorer l'infrastructure: abris supplémentaires, affichage temps réel, bancs, accessibilité",
                'expected_impact': 'Meilleure expérience usager et fluidité accrue'
            })

        # Recommandation 4: Arrêts sous-utilisés
        if 'stops' in self.results:
            s = self.results['stops']
            underutilized_pct = len(s['underutilized_stops']) / s['total_stops'] * 100

            recommendations.append({
                'category': 'Optimisation du réseau',
                'priority': 'Basse',
                'observation': f"{len(s['underutilized_stops'])} arrêts ({underutilized_pct:.1f}%) sont sous-utilisés",
                'recommendation': "Évaluer la pertinence de ces arrêts et considérer leur suppression ou fusion",
                'expected_impact': 'Réduction des coûts opérationnels et temps de trajet optimisé'
            })

        logger.info(f"✓ {len(recommendations)} recommandations générées")

        return recommendations
