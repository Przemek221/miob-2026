"""Loading and validating 8 x 8 grayscale digit images."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

IMAGE_SIZE = (8, 8)
FEATURE_COUNT = 64


def load_image_features(image_path: str | Path) -> np.ndarray:
    """Return one PNG as a normalized, row-major vector of 64 float values."""
    path = Path(image_path)
    with Image.open(path) as image:
        grayscale = image.convert("L")
        if grayscale.size != IMAGE_SIZE:
            raise ValueError(f"Expected an 8 x 8 PNG, got {grayscale.size} for {path}")
        features = np.asarray(grayscale, dtype=np.float32).reshape(-1) / 255.0
    if features.shape != (FEATURE_COUNT,):
        raise ValueError(f"Expected {FEATURE_COUNT} features, got {features.shape}")
    return features


def load_dataset(csv_path: str | Path, data_dir: str | Path | None = None) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Load a labelled CSV split and its image features.

    ``image_path`` entries are resolved relative to ``data_dir``; by default this
    is the directory containing the CSV file.
    """
    csv_path = Path(csv_path)
    root = Path(data_dir) if data_dir is not None else csv_path.parent
    frame = pd.read_csv(csv_path)
    required = {"image_id", "image_path", "label"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")
    features = np.stack([load_image_features(root / relative_path) for relative_path in frame["image_path"]])
    labels = frame["label"].to_numpy(dtype=np.int64)
    return features, labels, frame
