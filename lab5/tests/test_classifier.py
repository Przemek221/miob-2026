from pathlib import Path

from src.predict import predict_image
from src.train import train_and_select


ROOT = Path(__file__).resolve().parents[1]


def test_training_small_subset_saves_model(tmp_path):
    model_path = tmp_path / "model.joblib"
    results = train_and_select(
        ROOT / "data/train.csv", ROOT / "data/validation.csv", model_path, tmp_path / "results.csv", max_train_rows=100
    )
    assert model_path.is_file()
    assert not results.empty


def test_saved_model_predicts_digit_for_valid_png(tmp_path):
    model_path = tmp_path / "model.joblib"
    train_and_select(ROOT / "data/train.csv", ROOT / "data/validation.csv", model_path, tmp_path / "results.csv")
    image_path = ROOT / "data" / "images" / "digit-17a28342e8c0.png"
    assert 0 <= predict_image(model_path, image_path) <= 9
