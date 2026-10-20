#!/usr/bin/env python3
"""
Traductions de l'installeur : un fichier lang/<code>.json par langue.

Mêmes langues que personadle : anglais, français, allemand, espagnol, italien, portugais.
Les noms des Arcanes viennent de personadle. Les répliques officielles des jeux
(phrases des All-Out Attacks, « Looking cool, Joker! »…) restent telles qu'écrites.
"""
import json
import os

LANG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lang")
ORDER = ["en", "fr", "de", "es", "it", "pt"]
DEFAULT = "en"

current = DEFAULT
_strings = {}


def available():
    try:
        codes = {name[:-5] for name in os.listdir(LANG_DIR) if name.endswith(".json")}
    except OSError:
        codes = set()
    return [c for c in ORDER if c in codes] + sorted(codes - set(ORDER))


def _load(code):
    try:
        with open(os.path.join(LANG_DIR, f"{code}.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def set_language(code):
    """Change de langue. Les textes manquants retombent sur l'anglais."""
    global current, _strings
    code = (code or DEFAULT).lower()[:2]
    if code not in available():
        code = DEFAULT
    strings = _load(DEFAULT)
    if code != DEFAULT:
        for key, value in _load(code).items():
            if isinstance(value, dict):
                strings[key] = {**strings.get(key, {}), **value}
            else:
                strings[key] = value
    current, _strings = code, strings
    return code


def detect():
    """Langue du système (sudo garde en général LANG)"""
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if value and value not in ("C", "POSIX"):
            code = value.split(":")[0][:2].lower()
            if code in available():
                return code
    return DEFAULT


def t(key, **values):
    text = _strings.get(key, key)
    return text.format(**values) if values else text


def arcana(name):
    return _strings.get("arcana_names", {}).get(name, name)


def character(name):
    return _strings.get("character_names", {}).get(name, name)


def is_yes(answer):
    return answer.strip().lower() in _strings.get("yes_words", ["y", "yes"])


def language_name(code):
    return _load(code).get("language_name", code)


set_language(detect())
