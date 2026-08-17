import os

import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "models")

CATEGORY_MODEL_PATH = os.path.join(MODEL_DIR, "category_model.joblib")
PRIORITY_MODEL_PATH = os.path.join(MODEL_DIR, "priority_model.joblib")

_models = {}


def _load(path, key):
    if key not in _models:
        _models[key] = joblib.load(path) if os.path.exists(path) else None
    return _models[key]


def is_ready() -> bool:
    return (_load(CATEGORY_MODEL_PATH, "category") is not None
            and _load(PRIORITY_MODEL_PATH, "priority") is not None)


def _predict_with_confidence(model, text):
    label = model.predict([text])[0]

    if hasattr(model, "predict_proba"):
        confidence = float(model.predict_proba([text])[0].max())
    else:
        scores = model.decision_function([text])[0]
        exp_scores = np.exp(scores - np.max(scores))
        confidence = float((exp_scores / exp_scores.sum()).max())

    return label, round(confidence, 3)


def classify(title: str, description: str) -> dict:
    category_model = _load(CATEGORY_MODEL_PATH, "category")
    priority_model = _load(PRIORITY_MODEL_PATH, "priority")

    empty = {"category": None, "priority": None,
             "category_confidence": None, "priority_confidence": None}

    if category_model is None or priority_model is None:
        return empty

    text = f"{title} {description}".strip()
    if not text:
        return empty

    category, category_confidence = _predict_with_confidence(category_model, text)
    priority, priority_confidence = _predict_with_confidence(priority_model, text)

    return {
        "category": category,
        "priority": priority,
        "category_confidence": category_confidence,
        "priority_confidence": priority_confidence,
    }
