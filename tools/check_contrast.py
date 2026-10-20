#!/usr/bin/env python3
"""
Vérifie (et corrige avec --fix) la lisibilité des textes de chaque thème :
  - texte du menu sur le fond (assombri par le panneau boot_menu_c.png)
  - texte sélectionné sur la barre de sélection (select_c.png)
  - texte de la barre de progression sur sa couleur

Usage :
    python3 tools/check_contrast.py           # rapport, code 1 si un thème échoue
    python3 tools/check_contrast.py --fix     # corrige les theme.txt

Dépendance (outil de dev uniquement) : Pillow
"""
import argparse
import glob
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")

LIGHT = "#ECE9DB"
DARK = "#000000"
WHITE = "#FFFFFF"

# Couleurs de barre de progression appliquées à tout un jeu, remplacées par la couleur du perso
GAME_WIDE_PROGRESS = {"#8B0000", "#0066FF"}

MIN_MENU = 4.5      # WCAG AA, texte normal (police Regular 14)
MIN_SELECTED = 3.0  # texte en gras sur la barre de sélection
MIN_PROGRESS = 3.0  # texte en gras sur la barre de progression


# --- COULEURS ---
def hex_to_rgb(value):
    value = value.lstrip("#")[:6]
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def luminance(rgb):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(color_a, color_b):
    l1, l2 = luminance(color_a), luminance(color_b)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def darken_for_white_text(rgb, minimum):
    """Assombrit la couleur (même teinte) jusqu'à ce que du texte blanc soit lisible dessus"""
    base, factor = rgb, 1.0
    while factor > 0 and contrast((255, 255, 255), rgb) < minimum:
        factor -= 0.02
        rgb = tuple(int(round(c * factor)) for c in base)
    return rgb


# --- LECTURE DU THÈME ---
def read_value(text, key):
    match = re.search(r'^\s*' + key + r'\s*=\s*"?([^"\n]+)"?', text, re.M)
    return match.group(1).strip() if match else None


def replace_value(text, key, value):
    return re.sub(r'^(\s*' + key + r'\s*=\s*)"?[^"\n]+"?', r'\g<1>"' + value + '"', text, count=1, flags=re.M)


def percent(text, key):
    return float(read_value(text, key).rstrip("%")) / 100


def menu_background(theme_dir, text):
    """Couleur médiane du fond derrière le menu, assombri par le panneau"""
    bg = Image.open(os.path.join(theme_dir, "background.png")).convert("RGB").resize((1920, 1080))
    left, top = percent(text, "left"), percent(text, "top")
    width, height = percent(text, "width"), percent(text, "height")
    region = bg.crop((int(left * 1920), int(top * 1080),
                      int((left + width) * 1920), int((top + height) * 1080)))

    panel = Image.open(os.path.join(theme_dir, "boot_menu_c.png")).convert("RGBA")
    pr, pg, pb, pa = panel.getpixel((panel.width // 2, panel.height // 2))
    region = Image.blend(region, Image.new("RGB", region.size, (pr, pg, pb)), pa / 255)

    data = region.resize((64, 64)).tobytes()
    pixels = sorted((data[i:i + 3] for i in range(0, len(data), 3)), key=luminance)
    return tuple(pixels[len(pixels) // 2])


def selection_color(theme_dir):
    sel = Image.open(os.path.join(theme_dir, "select_c.png")).convert("RGB")
    return sel.getpixel((sel.width // 2, sel.height // 2))


def pick_text(current, background, minimum, candidates):
    """Garde la couleur actuelle si elle est lisible, sinon prend le meilleur candidat"""
    if contrast(hex_to_rgb(current), background) >= minimum:
        return current
    best = max(candidates, key=lambda c: contrast(hex_to_rgb(c), background))
    if contrast(hex_to_rgb(best), background) > contrast(hex_to_rgb(current), background):
        return best
    return current


# --- ANALYSE ---
def check_theme(theme_dir, fix):
    path = os.path.join(theme_dir, "theme.txt")
    with open(path) as f:
        text = f.read()

    item = read_value(text, "item_color")[:7]
    selected = read_value(text, "selected_item_color")[:7]
    progress_fg = read_value(text, "fg_color")

    menu_bg = menu_background(theme_dir, text)
    sel_rgb = selection_color(theme_dir)

    # Le panneau du menu est sombre : le texte du menu ne passe jamais en noir
    new_item = pick_text(item, menu_bg, MIN_MENU, [LIGHT])
    new_selected = pick_text(selected, sel_rgb, MIN_SELECTED, [LIGHT, DARK])

    # Barre de progression : couleur du perso (celle de la sélection) au lieu de la couleur du jeu,
    # assombrie si besoin pour que le texte blanc reste lisible
    fg_rgb = hex_to_rgb(progress_fg)
    if rgb_to_hex(fg_rgb) in GAME_WIDE_PROGRESS:
        fg_rgb = sel_rgb
    new_fg = rgb_to_hex(darken_for_white_text(fg_rgb, MIN_PROGRESS))

    changes = []
    for key, old, new in (("item_color", item, new_item),
                          ("selected_item_color", selected, new_selected),
                          ("fg_color", progress_fg, new_fg)):
        if hex_to_rgb(old) != hex_to_rgb(new):
            changes.append((key, old, new))
    if hex_to_rgb(read_value(text, "text_color")) != hex_to_rgb(WHITE):
        changes.append(("text_color", read_value(text, "text_color"), WHITE))

    if fix and changes:
        for key, _, value in changes:
            text = replace_value(text, key, value)
        with open(path, "w") as f:
            f.write(text)

    ratios = (contrast(hex_to_rgb(item), menu_bg),
              contrast(hex_to_rgb(selected), sel_rgb),
              contrast((255, 255, 255), hex_to_rgb(progress_fg)))
    new_ratios = (contrast(hex_to_rgb(new_item), menu_bg),
                  contrast(hex_to_rgb(new_selected), sel_rgb),
                  contrast((255, 255, 255), hex_to_rgb(new_fg)))
    return ratios, new_ratios, changes


def passes(ratios):
    return ratios[0] >= MIN_MENU and ratios[1] >= MIN_SELECTED and ratios[2] >= MIN_PROGRESS


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fix", action="store_true", help="corrige les theme.txt")
    parser.add_argument("themes", nargs="*", help="dossiers de thèmes (par défaut : tous)")
    args = parser.parse_args()

    theme_dirs = args.themes or sorted(
        os.path.dirname(p) for p in glob.glob(os.path.join(THEMES_DIR, "*", "*", "theme.txt"))
    )

    failures = 0
    print(f"{'theme':38} {'menu':>6} {'select':>7} {'bar':>5}")
    for theme_dir in theme_dirs:
        ratios, new_ratios, changes = check_theme(theme_dir, args.fix)
        final = new_ratios if args.fix else ratios
        flag = "" if passes(final) else "  <-- low contrast"
        failures += not passes(final)
        name = os.path.relpath(theme_dir, THEMES_DIR)
        print(f"{name:38} {final[0]:6.1f} {final[1]:7.1f} {final[2]:5.1f}{flag}")
        for key, old, new in changes:
            print(f"    {'fixed' if args.fix else 'can fix'} {key}: {old} -> {new}")

    print(f"\n{len(theme_dirs) - failures}/{len(theme_dirs)} themes pass "
          f"(menu >= {MIN_MENU}, selected >= {MIN_SELECTED}, bar >= {MIN_PROGRESS})")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
