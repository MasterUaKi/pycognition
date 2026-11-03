import re
from collections import Counter

_DEFAULT_STOP_WORDS = [
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'if',
    'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on', 'or', 'such', 'that',
    'the', 'their', 'then', 'there', 'these', 'they', 'this', 'to', 'was',
    'will', 'with'
]


def compute_word_frequency(text, stop_words=None, top_k=None):
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    if stop_words is None:
        stop_set = set(_DEFAULT_STOP_WORDS)
    else:
        if not isinstance(stop_words, (list, tuple)):
            raise TypeError('stop_words must be a list of strings')
        for w in stop_words:
            if not isinstance(w, str):
                raise TypeError('stop_words must contain only strings')
        stop_set = set(w.lower() for w in stop_words)
    if top_k is not None:
        if isinstance(top_k, bool) or not isinstance(top_k, int):
            raise TypeError('top_k must be an integer or None')
        if top_k < 0:
            raise ValueError('top_k must be non-negative')

    words = re.findall(r"[a-z0-9']+", text.lower())
    counts = Counter(w for w in words if w not in stop_set)

    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if top_k is not None:
        items = items[:top_k]
    return dict(items)
