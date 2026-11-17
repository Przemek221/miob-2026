"""Final, one-shot evaluation on the held-out test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from sklearn.metrics import accuracy_score, confusion_matrix

from src.data import load_dataset

LABELS = list(range(10))


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def _save_confusion_matrix_png(matrix: np.ndarray, path: Path) -> None:
    """Draw a readable 10 x 10 confusion matrix without extra dependencies."""
    cell = 52
    margin = 64
    size = margin + cell * len(LABELS)
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    font = _font(16)
    small = _font(11)
    largest = max(int(matrix.max()), 1)
    for row in range(len(LABELS)):
        for column in range(len(LABELS)):
            value = int(matrix[row, column])
            shade = 255 - int(190 * value / largest)
            box = (margin + column * cell, margin + row * cell, margin + (column + 1) * cell, margin + (row + 1) * cell)
            draw.rectangle(box, fill=(shade, shade, 255), outline=(120, 120, 120))
            if value:
                text = str(value)
                text_box = draw.textbbox((0, 0), text, font=font)
                text_width = text_box[2] - text_box[0]
                text_height = text_box[3] - text_box[1]
                draw.text(
                    (box[0] + (cell - text_width) / 2, box[1] + (cell - text_height) / 2 - 2),
                    text,
                    fill="black",
                    font=font,
                )
    for index, label in enumerate(LABELS):
        draw.text((margin + index * cell + cell / 2 - 4, margin - 24), str(label), fill="black", font=font)
        draw.text((margin - 28, margin + index * cell + cell / 2 - 9), str(label), fill="black", font=font)
    draw.text((margin, size - 30), "predicted digit", fill="black", font=small)
    draw.text((4, margin - 48), "true digit", fill="black", font=small)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def _save_misclassified_examples_png(
    frame: pd.DataFrame,
    y_true: np.ndarray,
    predicted: np.ndarray,
    data_dir: Path,
    path: Path,
    max_examples: int = 10,
) -> int:
    """Save a montage of wrongly classified PNGs, with true/predicted captions."""
    indices = np.flatnonzero(y_true != predicted)[:max_examples]
    if len(indices) == 0:
        return 0
    scale = 8
    cell = 8 * scale
    caption = 48
    columns = min(5, len(indices))
    rows = int(np.ceil(len(indices) / columns))
    image = Image.new("RGB", (columns * cell + 16, rows * (cell + caption) + 16), "white")
    draw = ImageDraw.Draw(image)
    font = _font(14)
    for position, index in enumerate(indices):
        row, column = divmod(position, columns)
        x = 8 + column * cell
        y = 8 + row * (cell + caption)
        with Image.open(data_dir / frame.iloc[index]["image_path"]) as source:
            digit = source.convert("L").resize((cell, cell), Image.Resampling.NEAREST).convert("RGB")
        image.paste(digit, (x, y))
        draw.text((x, y + cell + 4), f"true {int(y_true[index])}", fill="black", font=font)
        draw.text((x, y + cell + 22), f"pred {int(predicted[index])}", fill="#b00020", font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return len(indices)


def _metrics_markdown(metrics: dict[str, object], predictions_file: str) -> str:
    matrix = metrics["confusion_matrix"]
    lines = [
        "# Metryki końcowej oceny na `data/test.csv`",
        "",
        f"- Model: `{metrics['model_name']}`",
        f"- Trafienia: {metrics['correct']}",
        f"- Pomyłki: {metrics['incorrect']}",
        f"- Accuracy: {metrics['accuracy']:.4f}",
        f"- Predykcje: `{predictions_file}`",
        "",
        "## Macierz pomyłek",
        "",
        "Wiersze: prawdziwa cyfra; kolumny: przewidziana cyfra.",
        "",
        "| true \\ pred | " + " | ".join(str(label) for label in LABELS) + " |",
        "|---:|" + "---:|" * len(LABELS),
    ]
    for label, row in zip(LABELS, matrix):
        lines.append(f"| {label} | " + " | ".join(str(int(value)) for value in row) + " |")
    lines.extend(["", "## Najczęściej mylone pary", ""])
    confusions = metrics["most_common_confusions"]
    if confusions:
        lines.extend(["| prawdziwa | przewidziana | liczba |", "|---:|---:|---:|"])
        lines.extend(f"| {item['true']} | {item['predicted']} | {item['count']} |" for item in confusions)
    else:
        lines.append("Brak pomyłek.")
    lines.extend(["", "Wizualizacje: `artifacts/confusion_matrix.png` i `artifacts/misclassified_examples.png`.", ""])
    return "\n".join(lines)


def evaluate(
    model_path: str | Path,
    test_csv: str | Path,
    predictions_path: str | Path,
    metrics_path: str | Path,
    confusion_png: str | Path = "artifacts/confusion_matrix.png",
    examples_png: str | Path = "artifacts/misclassified_examples.png",
    metrics_md: str | Path = "artifacts/test_metrics.md",
) -> dict[str, object]:
    """Evaluate the saved model, write predictions, metrics and error visualisations."""
    bundle = joblib.load(model_path)
    test_csv = Path(test_csv)
    x_test, y_test, frame = load_dataset(test_csv)
    predicted = bundle["model"].predict(x_test).astype(int)
    output = pd.DataFrame(
        {
            "image_id": frame["image_id"],
            "image_path": frame["image_path"],
            "prediction": predicted,
            "true_label": y_test,
            "correct": y_test == predicted,
        }
    )
    predictions_path = Path(predictions_path)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(predictions_path, index=False)
    matrix = confusion_matrix(y_test, predicted, labels=LABELS)
    mistakes = [
        {"true": int(actual), "predicted": int(prediction), "count": int(count)}
        for (actual, prediction), count in np.ndenumerate(matrix)
        if actual != prediction and count > 0
    ]
    mistakes.sort(key=lambda item: (-item["count"], item["true"], item["predicted"]))
    metrics: dict[str, object] = {
        "model_name": bundle.get("model_name"),
        "accuracy": float(accuracy_score(y_test, predicted)),
        "correct": int((y_test == predicted).sum()),
        "incorrect": int((y_test != predicted).sum()),
        "confusion_matrix": matrix.tolist(),
        "most_common_confusions": mistakes,
        "misclassified_examples": _save_misclassified_examples_png(
            frame, y_test, predicted, test_csv.parent, Path(examples_png)
        ),
    }
    metrics_path = Path(metrics_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _save_confusion_matrix_png(matrix, Path(confusion_png))
    metrics_md = Path(metrics_md)
    metrics_md.parent.mkdir(parents=True, exist_ok=True)
    metrics_md.write_text(_metrics_markdown(metrics, str(predictions_path)), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="models/digit_classifier.joblib")
    parser.add_argument("--test", default="data/test.csv")
    parser.add_argument("--predictions", default="artifacts/test_predictions.csv")
    parser.add_argument("--metrics", default="artifacts/test_metrics.json")
    parser.add_argument("--confusion-png", default="artifacts/confusion_matrix.png")
    parser.add_argument("--examples-png", default="artifacts/misclassified_examples.png")
    parser.add_argument("--metrics-md", default="artifacts/test_metrics.md")
    args = parser.parse_args()
    metrics = evaluate(
        args.model, args.test, args.predictions, args.metrics, args.confusion_png, args.examples_png, args.metrics_md
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
