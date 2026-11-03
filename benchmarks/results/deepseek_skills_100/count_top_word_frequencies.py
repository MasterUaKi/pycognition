import re
from collections import Counter

_STOP_WORDS = frozenset({
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from',
    'has', 'have', 'he', 'her', 'his', 'i', 'in', 'is', 'it', 'its', 'me',
    'my', 'no', 'not', 'of', 'on', 'or', 'our', 'she', 'so', 'that', 'the',
    'their', 'them', 'they', 'this', 'to', 'was', 'we', 'were', 'will', 'with',
    'you', 'your'
})

_WORD_RE = re.compile(r"[a-z0-9]+")


def count_top_word_frequencies(text, top_k=3):
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise TypeError('top_k must be an integer')
    if top_k < 0:
        raise ValueError('top_k must be non-negative')

    words = _WORD_RE.findall(text.lower())
    filtered = [w for w in words if w not in _STOP_WORDS]
    counts = Counter(filtered)

    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{'word': word, 'count': count} for word, count in ordered[:top_k]]
