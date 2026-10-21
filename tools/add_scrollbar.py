#!/usr/bin/env python3
"""Donne à chaque thème une barre de défilement à la couleur du personnage.

Sans pixmaps, GRUB dessine sa barre de défilement par défaut dès qu'il y a plus
d'entrées que le menu n'en affiche : un rectangle gris qui n'a rien à voir avec
le thème. On génère donc deux jeux d'images à la couleur du personnage, le rail
et le curseur, comme pour les barres de sélection.

Les pixmaps sont découpés en 9 (centre, bords, coins), comme `select_*.png` et
`boot_menu_*.png` qui existent déjà.

Usage :
    python3 tools/add_scrollbar.py --all
    python3 tools/add_scrollbar.py --check      # pour la CI
"""
import argparse
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from check_contrast import rgb_to_hex  # noqa: E402
from recolor_icons import theme_accent  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")

SLICES = ("c", "n", "s", "e", "w", "nw", "ne", "sw", "se")
# Le rail est noir plutôt que teinté : un rail à la couleur du personnage
# disparaît sur une illustration de la même couleur, le rouge de Joker sur le
# rouge de son artwork par exemple. Du noir translucide marche sur les 78.
TRACK_COLOR = (0, 0, 0)
TRACK_ALPHA = 140
SCROLLBAR_WIDTH = 14

SETTINGS = """  scrollbar = true
  scrollbar_width = %d
  scrollbar_frame = "scrollbar_*.png"
  scrollbar_thumb = "slider_*.png"
  scrollbar_slice = "east"
""" % SCROLLBAR_WIDTH


def write_slices(theme_dir, prefix, color, alpha):
    # 1x1, comme boot_menu_c.png. Avec des tranches de 5x5, GRUB renonce à
    # dessiner la barre en dessous d'une soixantaine de pixels de large : les
    # coins ne tiennent pas. En 1x1 n'importe quelle largeur passe.
    for slice_name in SLICES:
        im = Image.new("RGBA", (1, 1), (color[0], color[1], color[2], alpha))
        im.save(os.path.join(theme_dir, "%s_%s.png" % (prefix, slice_name)),
                "PNG", optimize=True)


def strip_settings(text):
    """Retire les lignes qu'on gère, pour pouvoir rejouer le script"""
    keys = ("scrollbar", "scrollbar_width", "scrollbar_frame",
            "scrollbar_thumb", "scrollbar_slice")
    out = []
    for line in text.splitlines(keepends=True):
        name = line.strip().split("=")[0].strip()
        if name in keys:
            continue
        out.append(line)
    return "".join(out)


def apply_theme(theme_dir):
    theme_txt = os.path.join(theme_dir, "theme.txt")
    if not os.path.isfile(theme_txt):
        return None
    with open(theme_txt, encoding="utf-8") as f:
        text = f.read()

    accent = theme_accent(theme_dir)
    write_slices(theme_dir, "scrollbar", TRACK_COLOR, TRACK_ALPHA)
    write_slices(theme_dir, "slider", accent, 255)

    cleaned = strip_settings(text)
    marker = '  menu_pixmap_style = "boot_menu_*.png"\n'
    if marker not in cleaned:
        return None
    new = cleaned.replace(marker, marker + SETTINGS, 1)
    if new != text:
        with open(theme_txt, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    return accent


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
        description="Barre de défilement à la couleur du personnage")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    themes = find_themes()

    if args.check:
        missing = []
        for key, tdir in themes:
            with open(os.path.join(tdir, "theme.txt"), encoding="utf-8") as f:
                text = f.read()
            ok = 'scrollbar_thumb = "slider_*.png"' in text
            ok = ok and all(os.path.isfile(os.path.join(tdir, "%s_%s.png" % (p, s)))
                            for p in ("scrollbar", "slider") for s in SLICES)
            if not ok:
                missing.append(key)
        if missing:
            print("%d thèmes sans barre de défilement :" % len(missing))
            for key in missing[:10]:
                print("   %s" % key)
            print("\nCorriger avec tools/add_scrollbar.py --all")
            return 1
        print("%d/%d thèmes : barre de défilement à la couleur du personnage"
              % (len(themes), len(themes)))
        return 0

    done = 0
    for key, tdir in themes:
        accent = apply_theme(tdir)
        if accent is None:
            print("%-40s theme.txt inattendu" % key)
            continue
        print("%-40s %s" % (key, rgb_to_hex(accent)))
        done += 1
    print("\n%d thèmes sur %d" % (done, len(themes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
