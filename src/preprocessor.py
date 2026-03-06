"""
Module de prétraitement des données GTFS
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class GTFSPreprocessor:
    """Prétraite et enrichit les données GTFS pour l'analyse"""

    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialise le préprocesseur

        Args:
            data: Dictionnaire des DataFrames GTFS
        """
        self.data = data
        self.stop_times_enriched = None

    def preprocess_all(self) -> pd.DataFrame:
        """
        Exécute le prétraitement complet

        Returns:
            DataFrame enrichi avec toutes les informations nécessaires
        """
        logger.info("Début du prétraitement des données...")

        # 1. Conversion des horaires
        self._convert_times()

        # 2. Extraction de l'heure
        self._extract_hour()

        # 3. Fusion des tables
        self._merge_tables()

        # 4. Nettoyage
        self._clean_data()

        logger.info(f"✓ Prétraitement terminé: {len(self.stop_times_enriched):,} lignes")

        return self.stop_times_enriched

    def _convert_times(self):
        """Convertit les horaires en format timedelta"""
        logger.info("  → Conversion des horaires...")

        stop_times = self.data['stop_times'].copy()

        try:
            stop_times['arrival_time'] = pd.to_timedelta(stop_times['arrival_time'])
            stop_times['departure_time'] = pd.to_timedelta(stop_times['departure_time'])
        except Exception as e:
            logger.warning(f"  ⚠ Erreur lors de la conversion des horaires: {e}")
            # Fallback: essayer de convertir manuellement
            stop_times['arrival_time'] = stop_times['arrival_time'].apply(self._parse_time)
            stop_times['departure_time'] = stop_times['departure_time'].apply(self._parse_time)

        self.data['stop_times'] = stop_times

    @staticmethod
    def _parse_time(time_str: str) -> pd.Timedelta:
        """
        Parse une chaîne de temps GTFS (peut avoir des heures > 24)

        Args:
            time_str: Chaîne de temps (ex: "25:30:00")

        Returns:
            Timedelta correspondant
        """
        try:
            if pd.isna(time_str):
                return pd.NaT

            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])

            return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except Exception:
            return pd.NaT

    def _extract_hour(self):
        """Extrait l'heure (0-23) à partir du temps"""
        logger.info("  → Extraction de l'heure...")

        stop_times = self.data['stop_times']

        # Extraire les composantes
        stop_times['hour'] = stop_times['arrival_time'].dt.components['hours']

        # Gérer les heures > 23 (ex: 25:00 = 1h du lendemain)
        stop_times['hour'] = stop_times['hour'] % 24

        # Extraire aussi le jour
        stop_times['day_offset'] = stop_times['arrival_time'].dt.components['hours'] // 24

        self.data['stop_times'] = stop_times

    def _merge_tables(self):
        """Fusionne les tables pour créer un DataFrame enrichi"""
        logger.info("  → Fusion des tables...")

        df = self.data['stop_times'].copy()

        # Convertir stop_id en string pour assurer la compatibilité
        df['stop_id'] = df['stop_id'].astype(str)

        # Fusionner avec stops
        if 'stops' in self.data:
            stops_df = self.data['stops'].copy()
            stops_df['stop_id'] = stops_df['stop_id'].astype(str)

            stops_cols = ['stop_code', 'stop_name', 'stop_lat', 'stop_lon', 'zone_id']
            available_cols = ['stop_id'] + [col for col in stops_cols if col in stops_df.columns]
            df = df.merge(
                stops_df[available_cols],
                on='stop_id',
                how='left'
            )

        # Fusionner avec trips
        if 'trips' in self.data:
            df['trip_id'] = df['trip_id'].astype(str)
            trips_df = self.data['trips'].copy()
            trips_df['trip_id'] = trips_df['trip_id'].astype(str)
            if 'route_id' in trips_df.columns:
                trips_df['route_id'] = trips_df['route_id'].astype(str)

            trips_cols = ['route_id', 'service_id', 'trip_headsign', 'direction_id']
            available_cols = ['trip_id'] + [col for col in trips_cols if col in trips_df.columns]
            df = df.merge(
                trips_df[available_cols],
                on='trip_id',
                how='left'
            )

        # Fusionner avec routes
        if 'routes' in self.data:
            if 'route_id' in df.columns:
                df['route_id'] = df['route_id'].astype(str)
            routes_df = self.data['routes'].copy()
            routes_df['route_id'] = routes_df['route_id'].astype(str)

            routes_cols = ['route_short_name', 'route_long_name', 'route_type', 'route_color']
            available_cols = ['route_id'] + [col for col in routes_cols if col in routes_df.columns]
            df = df.merge(
                routes_df[available_cols],
                on='route_id',
                how='left'
            )

        self.stop_times_enriched = df

    def _clean_data(self):
        """Nettoie les données (supprime les valeurs manquantes critiques)"""
        logger.info("  → Nettoyage des données...")

        avant = len(self.stop_times_enriched)

        # Supprimer les lignes avec coordonnées manquantes
        self.stop_times_enriched = self.stop_times_enriched.dropna(
            subset=['stop_lat', 'stop_lon', 'hour']
        )

        # Supprimer les coordonnées aberrantes (hors de France métropolitaine approximativement)
        self.stop_times_enriched = self.stop_times_enriched[
            (self.stop_times_enriched['stop_lat'].between(41, 51)) &
            (self.stop_times_enriched['stop_lon'].between(-5, 10))
        ]

        apres = len(self.stop_times_enriched)
        lignes_supprimees = avant - apres

        logger.info(f"  → {lignes_supprimees:,} lignes supprimées ({lignes_supprimees/avant*100:.2f}%)")
        logger.info(f"  → {apres:,} lignes conservées")

    def get_enriched_data(self) -> pd.DataFrame:
        """
        Récupère les données enrichies

        Returns:
            DataFrame enrichi

        Raises:
            ValueError: Si le prétraitement n'a pas été exécuté
        """
        if self.stop_times_enriched is None:
            raise ValueError("Le prétraitement n'a pas été exécuté. Appelez preprocess_all() d'abord.")

        return self.stop_times_enriched

    def get_summary_stats(self) -> Dict:
        """
        Calcule des statistiques sommaires

        Returns:
            Dictionnaire de statistiques
        """
        if self.stop_times_enriched is None:
            raise ValueError("Le prétraitement n'a pas été exécuté.")

        df = self.stop_times_enriched

        stats = {
            'total_passages': len(df),
            'unique_stops': df['stop_id'].nunique(),
            'unique_routes': df['route_id'].nunique() if 'route_id' in df else 0,
            'unique_trips': df['trip_id'].nunique(),
            'date_range': {
                'min_hour': df['hour'].min(),
                'max_hour': df['hour'].max()
            },
            'geographic_bounds': {
                'min_lat': df['stop_lat'].min(),
                'max_lat': df['stop_lat'].max(),
                'min_lon': df['stop_lon'].min(),
                'max_lon': df['stop_lon'].max()
            }
        }

        return stats
