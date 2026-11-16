"""Cechy inżynieryjne wyliczane z pojedynczej wiadomości.

Kontrakt (plan.md, sekcja 4):

    features.extract(text: str) -> dict[str, float]

Funkcja jest deterministyczna, bezstanowa i nie wykonuje I/O — te same dane
wejściowe zawsze dają ten sam słownik. Dzięki temu da się ją testować na
ręcznie przygotowanych przykładach i bezpiecznie użyć w ``FeatureUnion``.

Świadomie **nie** ma tu cech kodujących artefakty korpusu (tagi listy ``[ILUG]``,
domeny ``spamassassin``/``taint.org``) ani żadnych metadanych pochodzenia —
to prowadziłoby do przecieku etykiety (plan.md, sekcje 2 i 6.6).
"""

from __future__ import annotations

import re

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin

URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
HOST_RE = re.compile(r"(?:https?://)?(?:www\.)?([^\s/:?#\"'<>)\]]+)", re.IGNORECASE)
IP_HOST_RE = re.compile(r"https?://\d{1,3}(?:\.\d{1,3}){3}", re.IGNORECASE)
PORT_RE = re.compile(r"https?://[^\s/:]+:\d{1,5}", re.IGNORECASE)
HEADER_LINE_RE = re.compile(
    r"^(?:From|To|Cc|Bcc|Date|Reply-To|Sender|Return-Path|Received|Message-ID|"
    r"MIME-Version|Content-Type|Content-Transfer-Encoding|X-[A-Za-z-]+):",
    re.IGNORECASE,
)
ALLCAPS_WORD_RE = re.compile(r"\b[A-Z]{2,}\b")
DIGIT_RUN_RE = re.compile(r"\d{7,}")
CURRENCY_RE = re.compile(r"(?:[$€£]\s?\d+(?:[.,]\d{1,2})?|\b\d+(?:[.,]\d{2})?\s?(?:USD|EUR|PLN)\b)", re.IGNORECASE)
PRICE_RE = re.compile(r"\b\d+[.,]\d{2}\b")
THREAD_PREFIX_RE = re.compile(r"^(?:re|fw|fwd|aw|odp)\s*:", re.IGNORECASE)

OFFER_WORDS = frozenset(
    {
        "free",
        "win",
        "winner",
        "prize",
        "guarantee",
        "guaranteed",
        "limited",
        "offer",
        "discount",
        "loan",
        "mortgage",
        "viagra",
        "casino",
        "porn",
        "credit",
        "cheap",
        "buy",
        "sale",
        "unsubscribe",
        "opt-out",
        "click",
    }
)


def split_subject_body(text: str) -> tuple[str, str]:
    """Dzieli wiadomość na temat (pierwsza linia ``Subject:``) i resztę treści."""
    if not text:
        return "", ""
    lines = text.splitlines()
    if lines and lines[0].lower().startswith("subject:"):
        return lines[0], "\n".join(lines[1:])
    return "", text


def subject_value(subject_line: str) -> str:
    """Zwraca samą wartość tematu, bez prefiksu ``Subject:``."""
    return re.sub(r"^subject:\s*", "", subject_line or "", flags=re.IGNORECASE).strip()


def _quote_depth(line: str) -> int:
    """Liczba poziomów cytowania (``>``) na początku linii, z pominięciem spacji."""
    return re.match(r"^[>\s]*", line).group(0).count(">")


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text)


def _domain(url: str) -> str:
    match = HOST_RE.match(url)
    return match.group(1).lower() if match else ""


def extract(text: str) -> dict[str, float]:
    """Zwraca cechy liczbowe wiadomości (wszystkie wartości typu ``float``)."""
    text = text or ""
    subject, body = split_subject_body(text)
    subject_text = subject_value(subject)
    words = _words(text)
    lines = [line for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line.strip()]
    urls = URL_RE.findall(text)
    domains = {_domain(url) for url in urls if _domain(url)}
    tlds = {domain.rsplit(".", 1)[-1] for domain in domains if "." in domain}
    lowered_words = [word.lower() for word in words]

    n_words = len(words)
    n_chars = len(text)
    n_paragraphs = len([block for block in re.split(r"\n\s*\n", text) if block.strip()])

    features = {
        # 6.1 struktura i podział
        "n_chars": float(n_chars),
        "n_words": float(n_words),
        "n_lines": float(len(lines)),
        "n_nonempty_lines": float(len(non_empty_lines)),
        "n_paragraphs": float(n_paragraphs),
        "n_empty_lines": float(len(lines) - len(non_empty_lines)),
        "n_quoted_lines": float(sum(1 for line in lines if line.lstrip().startswith(">"))),
        "n_header_lines": float(sum(1 for line in lines if HEADER_LINE_RE.match(line))),
        "quote_depth_max": float(max((_quote_depth(line) for line in lines), default=0)),
        "has_signature": float(any(line.strip() == "--" or line.strip() == "-- " for line in lines)),
        "has_thread_prefix": float(bool(THREAD_PREFIX_RE.match(subject_text))),
        "subject_len": float(len(subject)),
        "body_len": float(len(body)),
        "subject_upper_ratio": _upper_ratio(subject_text),
        # 6.2 styl i "nachalność"
        "caps_ratio": _upper_ratio(text),
        "n_allcaps_words": float(len(ALLCAPS_WORD_RE.findall(text))),
        "allcaps_word_ratio": float(len(ALLCAPS_WORD_RE.findall(text)) / n_words) if n_words else 0.0,
        "n_exclamations": float(text.count("!")),
        "n_questions": float(text.count("?")),
        "n_dollars": float(text.count("$")),
        "n_percents": float(text.count("%")),
        "n_stars": float(text.count("*")),
        "n_hashes": float(text.count("#")),
        "n_exclam_repeats": float(len(re.findall(r"!{2,}", text))),
        "n_question_repeats": float(len(re.findall(r"\?{2,}", text))),
        "digit_ratio": _digit_ratio(text),
        "nonalpha_ratio": float(len([c for c in text if not c.isalnum()]) / n_chars) if n_chars else 0.0,
        "nonascii_ratio": float(
            len([c for c in text if ord(c) > 127]) / n_chars
        )
        if n_chars
        else 0.0,
        "exclamations_per_100_words": float(text.count("!") * 100.0 / n_words) if n_words else 0.0,
        "n_numbers_in_subject": float(len(re.findall(r"\d+", subject))),
        # 6.3 linki i kontakt
        "n_urls": float(len(urls)),
        "n_unique_domains": float(len(domains)),
        "n_tlds": float(len(tlds)),
        "n_ip_urls": float(len(IP_HOST_RE.findall(text))),
        "n_port_urls": float(len(PORT_RE.findall(text))),
        "max_url_len": float(max((len(url) for url in urls), default=0)),
        "n_emails": float(len(EMAIL_RE.findall(text))),
        "has_mailto": float("mailto:" in text.lower()),
        "has_unsubscribe": float("unsubscribe" in text.lower() or "opt-out" in text.lower()),
        "has_click_here": float("click here" in text.lower()),
        "n_long_digit_runs": float(len(DIGIT_RUN_RE.findall(text))),
        # 6.4 pieniądze i oferta
        "n_currency_amounts": float(len(CURRENCY_RE.findall(text))),
        "n_price_patterns": float(len(PRICE_RE.findall(text))),
        "n_offer_words": float(sum(1 for word in lowered_words if word in OFFER_WORDS)),
        "offer_word_ratio": float(
            sum(1 for word in lowered_words if word in OFFER_WORDS) / n_words
        )
        if n_words
        else 0.0,
    }

    # Sanity check: kontrakt mówi o dict[str, float] bez NaN/inf.
    for name, value in features.items():
        if not isinstance(value, float):
            raise TypeError(f"cecha {name!r} nie jest float: {type(value)!r}")
    return features


def _upper_ratio(text: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    return float(sum(1 for char in letters if char.isupper()) / len(letters))


def _digit_ratio(text: str) -> float:
    if not text:
        return 0.0
    return float(sum(1 for char in text if char.isdigit()) / len(text))


def feature_names() -> list[str]:
    """Nazwy cech w stabilnej kolejności (na ręcznie przygotowanym przykładzie)."""
    return sorted(extract("Subject: sample\n\nBody text 123.").keys())


#: Stabilna, zamrożona lista nazw cech (kolejność kolumn macierzy).
FEATURE_NAMES: tuple[str, ...] = tuple(feature_names())


class MessageFeatures(TransformerMixin, BaseEstimator):
    """Transformer sklearn: ``text`` -> macierz cech inżynieryjnych.

    Nie uczy się niczego z danych (``fit`` tylko ustala nazwy kolumn), więc
    użycie go w pipeline nie przenosi informacji z validation do treningu.
    """

    def __init__(self, names: tuple[str, ...] | None = None) -> None:
        self.names = names

    def fit(self, X, y=None) -> "MessageFeatures":
        self.feature_names_ = list(self.names) if self.names is not None else list(FEATURE_NAMES)
        return self

    def transform(self, X):
        names = getattr(self, "feature_names_", list(FEATURE_NAMES))
        rows = [extract(text) for text in X]
        matrix = np.asarray([[row[name] for name in names] for row in rows], dtype=np.float64)
        if matrix.ndim == 1:  # pojedynczy wiersz
            matrix = matrix.reshape(1, -1)
        return csr_matrix(matrix)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(getattr(self, "feature_names_", list(FEATURE_NAMES)), dtype=object)



def extract_many(texts: list[str]) -> list[dict[str, float]]:
    """Wygodny wrapper dla listy wiadomości (np. w ``FeatureUnion``)."""
    return [extract(text) for text in texts]
