"""Train candidate digit classifiers using the fixed train/validation split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from src.data import load_dataset


def candidate_models() -> list[tuple[str, Pipeline]]:
    return [
        (f"knn_k{k}", Pipeline([("classifier", KNeighborsClassifier(n_neighbors=k))]))
        for k in (1, 3, 5, 7)
    ] + [
        (f"svc_c{c}_gamma{gamma}", Pipeline([("classifier", SVC(C=c, gamma=gamma))]))
        for c in (1.0, 10.0)
        for gamma in ("scale", 0.01)
    ]


def train_and_select(
    train_csv: str | Path,
    validation_csv: str | Path,
    model_path: str | Path,
    results_path: str | Path,
    max_train_rows: int | None = None,
) -> pd.DataFrame:
    """Fit candidates on train, select strictly by validation accuracy, save winner."""
    x_train, y_train, _ = load_dataset(train_csv)
    if max_train_rows is not None:
        x_train, y_train = x_train[:max_train_rows], y_train[:max_train_rows]
    x_validation, y_validation, _ = load_dataset(validation_csv)
    results: list[dict[str, object]] = []
    best_name: str | None = None
    best_model: Pipeline | None = None
    best_accuracy = -1.0
    for name, model in candidate_models():
        model.fit(x_train, y_train)
        accuracy = float(model.score(x_validation, y_validation))
        results.append({"model": name, "validation_accuracy": accuracy})
        if accuracy > best_accuracy:
            best_name, best_model, best_accuracy = name, model, accuracy
    assert best_name is not None and best_model is not None
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_model, "model_name": best_name, "feature_count": 64}, model_path)
    table = pd.DataFrame(results).sort_values(["validation_accuracy", "model"], ascending=[False, True])
    results_path = Path(results_path)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(results_path, index=False)
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", default="data/train.csv")
    parser.add_argument("--validation", default="data/validation.csv")
    parser.add_argument("--model", default="models/digit_classifier.joblib")
    parser.add_argument("--results", default="artifacts/validation_results.csv")
    parser.add_argument("--max-train-rows", type=int, help="Optional small training slice, useful for a quick check")
    args = parser.parse_args()
    table = train_and_select(args.train, args.validation, args.model, args.results, args.max_train_rows)
    print(table.to_string(index=False))
    print(json.dumps({"selected_model": table.iloc[0]["model"], "validation_accuracy": table.iloc[0]["validation_accuracy"]}))


if __name__ == "__main__":
    main()
