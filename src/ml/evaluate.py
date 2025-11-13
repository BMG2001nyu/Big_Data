"""Model evaluation utilities and reporting."""
from __future__ import annotations

import json
import logging
import pathlib
from typing import Dict

import pandas as pd


def load_metrics(metrics_dir: pathlib.Path) -> Dict[str, Dict[str, float]]:
    metrics: Dict[str, Dict[str, float]] = {}
    for json_file in metrics_dir.glob("*_metrics.json"):
        with json_file.open("r", encoding="utf-8") as file:
            metrics[json_file.stem.replace("_metrics", "")] = json.load(file)
    return metrics


def save_report(metrics: Dict[str, Dict[str, float]], report_path: pathlib.Path) -> None:
    report_lines = ["# Model Performance Report", ""]
    for model_name, model_metrics in metrics.items():
        report_lines.append(f"## {model_name}")
        for metric, value in model_metrics.items():
            report_lines.append(f"- {metric.upper()}: {value:.4f}")
        report_lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def compare_predictions(ground_truth: pd.Series, predictions: pd.Series) -> Dict[str, float]:
    residuals = ground_truth - predictions
    return {
        "mean_residual": residuals.mean(),
        "std_residual": residuals.std(),
        "median_abs_error": (residuals.abs()).median(),
    }


def main(metrics_dir: str, report_path: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    metrics = load_metrics(pathlib.Path(metrics_dir))
    save_report(metrics, pathlib.Path(report_path))
    logging.info("Saved model performance report to %s", report_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate model performance report")
    parser.add_argument("metrics_dir", help="Directory containing *_metrics.json files")
    parser.add_argument("report_path", help="Markdown report output path")
    args = parser.parse_args()
    main(args.metrics_dir, args.report_path)
