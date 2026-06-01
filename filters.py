import re

def normalize(text: str) -> str:
    text = text.lower()

    repl = {
        "@": "а",
        "0": "о",
        "3": "з",
        "4": "а",
        "1": "и"
    }

    for k, v in repl.items():
        text = text.replace(k, v)

    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "", text)

    return text


def contains_bad_word(text, bad_words):
    text = normalize(text)
    return any(word in text for word in bad_words)