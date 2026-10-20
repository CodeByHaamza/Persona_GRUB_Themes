#!/usr/bin/env python3
"""Construit un thème complet à partir d'une illustration d'All-Out Attack.

Un thème, c'est l'illustration, les 102 icônes de distribution et les pixmaps
du menu, tous à la couleur du personnage. Ce script part d'un thème existant
comme gabarit, remplace l'illustration, et recolore le reste.

La couleur du personnage est prise sur l'illustration : la teinte vive qui
couvre le plus de surface, ce qui donne le rouge de Wonder, le vert de Phoebe,
le bleu de Makoto. Elle peut être imposée avec --accent.

Usage :
    python3 tools/new_theme.py --game persona5_phantom_x --name blitz \\
        --art blitz.png --from wonder
    python3 tools/new_theme.py --game persona5_phantom_x --name blitz \\
        --art blitz.png --from wonder --accent "#A0203C"

Ensuite :
    python3 tools/check_contrast.py --fix
    python3 tools/fix_aspect.py --all
    python3 tools/prev.py --theme <jeu>/<nom>
"""
import argparse
import colorsys
import os
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from check_contrast import hex_to_rgb, replace_value, rgb_to_hex  # noqa: E402
from recolor_icons import recolor_theme  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")

# fichiers repris tels quels du gabarit
TEMPLATE_FILES = ["dejavu_14.pf2", "dejavu_bold_14.pf2"] + \
    ["boot_menu_%s.png" % d for d in ("c", "n", "s", "e", "w", "ne", "nw", "se", "sw")]
SELECT_FILES = ["select_%s.png" % d for d in ("c", "n", "s", "e", "w", "ne", "nw", "se", "sw")]


def dominant_accent(path):
    """Teinte vive qui couvre le plus de surface dans l'illustration"""
    im = Image.open(path).convert("RGB").resize((160, 90))
    buckets = {}
    data = im.tobytes()
    for i in range(0, len(data), 3):
        r, g, b = data[i] / 255, data[i + 1] / 255, data[i + 2] / 255
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        # on ignore le gris, le presque noir et le presque blanc
        if s < 0.35 or v < 0.2 or v > 0.97:
            continue
        key = int(h * 18)  # 18 secteurs de teinte
        acc = buckets.setdefault(key, [0, 0.0, 0.0])
        acc[0] += 1
        acc[1] += s
        acc[2] += v
    if not buckets:
        return (128, 128, 128)
    key, (n, s_sum, v_sum) = max(buckets.items(), key=lambda kv: kv[1][0])
    h = (key + 0.5) / 18
    s = min(1.0, s_sum / n)
    v = min(1.0, v_sum / n)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (round(r * 255), round(g * 255), round(b * 255))


def recolor_select(src, dst, accent):
    """Les pixmaps de sélection : tout ce qui n'est pas noir prend la couleur"""
    im = Image.open(src).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not (r < 10 and g < 10 and b < 10):
                px[x, y] = (accent[0], accent[1], accent[2], a)
    im.save(dst, "PNG", optimize=True)


def build(game, name, art, template, accent=None, dry_run=False):
    tpl_dir = os.path.join(THEMES_DIR, game, template)
    if not os.path.isdir(tpl_dir):
        # le gabarit peut venir d'un autre jeu
        for other in os.listdir(THEMES_DIR):
            candidate = os.path.join(THEMES_DIR, other, template)
            if os.path.isdir(candidate):
                tpl_dir = candidate
                break
    if not os.path.isdir(tpl_dir):
        raise SystemExit("gabarit introuvable : %s" % template)

    out_dir = os.path.join(THEMES_DIR, game, name)
    if accent is None:
        accent = dominant_accent(art)
    print("%s/%s  couleur %s  gabarit %s"
          % (game, name, rgb_to_hex(accent), os.path.basename(tpl_dir)))
    if dry_run:
        return accent

    os.makedirs(out_dir, exist_ok=True)

    # l'illustration
    Image.open(art).convert("RGB").save(os.path.join(out_dir, "background.png"),
                                        "PNG", optimize=True)

    # polices et pixmaps du menu, tels quels
    for fname in TEMPLATE_FILES:
        src = os.path.join(tpl_dir, fname)
        if os.path.isfile(src):
            shutil.copyfile(src, os.path.join(out_dir, fname))

    # barres de sélection, à la couleur du personnage
    for fname in SELECT_FILES:
        src = os.path.join(tpl_dir, fname)
        if os.path.isfile(src):
            recolor_select(src, os.path.join(out_dir, fname), accent)

    # icônes : copiées puis recolorées par recolor_icons
    icons_src = os.path.join(tpl_dir, "icons")
    icons_dst = os.path.join(out_dir, "icons")
    if os.path.isdir(icons_src):
        shutil.rmtree(icons_dst, ignore_errors=True)
        shutil.copytree(icons_src, icons_dst)

    # theme.txt : celui du gabarit, avec la couleur du personnage
    with open(os.path.join(tpl_dir, "theme.txt"), encoding="utf-8") as f:
        text = f.read()
    text = replace_value(text, "fg_color", rgb_to_hex(accent))
    with open(os.path.join(out_dir, "theme.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    count, before, after = recolor_theme(out_dir, cache={})
    print("   %d icônes recolorées (%.1f Mo)" % (count, after / 1048576))
    return accent


def main():
    parser = argparse.ArgumentParser(description="Construit un thème à partir d'une illustration")
    parser.add_argument("--game", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--art", required=True, help="l'illustration de l'All-Out Attack")
    parser.add_argument("--from", dest="template", required=True, help="thème servant de gabarit")
    parser.add_argument("--accent", help="couleur du personnage (#RRGGBB), sinon devinée")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    accent = hex_to_rgb(args.accent) if args.accent else None
    build(args.game, args.name, args.art, args.template, accent, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
