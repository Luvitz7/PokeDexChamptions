import json
import os
from difflib import SequenceMatcher

import requests

from search import normalize_text

POKEMON_CACHE_PATH = os.path.join("data", "pokemon_names.json")
POKEMON_LIST_URL = "https://pokeapi.co/api/v2/pokemon?limit=2000&offset=0"

REGIONAL_FORM_PREFIX_ALIASES = {
    "alolan": "alola",
    "hisuian": "hisui",
    "galarian": "galar",
    "paldean": "paldea",
}

REGIONAL_FORMS = {"alola", "hisui", "galar", "paldea"}
MEGA_TOKENS = {"mega", "x", "y"}

_POKEMON_INDEX = None


def load_pokemon_names():
    if os.path.exists(POKEMON_CACHE_PATH):
        with open(POKEMON_CACHE_PATH, "r", encoding="utf-8") as file:
            cached = json.load(file)
            if isinstance(cached, list) and cached:
                return cached

    try:
        response = requests.get(POKEMON_LIST_URL, timeout=30)
        response.raise_for_status()
        payload = response.json()
        names = [entry["name"] for entry in payload.get("results", []) if entry.get("name")]

        if names:
            os.makedirs(os.path.dirname(POKEMON_CACHE_PATH), exist_ok=True)
            with open(POKEMON_CACHE_PATH, "w", encoding="utf-8") as file:
                json.dump(names, file, ensure_ascii=False, indent=2)

        return names
    except requests.exceptions.RequestException:
        return []


def get_pokemon_index():
    global _POKEMON_INDEX

    if _POKEMON_INDEX is None:
        names = load_pokemon_names()
        _POKEMON_INDEX = {normalize_text(name): name for name in names}

    return _POKEMON_INDEX


def build_candidate_queries(query):
    normalized = normalize_text(query)
    tokens = normalized.split()
    candidates = [normalized]

    if not tokens:
        return candidates

    first_token = tokens[0]
    last_token = tokens[-1]

    if first_token in REGIONAL_FORM_PREFIX_ALIASES and len(tokens) >= 2:
        form = REGIONAL_FORM_PREFIX_ALIASES[first_token]
        candidates.append(" ".join(tokens[1:] + [form]))

    if last_token in REGIONAL_FORMS and len(tokens) >= 2:
        candidates.append(" ".join(tokens[:-1] + [last_token]))

    if "mega" in tokens:
        remaining = [token for token in tokens if token not in MEGA_TOKENS]
        if remaining:
            if last_token in {"x", "y"}:
                candidates.append(" ".join(remaining + ["mega", last_token]))
            else:
                candidates.append(" ".join(remaining + ["mega"]))

    if first_token == "mega" and len(tokens) >= 2:
        remaining = tokens[1:]
        if remaining:
            if remaining[-1] in {"x", "y"}:
                candidates.append(" ".join(remaining[:-1] + ["mega", remaining[-1]]))
            else:
                candidates.append(" ".join(remaining + ["mega"]))

    unique_candidates = []
    seen = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique_candidates.append(candidate)

    return unique_candidates


def resolve_pokemon_query(query, *, cutoff=0.82, limit=3):
    index = get_pokemon_index()
    if not index:
        return normalize_text(query).replace(" ", "-"), []

    for candidate in build_candidate_queries(query):
        if candidate in index:
            return index[candidate], []

    normalized = normalize_text(query)
    scored = []

    for candidate_key, raw_name in index.items():
        if normalized in candidate_key or candidate_key in normalized:
            score = 0.98
        else:
            score = SequenceMatcher(None, normalized, candidate_key).ratio()

        if score >= cutoff:
            scored.append((score, raw_name))

    scored.sort(key=lambda entry: (-entry[0], entry[1]))

    suggestions = []
    seen = set()
    for _score, name in scored:
        if name in seen:
            continue

        seen.add(name)
        suggestions.append(name)

        if len(suggestions) >= limit:
            break

    return None, suggestions
