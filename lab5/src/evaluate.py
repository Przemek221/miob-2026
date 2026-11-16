"""Final, one-shot evaluation on the held-out test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix

from src.data import load_dataset


def evaluate(model_path: str | Path, test_csv: str | Path, predictions_path: str | Path, metrics_path: str | Path) -> dict[str, object]:
    """Evaluate the saved model, write predictions and metrics for a labelled split."""
    bundle = joblib.load(model_path)
    x_test, y_test, frame = load_dataset(test_csv)
    predicted = bundle["model"].predict(x_test).astype(int)
    output = pd.DataFrame({"image_id": frame["image_id"], "prediction": predicted})
    predictions_path = Path(predictions_path)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(predictions_path, index=False)
    labels = list(range(10))
    matrix = confusion_matrix(y_test, predicted, labels=labels)
    mistakes = [
        {"true": int(actual), "predicted": int(prediction), "count": int(count)}
        for actual, prediction, count in zip(*__import__("numpy").where(matrix > 0))
        if actual != prediction
    ]
    mistakes.sort(key=lambda item: (-item["count"], item["true"], item["predicted"]))
    metrics = {
        "model_name": bundle.get("model_name"),
        "accuracy": float(accuracy_score(y_test, predicted)),
        "correct": int((y_test == predicted).sum()),
        "incorrect": int((y_test != predicted).sum()),
        "confusion_matrix": matrix.tolist(),
        "most_common_confusions": mistakes,
    }
    metrics_path = Path(metrics_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="models/digit_classifier.joblib")
    parser.add_argument("--test", default="data/test.csv")
    parser.add_argument("--predictions", default="artifacts/test_predictions.csv")
    parser.add_argument("--metrics", default="artifacts/test_metrics.json")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.model, args.test, args.predictions, args.metrics), indent=2))


if __name__ == "__main__":
    main()
