#!/usr/bin/env python3
"""
Compare les All-Out Attacks officiels recensés dans personadle avec les thèmes du repo.

personadle (https://github.com/CodeByHaamza/personadle) liste dans
allOutAttackMode/database/aoaCharacters.js chaque personnage et tenue qui a un
All-Out Attack officiel. Chaque entrée sans thème ici est un thème à faire.

Usage :
    python3 tools/personadle_sync.py                 # lit la liste sur GitHub
    python3 tools/personadle_sync.py chemin/aoaCharacters.js
    python3 tools/personadle_sync.py --json          # sortie pour la GitHub Action

Aucune dépendance.
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")
PERSONADLE_URL = ("https://raw.githubusercontent.com/CodeByHaamza/personadle/main/"
                  "allOutAttackMode/database/aoaCharacters.js")
PERSONADLE_PAGE = "https://github.com/CodeByHaamza/personadle/tree/main/allOutAttackMode"

# Nom de fichier personadle -> dossier de thème, quand ils diffèrent
FOLDER_ALIASES = {
    "Yuki": "makoto",                 # Makoto Yuki (P3)
    "YukiX": "yuki",                  # Yuki (P5X)
    "Shinjiro": "shinji",
    "Mona": "morgana",
    "Caroline_and_Justine": "caroline_justine",
    "Wonder_ChineseNY": "wonder_cny",
    "Rin_ChineseNY": "rin_cny",
    "Wind_V": "wind_vast",
}

ENTRY = re.compile(r'\{\s*nom:\s*"([^"]+)",\s*gif:\s*"([^"]+)",\s*opus:\s*\[([^\]]*)\]')


def game_for(opus):
    """Dossier de jeu pour un nouveau thème : une tenue P5X va dans P5X, même pour un perso de P5"""
    if "P5X" in opus:
        return "persona5_phantom_x"
    if any(o.startswith("P3") for o in opus):
        return "persona3_reload"
    return "persona5_royal"


def load(source):
    if source.startswith("http"):
        with urllib.request.urlopen(source, timeout=30) as response:
            return response.read().decode("utf-8")
    with open(source, encoding="utf-8") as f:
        return f.read()


def parse(text):
    characters = []
    for name, gif, opus in ENTRY.findall(text):
        opus = re.findall(r'"([^"]+)"', opus)
        characters.append({
            "name": name,
            "gif": gif,
            "folder": FOLDER_ALIASES.get(gif, gif.lower()),
            "game": game_for(opus),
        })
    return characters


def existing_themes():
    return {os.path.basename(os.path.dirname(p))
            for p in glob.glob(os.path.join(THEMES_DIR, "*", "*", "theme.txt"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", default=PERSONADLE_URL, help="aoaCharacters.js (URL ou fichier)")
    parser.add_argument("--json", action="store_true", help="liste des thèmes manquants en JSON")
    args = parser.parse_args()

    characters = parse(load(args.source))
    if not characters:
        print("No character found in personadle: the file format may have changed.", file=sys.stderr)
        sys.exit(2)

    themes = existing_themes()
    missing = [c for c in characters if c["folder"] not in themes]
    known = {c["folder"] for c in characters}
    extra = sorted(themes - known)

    if args.json:
        print(json.dumps(missing))
        return

    print(f"personadle: {len(characters)} official All-Out Attacks, repo: {len(themes)} themes\n")
    print(f"Missing themes ({len(missing)}):")
    for c in missing:
        print(f"  {c['game']}/{c['folder']:20} {c['name']}")
    if extra:
        print(f"\nThemes not listed in personadle ({len(extra)}): {', '.join(extra)}")


if __name__ == "__main__":
    main()
