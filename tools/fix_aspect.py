#!/usr/bin/env python3
"""Empêche GRUB de déformer les illustrations.

Par défaut GRUB étire `desktop-image` jusqu'aux bords de l'écran. Les 14 fonds
qui ne sont pas en 16:9 sont donc déformés verticalement : le visage de Fuuka
est allongé, et c'est pareil pour les 12 thèmes P5X en 2.33:1. Et même un fond
en 16:9 est déformé sur un écran 16:10 ou ultra-large.

GRUB sait faire autrement : `desktop-image-scale-method: "padding"` met
l'image à l'échelle en gardant ses proportions et comble le reste avec
`desktop-color`. On prend cette couleur sur les bords de l'illustration, pour
que la bande se fonde dedans au lieu d'afficher du noir.

Usage :
    python3 tools/fix_aspect.py --all
    python3 tools/fix_aspect.py --all --dry-run
    python3 tools/fix_aspect.py --check      # pour la CI
"""
import argparse
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from check_contrast import luminance, rgb_to_hex  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")

SCALE_KEYS = ("desktop-image-scale-method", "desktop-image-h-align",
              "desktop-image-v-align", "desktop-color")


def edge_color(path, band=0.06):
    """Couleur médiane des bords haut et bas de l'illustration"""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    edge = max(1, int(h * band))
    strip = Image.new("RGB", (w, edge * 2))
    strip.paste(im.crop((0, 0, w, edge)), (0, 0))
    strip.paste(im.crop((0, h - edge, w, h)), (0, edge))
    data = strip.resize((48, 48)).tobytes()
    pixels = sorted((data[i:i + 3] for i in range(0, len(data), 3)), key=luminance)
    return tuple(pixels[len(pixels) // 2])


def block(color):
    return ('desktop-image-scale-method: "padding"\n'
            'desktop-image-h-align: "center"\n'
            'desktop-image-v-align: "center"\n'
            'desktop-color: "%s"\n' % rgb_to_hex(color))


def strip_keys(text):
    """Retire les lignes qu'on gère, pour pouvoir rejouer le script"""
    return "".join(line for line in text.splitlines(keepends=True)
                   if not line.strip().startswith(SCALE_KEYS))


def apply_theme(theme_dir, dry_run=False):
    theme_txt = os.path.join(theme_dir, "theme.txt")
    background = os.path.join(theme_dir, "background.png")
    if not (os.path.isfile(theme_txt) and os.path.isfile(background)):
        return None
    with open(theme_txt, encoding="utf-8") as f:
        text = f.read()
    color = edge_color(background)
    cleaned = strip_keys(text)
    marker = 'desktop-image: "background.png"\n'
    if marker not in cleaned:
        return None
    new = cleaned.replace(marker, marker + block(color), 1)
    if new != text and not dry_run:
        with open(theme_txt, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    return color, new != text


def find_themes():
    out = []
    for game in sorted(os.listdir(THEMES_DIR)):
        gdir = os.path.join(THEMES_DIR, game)
        if not os.path.isdir(gdir) or game.startswith("_"):
            continue
        for name in sorted(os.listdir(gdir)):
            tdir = os.path.join(gdir, name)
            if os.path.isfile(os.path.join(tdir, "theme.txt")):
                out.append(("%s/%s" % (game, name), tdir))
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Empêche GRUB de déformer les illustrations")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--check", action="store_true",
                       help="vérifie sans écrire (code 1 s'il en manque)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    themes = find_themes()

    if args.check:
        missing = []
        for key, tdir in themes:
            with open(os.path.join(tdir, "theme.txt"), encoding="utf-8") as f:
                text = f.read()
            if 'desktop-image-scale-method: "padding"' not in text:
                missing.append(key)
        if missing:
            print("%d thèmes étirés par GRUB :" % len(missing))
            for key in missing[:10]:
                print("   %s" % key)
            print("\nCorriger avec tools/fix_aspect.py --all")
            return 1
        print("%d/%d thèmes : GRUB garde les proportions de l'illustration"
              % (len(themes), len(themes)))
        return 0

    changed = 0
    for key, tdir in themes:
        result = apply_theme(tdir, args.dry_run)
        if result is None:
            print("%-40s pas de background.png" % key)
            continue
        color, did = result
        print("%-40s bande %s%s" % (key, rgb_to_hex(color), "" if did else "  (déjà à jour)"))
        changed += bool(did)

    print("\n%d thèmes sur %d mis à jour" % (changed, len(themes)))
    if args.dry_run:
        print("DRY RUN : rien n'a été écrit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
