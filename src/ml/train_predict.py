"""Training pipeline for supervised congestion prediction models."""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
from dataclasses import dataclass
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
try:  # pragma: no cover - optional dependency may not be available locally
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except Exception:  # pylint: disable=broad-except
    XGBOOST_AVAILABLE = False


@dataclass
class TrainingConfig:
    processed_path: pathlib.Path
    target_col: str = "vehicle_count"
    feature_cols: List[str] = None
    output_dir: pathlib.Path = pathlib.Path("models")
    n_splits: int = 5
    random_state: int = 42
    classification_threshold: float = 1.2
    plots_dir: pathlib.Path = pathlib.Path("reports/plots")

    def __post_init__(self) -> None:
        if self.feature_cols is None:
            self.feature_cols = [
                "hour",
                "is_weekend",
                "borough",
                "roadwayname",
                "direction",
                "volume_per_minute",
                "weekpart_congestion_ratio",
            ]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)


class ModelTrainer:
    def __init__(self, config: TrainingConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        if not XGBOOST_AVAILABLE:
            self.logger.warning(
                "XGBoost is unavailable. Skipping XGB models; install libomp and xgboost for full pipeline."
            )

    def load_data(self) -> pd.DataFrame:
        parquet_files = list(self.config.processed_path.glob("**/*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files found in {self.config.processed_path}")

        self.logger.info("Loading %d parquet files", len(parquet_files))
        df = pd.concat((pd.read_parquet(file) for file in parquet_files), ignore_index=True)
        df = df.sort_values("from_hour")
        return df

    def build_preprocessor(self) -> ColumnTransformer:
        numeric_features = [
            col for col in self.config.feature_cols if col not in {"borough", "roadwayname", "direction"}
        ]
        categorical_features = [col for col in self.config.feature_cols if col not in numeric_features]

        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_pipeline = OneHotEncoder(handle_unknown="ignore")

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, numeric_features),
                ("cat", categorical_pipeline, categorical_features),
            ],
            remainder="drop",
        )
        return preprocessor

    def train_models(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        X = df[self.config.feature_cols]
        y = df[self.config.target_col]
        congestion_series = df.get("congestion_index")
        if congestion_series is None:
            raise KeyError("congestion_index column is required for classification targets")
        y_class = (congestion_series.fillna(0) >= self.config.classification_threshold).astype(int)

        splitter = TimeSeriesSplit(n_splits=self.config.n_splits)
        metrics: Dict[str, Dict[str, float]] = {}
        metrics.update(self._train_regressors(X, y, splitter))
        metrics.update(self._train_classifiers(X, y_class, splitter))
        return metrics

    def _train_regressors(
        self, X: pd.DataFrame, y: pd.Series, splitter: TimeSeriesSplit
    ) -> Dict[str, Dict[str, float]]:
        regressors = {
            "random_forest_regressor": RandomForestRegressor(
                n_estimators=200, random_state=self.config.random_state
            )
        }
        if XGBOOST_AVAILABLE:
            regressors["xgboost_regressor"] = XGBRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=8,
                subsample=0.8,
                colsample_bytree=0.8,
                objective="reg:squarederror",
                random_state=self.config.random_state,
            )
        results: Dict[str, Dict[str, float]] = {}

        for model_name, estimator in regressors.items():
            self.logger.info("Training %s", model_name)
            scores: List[Dict[str, float]] = []
            for fold, (train_idx, test_idx) in enumerate(splitter.split(X), start=1):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

                pipeline = Pipeline(
                    steps=[
                        ("preprocessor", self.build_preprocessor()),
                        ("model", estimator),
                    ]
                )
                pipeline.fit(X_train, y_train)
                predictions = pipeline.predict(X_test)
                fold_metrics = {
                    "mae": mean_absolute_error(y_test, predictions),
                    "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
                    "r2": r2_score(y_test, predictions),
                }
                self.logger.info("%s fold %d metrics: %s", model_name, fold, fold_metrics)
                scores.append(fold_metrics)

            aggregated = {
                metric: float(np.mean([score[metric] for score in scores]))
                for metric in ["mae", "rmse", "r2"]
            }
            results[model_name] = aggregated
            final_pipeline = Pipeline(
                steps=[
                    ("preprocessor", self.build_preprocessor()),
                    ("model", estimator),
                ]
            )
            final_pipeline.fit(X, y)
            joblib.dump(final_pipeline, self.config.output_dir / f"{model_name}.joblib")
            self._write_metrics(model_name, aggregated)
            self._plot_feature_importance(final_pipeline, model_name)
        return results

    def _train_classifiers(
        self, X: pd.DataFrame, y: pd.Series, splitter: TimeSeriesSplit
    ) -> Dict[str, Dict[str, float]]:
        classifiers = {
            "random_forest_classifier": RandomForestClassifier(
                n_estimators=300,
                class_weight="balanced",
                random_state=self.config.random_state,
            )
        }
        if XGBOOST_AVAILABLE:
            classifiers["xgboost_classifier"] = XGBClassifier(
                n_estimators=400,
                learning_rate=0.05,
                max_depth=8,
                subsample=0.8,
                colsample_bytree=0.8,
                objective="binary:logistic",
                random_state=self.config.random_state,
            )
        results: Dict[str, Dict[str, float]] = {}

        for model_name, estimator in classifiers.items():
            self.logger.info("Training %s", model_name)
            scores: List[Dict[str, float]] = []
            for fold, (train_idx, test_idx) in enumerate(splitter.split(X), start=1):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

                pipeline = Pipeline(
                    steps=[
                        ("preprocessor", self.build_preprocessor()),
                        ("model", estimator),
                    ]
                )
                pipeline.fit(X_train, y_train)
                predictions = pipeline.predict(X_test)
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y_test, predictions, average="binary", zero_division=0
                )
                fold_metrics = {
                    "accuracy": accuracy_score(y_test, predictions),
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                }
                self.logger.info("%s fold %d metrics: %s", model_name, fold, fold_metrics)
                scores.append(fold_metrics)

            aggregated = {
                metric: float(np.mean([score[metric] for score in scores]))
                for metric in ["accuracy", "precision", "recall", "f1"]
            }
            results[model_name] = aggregated
            final_pipeline = Pipeline(
                steps=[
                    ("preprocessor", self.build_preprocessor()),
                    ("model", estimator),
                ]
            )
            final_pipeline.fit(X, y)
            joblib.dump(final_pipeline, self.config.output_dir / f"{model_name}.joblib")
            self._write_metrics(model_name, aggregated)
            self._plot_feature_importance(final_pipeline, model_name)
        return results

    def _write_metrics(self, model_name: str, metrics: Dict[str, float]) -> None:
        report_path = self.config.output_dir / f"{model_name}_metrics.json"
        with report_path.open("w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=2)
        self.logger.info("Wrote metrics to %s", report_path)

    def _plot_feature_importance(self, pipeline: Pipeline, model_name: str) -> None:
        model = pipeline.named_steps.get("model")
        if not hasattr(model, "feature_importances_"):
            return
        preprocessor = pipeline.named_steps.get("preprocessor")
        try:
            feature_names = preprocessor.get_feature_names_out()
        except AttributeError:
            feature_names = [f"feature_{idx}" for idx in range(len(model.feature_importances_))]

        importances = model.feature_importances_
        order = np.argsort(importances)[::-1][:20]
        ordered_features = np.array(feature_names)[order]
        ordered_importances = importances[order]

        plt.figure(figsize=(10, 6))
        plt.barh(ordered_features, ordered_importances)
        plt.gca().invert_yaxis()
        plt.title(f"Feature Importance - {model_name}")
        plt.xlabel("Importance")
        plt.tight_layout()
        plot_path = self.config.plots_dir / f"{model_name}_feature_importance.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()
        self.logger.info("Saved feature importance plot to %s", plot_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train congestion prediction models")
    parser.add_argument("processed_path", type=pathlib.Path, help="Path to processed parquet data")
    parser.add_argument("--target-col", type=str, default="vehicle_count")
    parser.add_argument("--feature-cols", nargs="*", default=None)
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("models"))
    parser.add_argument("--n-splits", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    config = TrainingConfig(
        processed_path=args.processed_path,
        target_col=args.target_col,
        feature_cols=args.feature_cols,
        output_dir=args.output_dir,
        n_splits=args.n_splits,
    )
    trainer = ModelTrainer(config)
    df = trainer.load_data()
    metrics = trainer.train_models(df)
    logging.info("Training complete: %s", metrics)


if __name__ == "__main__":
    main()
