import re
import unicodedata
from difflib import SequenceMatcher


def normalize_text(text):
    if text is None:
        return ""

    normalized = str(text).strip().lower()
    normalized = unicodedata.normalize("NFD", normalized)
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    normalized = normalized.replace("`", "'").replace("´", "'").replace("’", "'")
    normalized = re.sub(r"[-_.]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def build_search_index(items):
    exact_index = {}
    candidates = []

    for item in items:
        name = item.get("name", "")
        key = normalize_text(name)

        if not key:
            continue

        exact_index[key] = item
        candidates.append((key, item))

    return exact_index, candidates


def search_with_suggestions(query, catalogs, *, cutoff=0.82, limit=3):
    normalized_query = normalize_text(query)
    if not normalized_query:
        return None, None, []

    for exact_index, _candidates, dictionary in catalogs:
        if normalized_query in exact_index:
            return exact_index[normalized_query], dictionary["dictionary"], []

    scored_suggestions = []
    seen = set()

    for _exact_index, candidates, dictionary in catalogs:
        for candidate_key, item in candidates:
            if normalized_query in candidate_key or candidate_key in normalized_query:
                score = 0.98
            else:
                score = SequenceMatcher(None, normalized_query, candidate_key).ratio()

            if score < cutoff:
                continue

            item_name = item.get("name", "")
            dedupe_key = (item_name, dictionary.get("language", ""))
            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)
            scored_suggestions.append((score, item, dictionary))

    scored_suggestions.sort(key=lambda entry: (-entry[0], entry[1].get("name", "")))

    suggestions = []
    suggestion_seen = set()
    for _score, item, dictionary in scored_suggestions:
        dedupe_key = (item.get("name", ""), dictionary.get("language", ""))
        if dedupe_key in suggestion_seen:
            continue

        suggestion_seen.add(dedupe_key)
        suggestions.append((item, dictionary["dictionary"]))

        if len(suggestions) >= limit:
            break

    return None, None, suggestions
