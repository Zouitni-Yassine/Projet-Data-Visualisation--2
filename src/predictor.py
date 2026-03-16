"""
Module de modélisation prédictive de l'affluence
Utilise scikit-learn pour prédire la fréquentation future
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

# Vérifier si scikit-learn est disponible
try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn n'est pas installé. pip install scikit-learn")


class MobilityPredictor:
    """Modélisation prédictive de l'affluence des transports publics"""

    def __init__(self, data: pd.DataFrame, output_path: Path = None):
        """
        Initialise le prédicteur

        Args:
            data: DataFrame enrichi des données de mobilité
            output_path: Chemin de sortie pour les visualisations
        """
        self.data = data
        self.output_path = output_path or Path("visualisations")
        self.models = {}
        self.results = {}
        self.feature_names = []

    def run_all_predictions(self) -> Dict:
        """
        Exécute toutes les prédictions

        Returns:
            Dictionnaire contenant tous les résultats de prédiction
        """
        if not SKLEARN_AVAILABLE:
            logger.error("❌ scikit-learn requis. Installez-le : pip install scikit-learn")
            return {}

        logger.info("Début de la modélisation prédictive...")

        # 1. Préparer les features
        X, y = self._prepare_features()

        if X is None or len(X) == 0:
            logger.error("❌ Impossible de préparer les features")
            return {}

        # 2. Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info(f"  → Données d'entraînement: {len(X_train):,} échantillons")
        logger.info(f"  → Données de test: {len(X_test):,} échantillons")

        # 3. Entraîner les modèles
        self._train_models(X_train, y_train)

        # 4. Évaluer les modèles
        self._evaluate_models(X_test, y_test)

        # 5. Analyse de l'importance des features
        self._analyze_feature_importance()

        # 6. Prédictions futures (scénarios)
        self._predict_scenarios()

        # 7. Créer les visualisations
        self._create_prediction_visualizations(X_test, y_test)

        logger.info("✓ Modélisation prédictive terminée")
        self._print_results()

        return self.results

    def _prepare_features(self) -> Tuple:
        """
        Prépare les features pour la modélisation

        Returns:
            Tuple (X, y) avec features et target
        """
        logger.info("  → Préparation des features...")

        # Agréger les données par heure et ligne
        if 'route_short_name' in self.data.columns:
            agg_data = self.data.groupby(
                ['hour', 'route_short_name']
            ).agg(
                nb_passages=('stop_id', 'count'),
                nb_arrets_uniques=('stop_id', 'nunique'),
                lat_moyenne=('stop_lat', 'mean'),
                lon_moyenne=('stop_lon', 'mean'),
            ).reset_index()
        else:
            agg_data = self.data.groupby(
                ['hour']
            ).agg(
                nb_passages=('stop_id', 'count'),
                nb_arrets_uniques=('stop_id', 'nunique'),
                lat_moyenne=('stop_lat', 'mean'),
                lon_moyenne=('stop_lon', 'mean'),
            ).reset_index()

        if len(agg_data) == 0:
            return None, None

        # Créer les features temporelles
        agg_data['est_heure_pointe_matin'] = agg_data['hour'].apply(
            lambda h: 1 if 7 <= h <= 9 else 0
        )
        agg_data['est_heure_pointe_soir'] = agg_data['hour'].apply(
            lambda h: 1 if 17 <= h <= 19 else 0
        )
        agg_data['est_nuit'] = agg_data['hour'].apply(
            lambda h: 1 if h >= 22 or h <= 5 else 0
        )
        agg_data['est_journee'] = agg_data['hour'].apply(
            lambda h: 1 if 9 <= h <= 17 else 0
        )

        # Features cycliques pour l'heure (sin/cos)
        agg_data['hour_sin'] = np.sin(2 * np.pi * agg_data['hour'] / 24)
        agg_data['hour_cos'] = np.cos(2 * np.pi * agg_data['hour'] / 24)

        # Encoder les lignes si présentes
        if 'route_short_name' in agg_data.columns:
            # Encoder les top 20 lignes, le reste = "Autre"
            top_routes = agg_data.groupby('route_short_name')['nb_passages'].sum()\
                .nlargest(20).index.tolist()
            agg_data['route_encoded'] = agg_data['route_short_name'].apply(
                lambda x: top_routes.index(x) if x in top_routes else 20
            )
            feature_cols = [
                'hour', 'nb_arrets_uniques', 'lat_moyenne', 'lon_moyenne',
                'est_heure_pointe_matin', 'est_heure_pointe_soir',
                'est_nuit', 'est_journee', 'hour_sin', 'hour_cos',
                'route_encoded'
            ]
        else:
            feature_cols = [
                'hour', 'nb_arrets_uniques', 'lat_moyenne', 'lon_moyenne',
                'est_heure_pointe_matin', 'est_heure_pointe_soir',
                'est_nuit', 'est_journee', 'hour_sin', 'hour_cos'
            ]

        available_cols = [col for col in feature_cols if col in agg_data.columns]
        self.feature_names = available_cols

        X = agg_data[available_cols].values
        y = agg_data['nb_passages'].values

        # Normaliser les features
        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X)

        logger.info(f"  → {len(available_cols)} features créées, {len(X):,} échantillons")

        self.results['feature_names'] = available_cols
        self.results['n_samples'] = len(X)
        self.results['n_features'] = len(available_cols)

        return X, y

    def _train_models(self, X_train, y_train):
        """Entraîne plusieurs modèles de régression"""
        logger.info("  → Entraînement des modèles...")

        models = {
            'Régression Linéaire': LinearRegression(),
            'Random Forest': RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
            )
        }

        for name, model in models.items():
            logger.info(f"    → Entraînement: {name}...")
            model.fit(X_train, y_train)
            self.models[name] = model

            # Validation croisée
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            logger.info(f"      R² moyen (CV-5): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    def _evaluate_models(self, X_test, y_test):
        """Évalue les modèles sur les données de test"""
        logger.info("  → Évaluation des modèles...")

        evaluations = {}

        for name, model in self.models.items():
            y_pred = model.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100

            evaluations[name] = {
                'MAE': mae,
                'RMSE': rmse,
                'R2': r2,
                'MAPE': mape,
                'predictions': y_pred
            }

            logger.info(f"    {name}: R²={r2:.4f}, MAE={mae:.1f}, RMSE={rmse:.1f}")

        # Identifier le meilleur modèle
        best_model_name = max(evaluations, key=lambda k: evaluations[k]['R2'])
        self.results['evaluations'] = evaluations
        self.results['best_model'] = best_model_name
        self.results['best_r2'] = evaluations[best_model_name]['R2']

        logger.info(f"  ✓ Meilleur modèle: {best_model_name} (R²={evaluations[best_model_name]['R2']:.4f})")

    def _analyze_feature_importance(self):
        """Analyse l'importance des features (pour Random Forest)"""
        logger.info("  → Analyse de l'importance des features...")

        if 'Random Forest' in self.models:
            model = self.models['Random Forest']
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]

            feature_importance = {}
            for i in range(len(self.feature_names)):
                feature_importance[self.feature_names[indices[i]]] = importances[indices[i]]

            self.results['feature_importance'] = feature_importance

            # Afficher le top 5
            for i, (name, imp) in enumerate(list(feature_importance.items())[:5]):
                logger.info(f"    {i+1}. {name}: {imp:.4f}")

    def _predict_scenarios(self):
        """Génère des prédictions pour différents scénarios"""
        logger.info("  → Génération de scénarios prédictifs...")

        if 'Random Forest' not in self.models:
            return

        model = self.models['Random Forest']

        # Scénario: prédire pour chaque heure de la journée
        scenarios = []
        for hour in range(24):
            features = {
                'hour': hour,
                'nb_arrets_uniques': 50,  # Valeur moyenne
                'lat_moyenne': 44.84,     # Centre Bordeaux
                'lon_moyenne': -0.58,
                'est_heure_pointe_matin': 1 if 7 <= hour <= 9 else 0,
                'est_heure_pointe_soir': 1 if 17 <= hour <= 19 else 0,
                'est_nuit': 1 if hour >= 22 or hour <= 5 else 0,
                'est_journee': 1 if 9 <= hour <= 17 else 0,
                'hour_sin': np.sin(2 * np.pi * hour / 24),
                'hour_cos': np.cos(2 * np.pi * hour / 24),
            }

            if 'route_encoded' in self.feature_names:
                features['route_encoded'] = 0  # Ligne principale

            X_scenario = np.array([[features.get(f, 0) for f in self.feature_names]])
            X_scenario = self.scaler.transform(X_scenario)
            pred = model.predict(X_scenario)[0]
            scenarios.append({'hour': hour, 'predicted_passages': max(0, pred)})

        self.results['hourly_predictions'] = pd.DataFrame(scenarios)

    def _create_prediction_visualizations(self, X_test, y_test):
        """Crée les visualisations de prédiction"""
        logger.info("  → Création des visualisations prédictives...")

        # 1. Comparaison des modèles (bar chart)
        self._plot_model_comparison()

        # 2. Prédictions vs Réalité (scatter)
        self._plot_predictions_vs_reality(X_test, y_test)

        # 3. Importance des features
        self._plot_feature_importance()

        # 4. Prédictions horaires
        self._plot_hourly_predictions()

    def _plot_model_comparison(self):
        """Graphique de comparaison des performances des modèles"""
        if 'evaluations' not in self.results:
            return

        evals = self.results['evaluations']
        models_names = list(evals.keys())
        r2_scores = [evals[m]['R2'] for m in models_names]
        mae_scores = [evals[m]['MAE'] for m in models_names]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # R² Score
        colors = ['#2ecc71' if s == max(r2_scores) else '#3498db' for s in r2_scores]
        bars1 = ax1.bar(models_names, r2_scores, color=colors, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Score R²', fontsize=13, weight='bold')
        ax1.set_title('Coefficient de Détermination (R²)\nPlus élevé = Meilleur',
                       fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylim(0, 1.05)
        ax1.grid(True, alpha=0.3, axis='y', linestyle=':')

        for bar, val in zip(bars1, r2_scores):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                     f'{val:.4f}', ha='center', va='bottom', fontsize=12, weight='bold')

        # MAE
        colors_mae = ['#2ecc71' if s == min(mae_scores) else '#e74c3c' for s in mae_scores]
        bars2 = ax2.bar(models_names, mae_scores, color=colors_mae, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Erreur Absolue Moyenne (MAE)', fontsize=13, weight='bold')
        ax2.set_title('Erreur Absolue Moyenne\nPlus faible = Meilleur',
                       fontsize=14, fontweight='bold', pad=15)
        ax2.grid(True, alpha=0.3, axis='y', linestyle=':')

        for bar, val in zip(bars2, mae_scores):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(mae_scores)*0.02,
                     f'{val:.1f}', ha='center', va='bottom', fontsize=12, weight='bold')

        plt.tight_layout()
        plt.savefig(self.output_path / 'prediction_comparaison_modeles.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("  ✓ Graphique comparaison modèles créé")

    def _plot_predictions_vs_reality(self, X_test, y_test):
        """Scatter plot Prédictions vs Réalité"""
        best_name = self.results.get('best_model', 'Random Forest')
        if best_name not in self.models:
            return

        model = self.models[best_name]
        y_pred = model.predict(X_test)

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(y_test, y_pred, alpha=0.4, s=30, c='royalblue', edgecolors='navy', linewidth=0.5)

        # Ligne parfaite
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Prédiction parfaite')

        r2 = self.results['evaluations'][best_name]['R2']
        mae = self.results['evaluations'][best_name]['MAE']

        ax.set_xlabel('Valeurs Réelles', fontsize=14, weight='bold')
        ax.set_ylabel('Prédictions', fontsize=14, weight='bold')
        ax.set_title(
            f'Prédictions vs Réalité — {best_name}\n'
            f'R² = {r2:.4f} | MAE = {mae:.1f}',
            fontsize=15, fontweight='bold', pad=20
        )
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, linestyle=':')

        plt.tight_layout()
        plt.savefig(self.output_path / 'prediction_vs_realite.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("  ✓ Graphique prédictions vs réalité créé")

    def _plot_feature_importance(self):
        """Graphique de l'importance des features"""
        if 'feature_importance' not in self.results:
            return

        fi = self.results['feature_importance']
        names = list(fi.keys())
        values = list(fi.values())

        # Traduction des noms pour les rendre lisibles
        translations = {
            'hour': 'Heure',
            'nb_arrets_uniques': 'Nb arrêts uniques',
            'lat_moyenne': 'Latitude moyenne',
            'lon_moyenne': 'Longitude moyenne',
            'est_heure_pointe_matin': 'Heure pointe matin',
            'est_heure_pointe_soir': 'Heure pointe soir',
            'est_nuit': 'Nuit',
            'est_journee': 'Journée',
            'hour_sin': 'Heure (sin)',
            'hour_cos': 'Heure (cos)',
            'route_encoded': 'Ligne de transport'
        }

        labels = [translations.get(n, n) for n in names]

        fig, ax = plt.subplots(figsize=(12, 8))

        # Barres horizontales, triées par importance
        y_pos = range(len(labels))
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(labels)))[::-1]

        bars = ax.barh(y_pos, values, color=colors, edgecolor='black', linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=12)
        ax.set_xlabel('Importance', fontsize=13, weight='bold')
        ax.set_title('Importance des Variables dans la Prédiction\n(Random Forest)',
                      fontsize=15, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x', linestyle=':')

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + max(values)*0.02, bar.get_y() + bar.get_height()/2.,
                    f'{val:.3f}', va='center', fontsize=10, weight='bold')

        plt.tight_layout()
        plt.savefig(self.output_path / 'prediction_importance_features.png',
                    dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("  ✓ Graphique importance features créé")

    def _plot_hourly_predictions(self):
        """Graphique des prédictions horaires"""
        if 'hourly_predictions' not in self.results:
            return

        df_pred = self.results['hourly_predictions']

        # Récupérer aussi les données réelles pour comparer
        real_data = self.data.groupby('hour').size().reset_index()
        real_data.columns = ['hour', 'real_passages']

        # Normaliser pour comparaison (même échelle relative)
        if len(real_data) > 0:
            real_max = real_data['real_passages'].max()
            pred_max = df_pred['predicted_passages'].max()

            fig, ax = plt.subplots(figsize=(14, 7))

            # Données réelles
            ax.plot(real_data['hour'], real_data['real_passages'],
                    marker='o', linewidth=2.5, markersize=8,
                    color='royalblue', label='Données observées', zorder=3)
            ax.fill_between(real_data['hour'], real_data['real_passages'],
                           alpha=0.15, color='royalblue')

            # Prédictions (normalisées à la même échelle)
            pred_scaled = df_pred['predicted_passages'] * (real_max / pred_max) if pred_max > 0 else df_pred['predicted_passages']
            ax.plot(df_pred['hour'], pred_scaled,
                    marker='s', linewidth=2.5, markersize=8,
                    color='#e74c3c', linestyle='--', label='Prédictions (Random Forest)', zorder=3)
            ax.fill_between(df_pred['hour'], pred_scaled, alpha=0.10, color='#e74c3c')

            # Zones de rush
            ax.axvspan(7, 9, alpha=0.08, color='orange', label='Rush matinal (7h-9h)')
            ax.axvspan(17, 19, alpha=0.08, color='orange', label='Rush soir (17h-19h)')

            ax.set_xlabel('Heure de la journée', fontsize=13, weight='bold')
            ax.set_ylabel('Nombre de passages', fontsize=13, weight='bold')
            ax.set_title(
                'Prédiction de l\'Affluence par Heure\nComparaison Données Observées vs Modèle Prédictif',
                fontsize=15, fontweight='bold', pad=20
            )
            ax.set_xticks(range(24))
            ax.set_xticklabels([f'{h}h' for h in range(24)], rotation=45)
            ax.legend(fontsize=11, loc='upper left')
            ax.grid(True, alpha=0.3, linestyle=':')

            plt.tight_layout()
            plt.savefig(self.output_path / 'prediction_horaire.png',
                        dpi=300, bbox_inches='tight')
            plt.close()
            logger.info("  ✓ Graphique prédictions horaires créé")

    def _print_results(self):
        """Affiche un résumé des résultats de prédiction"""
        logger.info("\n" + "=" * 70)
        logger.info("RÉSULTATS DE LA MODÉLISATION PRÉDICTIVE")
        logger.info("=" * 70)

        if 'evaluations' in self.results:
            for name, metrics in self.results['evaluations'].items():
                marker = " ⭐" if name == self.results.get('best_model') else ""
                logger.info(f"\n  📊 {name}{marker}:")
                logger.info(f"     R² = {metrics['R2']:.4f}")
                logger.info(f"     MAE = {metrics['MAE']:.1f}")
                logger.info(f"     RMSE = {metrics['RMSE']:.1f}")
                logger.info(f"     MAPE = {metrics['MAPE']:.1f}%")

        if 'feature_importance' in self.results:
            logger.info(f"\n  🔑 Top 3 features les plus importantes:")
            for i, (name, imp) in enumerate(list(self.results['feature_importance'].items())[:3]):
                logger.info(f"     {i+1}. {name}: {imp:.4f}")

        logger.info("\n" + "=" * 70 + "\n")
