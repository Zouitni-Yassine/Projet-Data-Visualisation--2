"""
Configuration du projet d'analyse de mobilité urbaine
"""

from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "Data"
OUTPUT_PATH = PROJECT_ROOT / "visualisations"
NOTEBOOKS_PATH = PROJECT_ROOT / "notebooks"

# Fichiers GTFS
GTFS_FILES = {
    'agency': 'agency.txt',
    'stops': 'stops.txt',
    'routes': 'routes.txt',
    'trips': 'trips.txt',
    'stop_times': 'stop_times.txt',
    'calendar': 'calendar.txt',
    'calendar_dates': 'calendar_dates.txt',
    'shapes': 'shapes.txt'
}

# Configuration des visualisations
VIZ_CONFIG = {
    'figsize': (14, 6),
    'dpi': 300,
    'style': 'seaborn-v0_8-darkgrid',
    'palette': 'husl',
    'colors': {
        'primary': 'royalblue',
        'secondary': 'coral',
        'accent': 'steelblue'
    }
}

# Configuration de la carte
MAP_CONFIG = {
    'center_lat': 44.8378,  # Centre de Bordeaux
    'center_lon': -0.5792,
    'zoom_start': 12,
    'heatmap_radius': 15,
    'heatmap_blur': 25
}

# Types de transport selon GTFS
ROUTE_TYPES = {
    0: 'Tramway',
    1: 'Métro',
    2: 'Train',
    3: 'Bus',
    4: 'Ferry',
    5: 'Cable tram',
    6: 'Aerial lift',
    7: 'Funicular'
}

# Paramètres d'analyse
ANALYSIS_CONFIG = {
    'top_n_routes': 20,
    'top_n_stops': 50,
    'hours_range': range(24)
}
