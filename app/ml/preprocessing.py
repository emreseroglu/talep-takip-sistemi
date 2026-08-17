import re


def normalize_text(text: str) -> str:
    text = str(text)

    text = text.replace("I", "ı").replace("İ", "i")
    text = text.lower()

    text = re.sub(r"[^a-zçğıöşü\s]", " ", text)

    return re.sub(r"\s+", " ", text).strip()
