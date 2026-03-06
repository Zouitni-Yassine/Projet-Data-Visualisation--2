"""
Point d'entrée principal pour l'analyse de mobilité urbaine à Bordeaux

Ce script orchestre l'ensemble du pipeline d'analyse:
1. Chargement des données GTFS
2. Prétraitement et enrichissement
3. Analyse exploratoire
4. Création des visualisations
5. Génération du rapport et des recommandations
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import GTFSDataLoader
from src.preprocessor import GTFSPreprocessor
from src.analyzer import MobilityAnalyzer
from src.visualizer import MobilityVisualizer
from src.config import OUTPUT_PATH

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('analysis.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def print_header():
    """Affiche l'en-tête du programme"""
    print("\n" + "="*80)
    print("ANALYSE DES DYNAMIQUES DE MOBILITÉ URBAINE À BORDEAUX")
    print("Projet Data Visualisation #2")
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*80 + "\n")


def save_recommendations(recommendations):
    """
    Sauvegarde les recommandations dans un fichier

    Args:
        recommendations: Liste des recommandations
    """
    filepath = Path('recommandations.txt')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RECOMMANDATIONS D'OPTIMISATION DU RÉSEAU TBM BORDEAUX\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        for i, rec in enumerate(recommendations, 1):
            f.write(f"\n{i}. {rec['category']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Priorité: {rec['priority']}\n")
            f.write(f"Observation: {rec['observation']}\n")
            f.write(f"Recommandation: {rec['recommendation']}\n")
            f.write(f"Impact attendu: {rec['expected_impact']}\n")

    logger.info(f"✓ Recommandations sauvegardées: {filepath}")


def generate_markdown_report(data, analysis_results, recommendations):
    """
    Génère un rapport final en Markdown

    Args:
        data: DataFrame des données
        analysis_results: Résultats de l'analyse
        recommendations: Liste des recommandations
    """
    filepath = Path('RAPPORT_FINAL.md')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Analyse des dynamiques de mobilité urbaine à Bordeaux\n\n")
        f.write("## Projet Data Visualisation #2\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%d/%m/%Y')}\n\n")
        f.write("**Source des données:** TBM (Transports Bordeaux Métropole) - Format GTFS\n\n")

        f.write("---\n\n")
        f.write("## 1. Résumé exécutif\n\n")
        f.write("Ce projet analyse les schémas de mobilité urbaine à Bordeaux à partir des données ")
        f.write("de transport public au format GTFS. L'objectif est d'identifier les patterns temporels ")
        f.write("et géographiques de fréquentation, ainsi que de proposer des optimisations.\n\n")

        f.write("---\n\n")
        f.write("## 2. Données analysées\n\n")
        f.write(f"- **Total de passages analysés:** {len(data):,}\n")
        f.write(f"- **Nombre d'arrêts uniques:** {data['stop_id'].nunique():,}\n")
        f.write(f"- **Nombre de lignes:** {data['route_id'].nunique() if 'route_id' in data else 'N/A':,}\n")
        f.write(f"- **Nombre de trajets:** {data['trip_id'].nunique():,}\n\n")

        f.write("---\n\n")
        f.write("## 3. Résultats de l'analyse\n\n")

        # Analyse temporelle
        if 'temporal' in analysis_results:
            t = analysis_results['temporal']
            f.write("### 3.1 Analyse temporelle\n\n")
            f.write(f"- **Heure de pointe:** {t['peak_hour']}h ({t['peak_value']:,} passages)\n")
            f.write(f"- **Heure creuse:** {t['off_peak_hour']}h ({t['off_peak_value']:,} passages)\n")
            f.write(f"- **Ratio pointe/creuse:** {t['peak_to_offpeak_ratio']:.1f}x\n")
            f.write(f"- **Moyenne rush matinal (7h-9h):** {t['morning_rush_avg']:,.0f} passages\n")
            f.write(f"- **Moyenne rush du soir (17h-19h):** {t['evening_rush_avg']:,.0f} passages\n\n")

        # Lignes principales
        if 'routes' in analysis_results and analysis_results['routes']:
            r = analysis_results['routes']
            f.write("### 3.2 Lignes les plus fréquentées\n\n")
            f.write("| Rang | Ligne | Nombre de passages |\n")
            f.write("|------|-------|--------------------|\n")
            for i, (ligne, freq) in enumerate(r['top_routes'].head(10).items(), 1):
                f.write(f"| {i} | {ligne} | {freq:,} |\n")
            f.write(f"\n**Coefficient de variation:** {r['coefficient_of_variation']:.2f} ")
            f.write(f"({'forte dispersion' if r['coefficient_of_variation'] > 0.5 else 'faible dispersion'})\n\n")

        # Arrêts principaux
        if 'stops' in analysis_results:
            s = analysis_results['stops']
            f.write("### 3.3 Arrêts les plus fréquentés\n\n")
            f.write("| Rang | Arrêt | Nombre de passages |\n")
            f.write("|------|-------|--------------------|\n")
            for i, (idx, freq) in enumerate(s['top_stops'].head(10).items(), 1):
                stop_name = idx[1]
                f.write(f"| {i} | {stop_name} | {freq:,} |\n")
            f.write(f"\n**Arrêts sous-utilisés:** {len(s['underutilized_stops']):,} ")
            f.write(f"({len(s['underutilized_stops'])/s['total_stops']*100:.1f}% du total)\n\n")

        f.write("---\n\n")
        f.write("## 4. Visualisations\n\n")
        f.write("Les visualisations suivantes ont été générées:\n\n")
        f.write("### Visualisations statiques (PNG)\n\n")
        f.write("1. **Heatmap temporelle** - [visualisations/heatmap_temporel.png](visualisations/heatmap_temporel.png)\n")
        f.write("2. **Distribution horaire** - [visualisations/distribution_horaire.png](visualisations/distribution_horaire.png)\n")
        f.write("3. **Top lignes** - [visualisations/top_lignes.png](visualisations/top_lignes.png)\n")
        f.write("4. **Top arrêts** - [visualisations/top_arrets.png](visualisations/top_arrets.png)\n\n")
        f.write("### Visualisations interactives (HTML)\n\n")
        f.write("1. **Carte interactive** - [visualisations/carte_interactive.html](visualisations/carte_interactive.html)\n")
        f.write("2. **Dashboard horaire** - [visualisations/dashboard_horaire.html](visualisations/dashboard_horaire.html)\n")
        f.write("3. **Dashboard lignes** - [visualisations/dashboard_lignes.html](visualisations/dashboard_lignes.html)\n\n")

        f.write("---\n\n")
        f.write("## 5. Recommandations\n\n")
        for i, rec in enumerate(recommendations, 1):
            f.write(f"### 5.{i} {rec['category']} (Priorité: {rec['priority']})\n\n")
            f.write(f"**Observation:** {rec['observation']}\n\n")
            f.write(f"**Recommandation:** {rec['recommendation']}\n\n")
            f.write(f"**Impact attendu:** {rec['expected_impact']}\n\n")

        f.write("---\n\n")
        f.write("## 6. Limites de l'analyse\n\n")
        f.write("- Les données GTFS représentent les horaires planifiés, pas la fréquentation réelle des passagers\n")
        f.write("- Pas de données sur le nombre effectif de passagers par trajet\n")
        f.write("- Pas d'informations sur les retards ou perturbations du service\n")
        f.write("- L'analyse ne distingue pas les différents jours de la semaine (simulation utilisée)\n")
        f.write("- Pas de données météorologiques ou d'événements spéciaux\n\n")

        f.write("---\n\n")
        f.write("## 7. Conclusion\n\n")
        f.write("Cette analyse a permis d'identifier les patterns clés de mobilité à Bordeaux. ")
        f.write("Les visualisations et recommandations fournies peuvent aider TBM à optimiser ")
        f.write("son réseau de transport pour mieux répondre aux besoins des usagers.\n\n")
        f.write("Les principales conclusions sont:\n\n")

        if 'temporal' in analysis_results:
            t = analysis_results['temporal']
            f.write(f"- Une forte variation de la fréquentation selon l'heure (ratio {t['peak_to_offpeak_ratio']:.1f}x)\n")

        if 'routes' in analysis_results and analysis_results['routes']:
            r = analysis_results['routes']
            if r['coefficient_of_variation'] > 0.5:
                f.write("- Une concentration importante du trafic sur quelques lignes principales\n")

        if 'stops' in analysis_results:
            s = analysis_results['stops']
            f.write(f"- {len(s['underutilized_stops'])} arrêts sous-utilisés nécessitant une réévaluation\n")

        f.write("\n---\n\n")
        f.write("*Rapport généré automatiquement par le système d'analyse de mobilité urbaine*\n")

    logger.info(f"✓ Rapport final généré: {filepath}")


def main():
    """Fonction principale"""
    try:
        print_header()

        # Étape 1: Chargement des données
        logger.info("="*80)
        logger.info("ÉTAPE 1/5: CHARGEMENT DES DONNÉES")
        logger.info("="*80)
        loader = GTFSDataLoader()
        data_dict = loader.load_all(include_shapes=False)

        if not loader.validate_data():
            logger.error("❌ Validation des données échouée")
            return 1

        # Étape 2: Prétraitement
        logger.info("\n" + "="*80)
        logger.info("ÉTAPE 2/5: PRÉTRAITEMENT DES DONNÉES")
        logger.info("="*80)
        preprocessor = GTFSPreprocessor(data_dict)
        data_enriched = preprocessor.preprocess_all()

        # Statistiques sommaires
        stats = preprocessor.get_summary_stats()
        logger.info(f"\nStatistiques sommaires:")
        logger.info(f"  - Total passages: {stats['total_passages']:,}")
        logger.info(f"  - Arrêts uniques: {stats['unique_stops']:,}")
        logger.info(f"  - Lignes uniques: {stats['unique_routes']:,}")
        logger.info(f"  - Trajets uniques: {stats['unique_trips']:,}")

        # Étape 3: Analyse
        logger.info("\n" + "="*80)
        logger.info("ÉTAPE 3/5: ANALYSE EXPLORATOIRE")
        logger.info("="*80)
        analyzer = MobilityAnalyzer(data_enriched)
        analysis_results = analyzer.analyze_all()

        # Étape 4: Visualisations
        logger.info("\n" + "="*80)
        logger.info("ÉTAPE 4/5: CRÉATION DES VISUALISATIONS")
        logger.info("="*80)
        visualizer = MobilityVisualizer(data_enriched, analysis_results)
        visualizer.create_all_visualizations()

        # Étape 5: Recommandations et rapport
        logger.info("\n" + "="*80)
        logger.info("ÉTAPE 5/5: GÉNÉRATION DES RECOMMANDATIONS ET RAPPORT")
        logger.info("="*80)
        recommendations = analyzer.generate_recommendations()
        save_recommendations(recommendations)
        generate_markdown_report(data_enriched, analysis_results, recommendations)

        # Conclusion
        print("\n" + "="*80)
        print("ANALYSE TERMINEE AVEC SUCCES!")
        print("="*80)
        print("\nFichiers générés:")
        print(f"  📊 Visualisations: {OUTPUT_PATH}/")
        print("  📝 Rapport: RAPPORT_FINAL.md")
        print("  💡 Recommandations: recommandations.txt")
        print("  📋 Logs: analysis.log")
        print("\nPour explorer les visualisations:")
        print(f"  - Ouvrez {OUTPUT_PATH}/carte_interactive.html dans votre navigateur")
        print(f"  - Consultez {OUTPUT_PATH}/dashboard_horaire.html pour le dashboard interactif")
        print("\n" + "="*80 + "\n")

        return 0

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Analyse interrompue par l'utilisateur")
        return 130
    except Exception as e:
        logger.error(f"\n\n❌ Erreur lors de l'analyse: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
