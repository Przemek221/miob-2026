"""Small fixed examples; no required model-quality score."""
import unittest
from components import FEATURES, counts, matrix, score_predictions


class ExperimentTest(unittest.TestCase):
    def test_two_error_types(self):
        self.assertEqual(counts([0, 0, 1, 1], [0, 1, 0, 1]),
                         {"n": 4, "tp": 1, "tn": 1, "fp": 1, "fn": 1, "errors": 2})

    def test_label_and_id_are_not_features(self):
        row = {name: i for i, name in enumerate(FEATURES)}
        row.update(label="spam", message_id="reveals-spam", text="spam")
        self.assertEqual(matrix([row]).tolist(), [[0, 1, 2, 3, 4, 5]])
        row.update(label="ham", message_id="different", text="different")
        self.assertEqual(matrix([row]).tolist(), [[0, 1, 2, 3, 4, 5]])

    def test_reference_labels_are_joined_by_id(self):
        predictions = [{"message_id": "b", "prediction": "spam"}, {"message_id": "a", "prediction": "ham"}]
        references = [{"message_id": "a", "label": "spam"}, {"message_id": "b", "label": "ham"}]
        self.assertEqual(score_predictions(predictions, references),
                         {"n": 2, "tp": 0, "tn": 0, "fp": 1, "fn": 1, "errors": 2})
        with self.assertRaisesRegex(ValueError, "different messages"):
            score_predictions(predictions, [{"message_id": "c", "label": "ham"}])


if __name__ == "__main__":
    unittest.main()
