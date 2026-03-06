"""
Module de chargement des données GTFS
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import logging

from .config import DATA_PATH, GTFS_FILES

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GTFSDataLoader:
    """Charge et gère les données GTFS"""

    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialise le chargeur de données

        Args:
            data_path: Chemin vers le dossier des données GTFS
        """
        self.data_path = data_path or DATA_PATH
        self.data: Dict[str, pd.DataFrame] = {}

    def load_all(self, include_shapes: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Charge tous les fichiers GTFS

        Args:
            include_shapes: Inclure le fichier shapes (volumineux)

        Returns:
            Dictionnaire contenant tous les DataFrames chargés
        """
        logger.info("Début du chargement des données GTFS...")

        files_to_load = {k: v for k, v in GTFS_FILES.items()}
        if not include_shapes:
            files_to_load.pop('shapes', None)

        for key, filename in files_to_load.items():
            self.data[key] = self._load_file(filename, key)

        logger.info(f"✓ {len(self.data)} fichiers chargés avec succès")
        self._print_summary()

        return self.data

    def _load_file(self, filename: str, file_type: str) -> pd.DataFrame:
        """
        Charge un fichier GTFS spécifique

        Args:
            filename: Nom du fichier
            file_type: Type de fichier (pour logging)

        Returns:
            DataFrame contenant les données
        """
        filepath = self.data_path / filename

        try:
            if file_type == 'stop_times':
                logger.info(f"  Chargement de {filename} (peut prendre 30-60 secondes)...")

            df = pd.read_csv(filepath)
            logger.info(f"  ✓ {filename}: {len(df):,} lignes")
            return df

        except FileNotFoundError:
            logger.warning(f"  ⚠ Fichier non trouvé: {filename}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"  ✗ Erreur lors du chargement de {filename}: {e}")
            raise

    def _print_summary(self):
        """Affiche un résumé des données chargées"""
        logger.info("\n" + "="*70)
        logger.info("RÉSUMÉ DES DONNÉES CHARGÉES")
        logger.info("="*70)

        if 'agency' in self.data:
            logger.info(f"Agence: {self.data['agency'].iloc[0]['agency_name']}")

        if 'stops' in self.data:
            logger.info(f"Arrêts: {len(self.data['stops']):,}")

        if 'routes' in self.data:
            logger.info(f"Lignes: {len(self.data['routes']):,}")

        if 'trips' in self.data:
            logger.info(f"Trajets: {len(self.data['trips']):,}")

        if 'stop_times' in self.data:
            logger.info(f"Horaires: {len(self.data['stop_times']):,}")

        logger.info("="*70 + "\n")

    def get_dataframe(self, name: str) -> pd.DataFrame:
        """
        Récupère un DataFrame spécifique

        Args:
            name: Nom du DataFrame (agency, stops, routes, etc.)

        Returns:
            DataFrame demandé

        Raises:
            KeyError: Si le DataFrame n'est pas chargé
        """
        if name not in self.data:
            raise KeyError(f"DataFrame '{name}' non chargé. Fichiers disponibles: {list(self.data.keys())}")

        return self.data[name]

    def validate_data(self) -> bool:
        """
        Valide que les données essentielles sont présentes

        Returns:
            True si les données sont valides
        """
        required_files = ['stops', 'routes', 'trips', 'stop_times']

        for file in required_files:
            if file not in self.data or self.data[file].empty:
                logger.error(f"✗ Données manquantes ou vides: {file}")
                return False

        logger.info("✓ Validation des données réussie")
        return True
