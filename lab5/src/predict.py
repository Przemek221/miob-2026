"""Predict a digit from a saved model and a single PNG image."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from src.data import load_image_features


def predict_image(model_path: str | Path, image_path: str | Path) -> int:
    """Load a fitted model and predict one image without accessing any label."""
    bundle = joblib.load(model_path)
    model = bundle["model"]
    prediction = model.predict(load_image_features(image_path).reshape(1, -1))
    return int(prediction[0])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Path to an 8 x 8 grayscale PNG")
    parser.add_argument("--model", default="models/digit_classifier.joblib")
    args = parser.parse_args()
    print(predict_image(args.model, args.image))


if __name__ == "__main__":
    main()
