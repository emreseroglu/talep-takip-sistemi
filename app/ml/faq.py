import json
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ml.preprocessing import normalize_text

FAQ_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "faq.json",
)

SIMILARITY_THRESHOLD = 0.30

MAX_RESULTS = 3


class FaqMatcher:
    def __init__(self, faq_file: str = FAQ_FILE):
        with open(faq_file, encoding="utf-8") as f:
            self.entries = json.load(f)

        documents = [
            entry["question"] + " " + " ".join(entry.get("keywords", []))
            for entry in self.entries
        ]

        self.vectorizer = TfidfVectorizer(
            preprocessor=normalize_text,
            analyzer="char_wb",
            ngram_range=(3, 5),
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(documents)

    def search(self, message: str, limit: int = MAX_RESULTS) -> list:
        message = (message or "").strip()
        if not message:
            return []

        if not normalize_text(message):
            return []

        scores = cosine_similarity(
            self.vectorizer.transform([message]), self.matrix
        )[0]

        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for index in ranked[:limit]:
            if scores[index] < SIMILARITY_THRESHOLD:
                break
            entry = self.entries[index]
            results.append({
                "id": entry["id"],
                "question": entry["question"],
                "answer": entry["answer"],
                "score": round(float(scores[index]), 3),
            })
        return results


_matcher = None


def get_matcher() -> FaqMatcher:
    global _matcher
    if _matcher is None:
        _matcher = FaqMatcher()
    return _matcher
