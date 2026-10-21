#!/usr/bin/env python3
"""Donne aux icônes de distribution la couleur du personnage du thème.

Les 102 icônes sont un carré de couleur plate avec le logo de la distribution
en blanc (ou en noir pour les variantes `_black`) par-dessus. Elles étaient
toutes rouges dans les 68 thèmes, ce qui jure sur les thèmes qui ne sont pas
rouges : le bleu de Makoto, le vert de Phoebe, le violet de Noir.

Chaque pixel est un mélange fond -> logo. On retrouve ce facteur de mélange et
on recompose sur la couleur du personnage, ce qui garde l'anticrénelage intact.

La couleur du personnage est celle de sa barre de progression (`fg_color` dans
`theme.txt`), la même que celle de sa barre de sélection. Elle est assombrie ou
éclaircie si le logo n'y serait pas lisible : le gris clair de Koromaru ne donne
qu'un contraste de 1.4 avec un logo blanc.

Les icônes sont réécrites en PNG indexé. Un dégradé entre deux couleurs ne
contient jamais plus de 256 teintes, donc la palette est sans perte, et le jeu
d'icônes passe de 37 Mo à environ 14 Mo : moins lourd dans le dépôt, et plus
rapide à charger au démarrage.

Usage:
    python3 tools/recolor_icons.py --all
    python3 tools/recolor_icons.py --theme persona3_reload/makoto
    python3 tools/recolor_icons.py --game persona5_phantom_x
    python3 tools/recolor_icons.py --all --dry-run
    python3 tools/recolor_icons.py --check      # pour la CI
"""
import argparse

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from check_contrast import (contrast, hex_to_rgb, luminance,  # noqa: E402
                            read_value, rgb_to_hex, selection_color)

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")

# Contraste minimum entre le logo et le fond de l'icône. 3.0 est le seuil des
# éléments non textuels (WCAG 1.4.11), ce que sont des logos de 48 px.
MIN_ICON = 3.0

# Une couleur ne couvrant pas au moins 0.5 % de l'icône est de l'anticrénelage,
# pas le logo.
LOGO_MIN_SHARE = 0.005


# --- LECTURE DE L'ICÔNE ---
def analyse(im):
    """Couleurs (fond, logo) d'une icône : un carré plat et un logo par-dessus"""
    counts = im.convert("RGB").getcolors(maxcolors=im.size[0] * im.size[1])
    bg = max(counts)[1]
    total = sum(n for n, _ in counts)
    common = [c for n, c in counts if n >= total * LOGO_MIN_SHARE]
    if len(common) < 2:
        return bg, (255, 255, 255)
    logo = max(common, key=lambda c: sum((c[i] - bg[i]) ** 2 for i in range(3)))
    return bg, logo


def blend_mask(im, bg, logo):
    """Part du logo dans chaque pixel, de 0 (fond) à 255 (logo plein)"""
    vec = [logo[i] - bg[i] for i in range(3)]
    denom = sum(v * v for v in vec)
    mask = Image.new("L", im.size)
    if denom == 0:
        return mask
    src = im.convert("RGB").load()
    out = mask.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            pixel = src[x, y]
            t = sum((pixel[i] - bg[i]) * vec[i] for i in range(3)) / denom
            out[x, y] = 0 if t < 0 else (255 if t > 1 else round(t * 255))
    return mask


# --- COULEUR DU PERSONNAGE ---
def theme_accent(theme_dir):
    """Couleur du personnage : sa barre de progression, sinon sa barre de sélection"""
    with open(os.path.join(theme_dir, "theme.txt"), encoding="utf-8") as f:
        value = read_value(f.read(), "fg_color")
    if value and value.startswith("#"):
        return hex_to_rgb(value)
    return selection_color(theme_dir)


def fit_contrast(bg, logo, minimum=MIN_ICON):
    """Assombrit ou éclaircit le fond jusqu'à ce que le logo soit lisible dessus"""
    if contrast(bg, logo) >= minimum:
        return bg
    # Vers le noir si le logo est clair, vers le blanc s'il est sombre. On se
    # fie à la luminance du logo seul : la comparer à celle du fond échoue
    # quand les deux sont égales, et on repart alors vers le blanc sous un logo
    # blanc, ce qui n'arrange rien.
    target = (0, 0, 0) if luminance(logo) > 0.5 else (255, 255, 255)
    best = bg
    for step in range(1, 101):
        factor = step / 100
        candidate = tuple(round(bg[i] + (target[i] - bg[i]) * factor) for i in range(3))
        best = candidate
        if contrast(candidate, logo) >= minimum:
            break
    return best


# --- ÉCRITURE ---
def save_icon(im, path, dry_run=False):
    """Écrit l'icône en PNG indexé, ou en RGB si elle a plus de 256 teintes"""
    colors = im.getcolors(maxcolors=257)
    if colors is not None and len(colors) <= 256:
        im = im.convert("P", palette=Image.ADAPTIVE, colors=len(colors),
                        dither=Image.Dither.NONE)
    if not dry_run:
        im.save(path, "PNG", optimize=True)
    return im


def recolor_theme(theme_dir, dry_run=False, cache=None):
    """Recolore les icônes d'un thème. Retourne (nombre, octets avant, après)"""
    icons_dir = os.path.join(theme_dir, "icons")
    if not os.path.isdir(icons_dir):
        return 0, 0, 0
    accent = theme_accent(theme_dir)
    count = before = after = 0
    for name in sorted(os.listdir(icons_dir)):
        if not name.endswith(".png"):
            continue
        path = os.path.join(icons_dir, name)
        before += os.path.getsize(path)
        im = Image.open(path)
        bg, logo = analyse(im)

        key = (im.tobytes(), bg, logo)
        mask = cache.get(key) if cache is not None else None
        if mask is None:
            mask = blend_mask(im, bg, logo)
            if cache is not None:
                cache[key] = mask

        new_bg = fit_contrast(accent, logo)
        out = Image.composite(Image.new("RGB", im.size, logo),
                              Image.new("RGB", im.size, new_bg), mask)
        save_icon(out, path, dry_run)
        after += os.path.getsize(path) if not dry_run else 0
        count += 1
    return count, before, after


# --- VÉRIFICATION ---
def check_theme(theme_dir):
    """Problèmes du thème : icône hors couleur du personnage ou logo illisible"""
    icons_dir = os.path.join(theme_dir, "icons")
    if not os.path.isdir(icons_dir):
        return []
    accent = theme_accent(theme_dir)
    problems = []
    for name in sorted(os.listdir(icons_dir)):
        if not name.endswith(".png"):
            continue
        bg, logo = analyse(Image.open(os.path.join(icons_dir, name)))
        expected = fit_contrast(accent, logo)
        if max(abs(bg[i] - expected[i]) for i in range(3)) > 2:
            problems.append("%s : fond %s au lieu de %s"
                            % (name, rgb_to_hex(bg), rgb_to_hex(expected)))
        elif contrast(bg, logo) < MIN_ICON:
            problems.append("%s : contraste %.1f < %.1f"
                            % (name, contrast(bg, logo), MIN_ICON))
    return problems


# --- THÈMES ---
def find_themes(selector=None):
    themes = []
    for game in sorted(os.listdir(THEMES_DIR)):
        game_dir = os.path.join(THEMES_DIR, game)
        if not os.path.isdir(game_dir) or game.startswith("_"):
            continue
        for name in sorted(os.listdir(game_dir)):
            theme_dir = os.path.join(game_dir, name)
            if not os.path.isfile(os.path.join(theme_dir, "theme.txt")):
                continue
            key = "%s/%s" % (game, name)
            if selector is None or selector == key or selector == game:
                themes.append((key, theme_dir))
    return themes


def main():
    parser = argparse.ArgumentParser(
        description="Donne aux icônes la couleur du personnage du thème")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="tous les thèmes")
    group.add_argument("--theme", help="un thème (ex: persona3_reload/makoto)")
    group.add_argument("--game", help="un jeu (ex: persona5_phantom_x)")
    group.add_argument("--check", action="store_true",
                       help="vérifie sans rien écrire (code 1 si un thème cloche)")
    parser.add_argument("--dry-run", action="store_true",
                        help="affiche ce qui serait fait sans écrire")
    args = parser.parse_args()

    selector = args.theme or args.game
    themes = find_themes(selector)
    if not themes:
        print("Aucun thème trouvé pour %s" % selector)
        return 1

    if args.check:
        failed = 0
        for key, theme_dir in themes:
            problems = check_theme(theme_dir)
            if problems:
                failed += 1
                print("%s :" % key)
                for problem in problems[:5]:
                    print("   %s" % problem)
                if len(problems) > 5:
                    print("   ... et %d autres" % (len(problems) - 5))
        if failed:
            print("\n%d/%d thèmes à recolorer (tools/recolor_icons.py --all)"
                  % (failed, len(themes)))
            return 1
        print("%d/%d thèmes : icônes à la couleur du personnage, logos lisibles"
              % (len(themes), len(themes)))
        return 0

    cache = {}
    total = before = after = 0
    for key, theme_dir in themes:
        accent = theme_accent(theme_dir)
        count, size_before, size_after = recolor_theme(theme_dir, args.dry_run, cache)
        fitted = fit_contrast(accent, (255, 255, 255))
        note = "" if fitted == accent else " (assombri en %s)" % rgb_to_hex(fitted)
        print("%-40s %s%s  %d icônes" % (key, rgb_to_hex(accent), note, count))
        total += count
        before += size_before
        after += size_after

    print("\n%d icônes dans %d thèmes" % (total, len(themes)))
    if args.dry_run:
        print("DRY RUN : rien n'a été écrit")
    else:
        print("%.1f Mo -> %.1f Mo" % (before / 1048576, after / 1048576))
    return 0


if __name__ == "__main__":
    sys.exit(main())
