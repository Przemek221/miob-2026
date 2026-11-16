"""Testy ekstrakcji cech (bramka E3).

Cechy muszą być deterministyczne, bezstanowe i liczone wyłącznie z ``text``.
Przykłady są ręcznie przygotowane — testy nie zależą od zawartości `data/`.
"""

from __future__ import annotations

import math

import pytest

from src import features


SAMPLE = """Subject: Re: CHEAP VIAGRA!!! Buy now for $14.95

Hello, click here -> http://example.com:8080/buy?x=1 and http://1.2.3.4/offer
Mail: sales@example.com
> quoted line
> > deeper quote
From: someone@example.com
Date: Mon, 1 Jan 2003

WIN a free prize, guaranteed! Limited offer, 100% free.
Call 1234567890 or write to unsubscribe@example.com
"""


def test_extract_returns_only_floats() -> None:
    result = features.extract(SAMPLE)
    assert result
    assert all(isinstance(value, float) for value in result.values())
    assert all(math.isfinite(value) for value in result.values())


def test_extract_is_deterministic_and_stateless() -> None:
    first = features.extract(SAMPLE)
    second = features.extract(SAMPLE)
    assert first == second
    # inna wiadomość nie zmienia wyniku poprzedniej
    features.extract("Subject: x\n\nother")
    assert features.extract(SAMPLE) == first


def test_empty_text_is_safe() -> None:
    result = features.extract("")
    assert all(value == 0.0 for value in result.values()), result


def test_feature_names_are_stable() -> None:
    assert features.feature_names() == sorted(features.extract("Subject: a\n\nb").keys())


def test_subject_and_body_split() -> None:
    subject, body = features.split_subject_body("Subject: Hello\n\nWorld")
    assert subject == "Subject: Hello"
    assert body == "\nWorld"


def test_subject_split_without_subject_line() -> None:
    subject, body = features.split_subject_body("just body")
    assert subject == ""
    assert body == "just body"


def test_structural_features() -> None:
    result = features.extract(SAMPLE)
    assert result["n_quoted_lines"] == 2.0
    assert result["n_header_lines"] == 2.0  # From:, Date:
    assert result["n_empty_lines"] == 2.0
    assert result["quote_depth_max"] == 2.0  # linia "> > deeper quote"
    assert result["has_thread_prefix"] == 1.0  # temat zaczyna się od "Re:"
    assert result["n_chars"] == float(len(SAMPLE))


def test_quote_depth_counts_nested_quotes() -> None:
    result = features.extract("Subject: x\n\n> one\n>> two\n> > three")
    assert result["n_quoted_lines"] == 3.0
    assert result["quote_depth_max"] == 2.0


def test_url_and_email_features() -> None:
    result = features.extract(SAMPLE)
    assert result["n_urls"] == 2.0
    assert result["n_unique_domains"] == 2.0
    assert result["n_ip_urls"] == 1.0
    assert result["n_port_urls"] == 1.0
    assert result["n_emails"] == 3.0  # sales@, someone@, unsubscribe@


def test_style_features() -> None:
    result = features.extract(SAMPLE)
    assert result["n_exclamations"] >= 3.0
    assert result["n_exclam_repeats"] == 1.0  # "!!!"
    assert 0.0 < result["caps_ratio"] <= 1.0
    assert result["n_allcaps_words"] == 3.0  # CHEAP, VIAGRA, WIN
    assert result["n_dollars"] == 1.0
    assert result["n_percents"] == 1.0


def test_offer_features() -> None:
    result = features.extract(SAMPLE)
    # viagra, buy, win, free, prize, guaranteed, limited, offer, unsubscribe
    assert result["n_offer_words"] >= 8.0


def test_money_features() -> None:
    result = features.extract(SAMPLE)
    assert result["n_currency_amounts"] >= 1.0
    assert result["n_price_patterns"] >= 1.0


def test_plain_message_has_no_spam_markers() -> None:
    result = features.extract("Subject: lunch\n\nSee you at noon, no links here.")
    assert result["n_urls"] == 0.0
    assert result["n_emails"] == 0.0
    assert result["n_offer_words"] == 0.0
    assert result["n_currency_amounts"] == 0.0
    assert result["n_exclamations"] == 0.0


@pytest.mark.parametrize(
    "forbidden",
    ["label", "message_id", "source", "member", "split", "raw_sha256", "body_sha256"],
)
def test_features_do_not_encode_metadata(forbidden: str) -> None:
    assert forbidden not in features.feature_names()


def test_features_do_not_encode_corpus_artifacts() -> None:
    """Tagi listy i domeny korpusu nie są cechami (artefakt zbioru, nie sygnał)."""
    names = features.feature_names()
    assert not any("ilug" in name for name in names)
    assert not any("taint" in name for name in names)
    assert not any("spamassassin" in name for name in names)


def test_message_features_transformer_shape_and_names() -> None:
    transformer = features.MessageFeatures().fit(["Subject: a\n\nb", "Subject: c\n\nd"])
    matrix = transformer.transform(["Subject: a\n\nb", "Subject: c\n\nd"])
    assert matrix.shape == (2, len(features.FEATURE_NAMES))
    assert list(transformer.get_feature_names_out()) == list(features.FEATURE_NAMES)


def test_message_features_is_stateless() -> None:
    """``fit`` nie uczy się z danych — dwie różne ramki dają tę samą transformację."""
    texts = ["Subject: a\n\nb"]
    first = features.MessageFeatures().fit(texts).transform(texts).toarray()
    second = features.MessageFeatures().fit(["Subject: z\n\nzzz"]).transform(texts).toarray()
    assert (first == second).all()


def test_message_features_values_match_extract() -> None:
    texts = ["Subject: win $100 now!!!\n\nClick http://1.2.3.4/"]
    matrix = features.MessageFeatures().fit_transform(texts).toarray()[0]
    row = features.extract(texts[0])
    expected = [row[name] for name in features.FEATURE_NAMES]
    assert list(matrix) == expected


def test_feature_names_have_no_metadata() -> None:
    from src.data import FORBIDDEN_FEATURE_COLUMNS

    assert not (set(features.FEATURE_NAMES) & FORBIDDEN_FEATURE_COLUMNS)
