#!/usr/bin/env python3
import os
import sys
import glob
import shutil
import argparse
import datetime
import subprocess

# --- CONFIGURATION DES COULEURS (ANSI) ---
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"

# Couleurs de fond
BG_RED    = "\033[41m\033[37m"
BG_BLUE   = "\033[44m\033[37m"
BG_GREEN  = "\033[42m\033[37m"
BG_YELLOW = "\033[43m\033[30m"
BG_PURPLE = "\033[45m\033[37m"
BG_CYAN   = "\033[46m\033[37m"
BG_WHITE  = "\033[47m\033[30m"
BG_ORANGE = "\033[48;5;208m\033[37m"
BG_GREY   = "\033[48;5;240m\033[37m"
BG_PINK   = "\033[48;5;205m\033[37m"
BG_BROWN  = "\033[48;5;94m\033[37m"
BG_TEAL   = "\033[48;5;30m\033[37m" 

# --- MAPPING COULEURS PERSONNAGES ---
CHARACTER_COLORS = {
    # --- Persona 3 Reload ---
    "makoto":   BG_BLUE,
    "junpei":   BG_CYAN,
    "akihiko":  BG_GREY,
    "mitsuru":  BG_PURPLE,
    "aigis":    BG_YELLOW, 
    "ken":      BG_ORANGE,
    "yukari":   BG_PINK,
    "fuuka":    BG_TEAL,
    "koromaru": BG_WHITE,
    "shinji":   BG_BROWN,
    "metis":    BG_RED,
    "kotone":   BG_PINK,

    # --- Persona 5 Royal ---
    "joker":    BG_RED,
    "skull":    BG_YELLOW,
    "panther":  BG_PINK,
    "morgana":  BG_CYAN,
    "fox":      BG_BLUE,
    "queen":    BG_BLUE,
    "oracle":   BG_GREEN,
    "noir":     BG_PURPLE,
    "crow":     BG_WHITE,
    "violet":   BG_RED,
    "lavenza":  BG_PURPLE,
    "caroline": BG_BLUE,
    
    # --- Persona 5: The Phantom X ---
    "wonder":   BG_RED,
    "ange":     BG_YELLOW,
    "berry":    BG_PINK,
    "bui":      BG_GREEN,
    "cattle":   BG_BROWN,
    "cherish":  BG_PINK,
    "chord":    BG_GREY,
    "closer":   BG_GREEN,
    "fleuret":  BG_PURPLE,
    "howler":   BG_ORANGE,
    "key":      BG_CYAN,
    "leon":     BG_RED,
    "luce":     BG_WHITE,
    "marian":   BG_PURPLE,
    "matoi":    BG_RED,
    "messa":    BG_PURPLE,
    "moko":     BG_PINK,
    "mont":     BG_GREEN,
    "okyann":   BG_BLUE,
    "phoebe":   BG_ORANGE,
    "puppet":   BG_GREY,
    "riddle":   BG_TEAL,
    "rin":      BG_GREY,
    "sepia":    BG_BROWN,
    "soy":      BG_BLUE,
    "turbo":    BG_YELLOW,
    "vino":     BG_PURPLE,
    "wind":     BG_CYAN,
    "yuki":     BG_WHITE
}

# --- NOMS D'AFFICHAGE SPÉCIAUX ---
CHARACTER_DISPLAY_NAMES = {
    "caroline_justine": "Caroline & Justine",
    "bui_cosmic":    "Bui (Cosmic)",
    "luce_notte":    "Luce (Notte)",
    "moko_summer":   "Moko (Summer)",
    "soy_pioneer":   "Soy (Pioneer)",
    "wind_vast":     "Wind (Vast)",
    "wonder_cny":    "Wonder (Chinese New Year)",
    "wonder_summer": "Wonder (Summer)",
    "wonder_valentine": "Wonder (Valentine)", # AJOUTÉ ICI
    "marian_summer": "Marian (Summer)",
    "closer_summer": "Closer (Summer)",
    "puppet_summer": "Puppet (Summer)",
    "rin_cny":       "Rin (Chinese New Year)",
    "mont_music":    "Mont (Music)"
}

# --- ANCIENS NOMS DE DOSSIERS ---
# Variantes renommées avec leur nom officiel : les anciens noms marchent toujours
# avec --theme, et --uninstall retire aussi les thèmes installés sous l'ancien nom
RENAMED_THEMES = {
    "bui_stellar":   "bui_cosmic",
    "soy_frontiere": "soy_pioneer",
    "wonder_beach":  "wonder_summer",
    "closer_beach":  "closer_summer",
    "moko_beach":    "moko_summer",
    "marian_beach":  "marian_summer",
    "puppet_beach":  "puppet_summer",
}

# Chemins
PWD = os.path.dirname(os.path.realpath(__file__))
THEMES_DIR = os.path.join(PWD, "themes")
GRUB_CONFIG_FILE = "/etc/default/grub"
# Copie de la config d'origine, faite une seule fois et jamais écrasée
GRUB_CONFIG_ORIGINAL = GRUB_CONFIG_FILE + ".persona.orig"
DRM_DIR = "/sys/class/drm"

# Mode simulation (--dry-run) : rien n'est écrit
DRY_RUN = False

# Noms d'affichage des jeux
GAME_NAMES = {
    "persona5_royal": "Persona 5 Royal",
    "persona5_phantom_x": "Persona 5: The Phantom X",
    "persona3_reload": "Persona 3 Reload"
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, color=BG_RED):
    print(f"\n{color}  {title}  {C_RESET}\n")

def check_root():
    if os.geteuid() != 0:
        print(f"{BG_RED} ERROR {C_RESET} This script requires root privileges.")
        print("Please run with: sudo python3 install.py")
        sys.exit(1)

def get_char_color(char_name, default_color):
    """Cherche la couleur spécifique du perso, sinon retourne la couleur du jeu"""
    key = char_name.lower()
    for name, color in CHARACTER_COLORS.items():
        # Match exact ou préfixe (pour gérer wonder_summer, wonder_cny, etc.)
        if key == name or key.startswith(name + "_"): 
            return color
    return default_color

def get_display_name(folder_name):
    """Retourne un nom joli pour le dossier"""
    key = folder_name.lower()
    if key in CHARACTER_DISPLAY_NAMES:
        return CHARACTER_DISPLAY_NAMES[key]
    return folder_name.capitalize().replace("_", " ")

def scan_themes():
    structure = {}
    if not os.path.exists(THEMES_DIR):
        print(f"Error: Directory {THEMES_DIR} not found.")
        sys.exit(1)

    # Ignore les dossiers système, icons et docs
    ignored_folders = ["icons", "docs", "assets"]
    games = [d for d in os.listdir(THEMES_DIR) 
             if os.path.isdir(os.path.join(THEMES_DIR, d)) 
             and not d.startswith('_') 
             and d not in ignored_folders]
    
    for game in games:
        structure[game] = {}
        game_path = os.path.join(THEMES_DIR, game)
        subfolders = [f for f in os.listdir(game_path) if os.path.isdir(os.path.join(game_path, f)) and not f.startswith('_')]
        subfolders.sort()

        for folder in subfolders:
            # Vérifie que c'est un thème valide
            if not os.path.exists(os.path.join(game_path, folder, "theme.txt")):
                continue

            # --- LOGIQUE DE REGROUPEMENT ---
            parts = folder.split('_')
            
            # Gestion spéciale pour Caroline & Justine
            if folder == "caroline_justine":
                base_display = "Caroline & Justine"
                variant_name = "Default"
            
            # Gestion des variantes connues dans le mapping (Ex: wonder_valentine)
            elif folder in CHARACTER_DISPLAY_NAMES:
                full_name = CHARACTER_DISPLAY_NAMES[folder]
                if "(" in full_name:
                    # Extrait "Wonder" de "Wonder (Valentine)"
                    base_display = full_name.split('(')[0].strip()
                    # Extrait "Valentine" de "(Valentine)"
                    variant_name = full_name.split('(')[1].replace(')', '').strip()
                else:
                    base_display = full_name
                    variant_name = "Default"
            
            else:
                # Cas standard ou non mappé
                base_display = parts[0].capitalize()
                variant_name = "Default"
                if len(parts) > 1:
                    variant_name = " ".join([p.capitalize() for p in parts[1:]])

            if base_display not in structure[game]:
                structure[game][base_display] = {}
            
            structure[game][base_display][variant_name] = os.path.join(game_path, folder)
            
    return structure

def select_from_dict(options, prompt_text, default_color=BG_RED, use_char_colors=False):
    keys = list(options.keys())
    
    for i, key in enumerate(keys):
        display_color = default_color
        
        if use_char_colors:
            char_key = key.split(' ')[0].lower()
            if "caroline" in char_key: char_key = "caroline"
            display_color = get_char_color(char_key, default_color)
            
        print(f"  {display_color}[{i+1}] {key} {C_RESET}")
    
    print()
    while True:
        try:
            choice = input(f"{prompt_text} (1-{len(keys)}): ")
            if not choice.strip(): continue
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            pass
        print("Invalid selection.")

# --- DÉTECTION DE GRUB ---
def detect_grub():
    """Retourne (dossier GRUB, commande de mise à jour) selon la distribution.
    Debian/Ubuntu/Arch : /boot/grub — Fedora/openSUSE/RHEL : /boot/grub2"""
    if os.path.isdir("/boot/grub2") and not os.path.isdir("/boot/grub"):
        grub_dir = "/boot/grub2"
    elif os.path.isfile("/boot/grub2/grub.cfg") and not os.path.isfile("/boot/grub/grub.cfg"):
        grub_dir = "/boot/grub2"
    else:
        grub_dir = "/boot/grub"

    cfg = os.path.join(grub_dir, "grub.cfg")
    if shutil.which("update-grub"):
        cmd = ["update-grub"]
    elif shutil.which("grub2-mkconfig"):
        cmd = ["grub2-mkconfig", "-o", cfg]
    elif shutil.which("grub-mkconfig"):
        cmd = ["grub-mkconfig", "-o", cfg]
    else:
        cmd = None
    return grub_dir, cmd

def detect_resolution():
    """Résolution native du premier écran branché (ex: '1920x1080'), sinon None"""
    for status_file in sorted(glob.glob(os.path.join(DRM_DIR, "card*-*", "status"))):
        try:
            with open(status_file) as f:
                if f.read().strip() != "connected":
                    continue
            with open(os.path.join(os.path.dirname(status_file), "modes")) as f:
                mode = f.readline().strip()
            if mode:
                return mode
        except OSError:
            continue
    return None

# --- CONFIGURATION ---
def backup_grub_config():
    """Garde la config d'origine une seule fois, puis une sauvegarde horodatée à chaque modif"""
    if DRY_RUN:
        return
    if not os.path.exists(GRUB_CONFIG_ORIGINAL):
        shutil.copyfile(GRUB_CONFIG_FILE, GRUB_CONFIG_ORIGINAL)
        print(f"Original config saved to {GRUB_CONFIG_ORIGINAL}")
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    shutil.copyfile(GRUB_CONFIG_FILE, f"{GRUB_CONFIG_FILE}.bak.{stamp}")

def write_grub_config(lines, new_lines):
    if new_lines == lines:
        print(f"{GRUB_CONFIG_FILE} is already up to date.")
        return
    if DRY_RUN:
        print(f"{BG_YELLOW} DRY RUN {C_RESET} Changes that would be made to {GRUB_CONFIG_FILE}:")
        for line in lines:
            if line not in new_lines:
                print(f"  - {line.rstrip()}")
        for line in new_lines:
            if line not in lines:
                print(f"  + {line.rstrip()}")
        return
    backup_grub_config()
    with open(GRUB_CONFIG_FILE, 'w') as f:
        f.writelines(new_lines)

def config_value(line):
    return line.split("=", 1)[1].strip().strip('"').strip("'")

def update_grub_config(theme_path, gfxmode=None):
    print(f"Updating {GRUB_CONFIG_FILE}...")
    with open(GRUB_CONFIG_FILE, 'r') as f:
        lines = f.readlines()

    new_lines = []
    theme_set = False
    gfxmode_set = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("GRUB_THEME="):
            new_lines.append(f'GRUB_THEME="{theme_path}/theme.txt"\n')
            theme_set = True
        # Un terminal "console" désactive le thème graphique
        elif stripped.startswith("GRUB_TERMINAL_OUTPUT=") and "console" in config_value(stripped):
            new_lines.append("#" + line)
        elif stripped.startswith("GRUB_TERMINAL=") and config_value(stripped) == "console":
            new_lines.append("#" + line)
        else:
            if stripped.startswith("GRUB_GFXMODE="):
                gfxmode_set = True
            new_lines.append(line)

    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"
    if not theme_set:
        new_lines.append(f'GRUB_THEME="{theme_path}/theme.txt"\n')
    # On ne touche pas à une résolution déjà choisie par l'utilisateur
    if not gfxmode_set:
        mode = f"{gfxmode},auto" if gfxmode else "auto"
        new_lines.append(f'GRUB_GFXMODE="{mode}"\n')

    write_grub_config(lines, new_lines)

def remove_theme_from_config():
    with open(GRUB_CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    new_lines = ["#" + line if line.strip().startswith("GRUB_THEME=") else line for line in lines]
    write_grub_config(lines, new_lines)

def update_grub_binary(cmd):
    print_header("Updating GRUB Binary...", BG_BLUE)
    if not cmd:
        print(f"{BG_RED} WARNING {C_RESET} Could not find 'update-grub', 'grub-mkconfig' or 'grub2-mkconfig'.")
        return False
    if DRY_RUN:
        print(f"{BG_YELLOW} DRY RUN {C_RESET} Would run: {' '.join(cmd)}")
        return True
    try:
        subprocess.run(cmd, check=True)
        print(f"\n{BG_GREEN} SUCCESS {C_RESET} GRUB has been updated successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"\n{BG_RED} ERROR {C_RESET} Failed to update GRUB.")
        return False

# --- ACTIONS ---
def install_theme(source_path, grub_dir, cmd):
    themes_target = os.path.join(grub_dir, "themes")
    target_path = os.path.join(themes_target, os.path.basename(source_path))

    if DRY_RUN:
        print(f"{BG_YELLOW} DRY RUN {C_RESET} Would copy {source_path} -> {target_path}")
    else:
        os.makedirs(themes_target, exist_ok=True)
        print(f"Copying files to {target_path}...")
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        shutil.copytree(source_path, target_path)

    resolution = detect_resolution()
    if resolution:
        print(f"Detected screen resolution: {resolution}")
    update_grub_config(target_path, resolution)
    return update_grub_binary(cmd)

def uninstall_themes(grub_dir, cmd):
    """Retire GRUB_THEME de la config et supprime les thèmes Persona installés"""
    print_header("Uninstall", BG_RED)
    themes_target = os.path.join(grub_dir, "themes")
    ours = {name for name in os.listdir(THEMES_DIR) if not name.startswith("_")}
    ours = {theme for game in ours if os.path.isdir(os.path.join(THEMES_DIR, game))
            for theme in os.listdir(os.path.join(THEMES_DIR, game))}
    ours |= set(RENAMED_THEMES)

    installed = []
    if os.path.isdir(themes_target):
        installed = sorted(t for t in os.listdir(themes_target) if t in ours)
    for theme in installed:
        path = os.path.join(themes_target, theme)
        if DRY_RUN:
            print(f"{BG_YELLOW} DRY RUN {C_RESET} Would remove {path}")
        else:
            print(f"Removing {path}")
            shutil.rmtree(path)
    if not installed:
        print("No Persona theme found in " + themes_target)

    remove_theme_from_config()
    update_grub_binary(cmd)

def restore_config(cmd):
    """Remet la config GRUB telle qu'elle était avant la toute première installation"""
    print_header("Restore", BG_BLUE)
    if not os.path.exists(GRUB_CONFIG_ORIGINAL):
        print(f"{BG_RED} ERROR {C_RESET} No original backup found ({GRUB_CONFIG_ORIGINAL}).")
        return
    if DRY_RUN:
        print(f"{BG_YELLOW} DRY RUN {C_RESET} Would restore {GRUB_CONFIG_ORIGINAL} -> {GRUB_CONFIG_FILE}")
    else:
        backup_grub_config()
        shutil.copyfile(GRUB_CONFIG_ORIGINAL, GRUB_CONFIG_FILE)
        print(f"Restored {GRUB_CONFIG_FILE} from {GRUB_CONFIG_ORIGINAL}")
    update_grub_binary(cmd)

def list_themes(data):
    for game in sorted(data.keys()):
        print_header(GAME_NAMES.get(game, game), BG_BLUE if "persona3" in game else BG_RED)
        for char in sorted(data[game].keys()):
            for variant, path in data[game][char].items():
                label = char if variant == "Default" else f"{char} ({variant})"
                print(f"  {os.path.basename(path):20} {label}")

def find_theme(data, name):
    """Trouve un thème par nom de dossier ('joker') ou 'jeu/dossier' ('persona5_royal/joker')"""
    game_prefix, _, folder_name = name.rpartition("/")
    if folder_name in RENAMED_THEMES:
        name = f"{game_prefix}/{RENAMED_THEMES[folder_name]}" if game_prefix else RENAMED_THEMES[folder_name]
    matches = []
    for game, characters in data.items():
        for variants in characters.values():
            for path in variants.values():
                folder = os.path.basename(path)
                if name in (folder, f"{game}/{folder}"):
                    matches.append(path)
    return matches

def ask_reboot():
    reboot = input(f"\n{C_BOLD}Do you want to reboot now? [y/N]: {C_RESET}")
    if reboot.lower() in ["y", "yes"]:
        print("Rebooting...")
        subprocess.run(["reboot"])
    else:
        print("Okay. Don't forget to reboot later!")

def parse_args():
    parser = argparse.ArgumentParser(description="Persona GRUB Theme Installer")
    parser.add_argument("--theme", metavar="NAME",
                        help="install a theme without the menu (folder name, e.g. 'joker' or 'persona5_royal/joker')")
    parser.add_argument("--list", action="store_true", help="list available themes")
    parser.add_argument("--uninstall", action="store_true", help="remove installed Persona themes and the GRUB_THEME line")
    parser.add_argument("--restore", action="store_true", help="restore /etc/default/grub as it was before the first install")
    parser.add_argument("--dry-run", action="store_true", help="show what would change without touching anything")
    parser.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation or reboot")
    return parser.parse_args()

def interactive_select(data):
    """Menus jeu -> personnage -> variante. Retourne (chemin, nom, variante ou None, couleur)"""
    # 1. Sélection du JEU
    print(f"{C_BOLD}Select your Game:{C_RESET}")
    sorted_games = {k: data[k] for k in sorted(data.keys())} 
    display_games = {GAME_NAMES.get(k, k): k for k in sorted_games.keys()}
    selected_game_display = select_from_dict(display_games, "Choose a game", BG_RED)
    selected_game_key = display_games[selected_game_display]
    
    game_default_color = BG_BLUE if "persona3" in selected_game_key else BG_RED
    
    # 2. Sélection du PERSONNAGE
    clear_screen()
    print_header(selected_game_display, game_default_color)
    print(f"{C_BOLD}Select a Character:{C_RESET}")
    
    characters = data[selected_game_key]
    characters = {k: characters[k] for k in sorted(characters.keys())}
    selected_char_key = select_from_dict(characters, "Choose a character", game_default_color, use_char_colors=True)
    
    char_key_simple = selected_char_key.split(' ')[0].lower()
    if "caroline" in char_key_simple: char_key_simple = "caroline"
    char_color = get_char_color(char_key_simple, game_default_color)

    # 3. Sélection de la VARIANTE
    variants = characters[selected_char_key]
    
    if len(variants) == 1:
        return list(variants.values())[0], selected_char_key, None, char_color

    clear_screen()
    print_header(f"{selected_char_key} Styles", char_color)
    print(f"{C_BOLD}Select a Style:{C_RESET}")
    selected_variant_key = select_from_dict(variants, "Choose a style", char_color)
    return variants[selected_variant_key], selected_char_key, selected_variant_key, char_color

def main():
    global DRY_RUN
    args = parse_args()
    DRY_RUN = args.dry_run

    data = scan_themes()
    if not data:
        print("No themes found.")
        return

    if args.list:
        list_themes(data)
        return

    if not DRY_RUN:
        check_root()
    if not os.path.isfile(GRUB_CONFIG_FILE):
        print(f"{BG_RED} ERROR {C_RESET} {GRUB_CONFIG_FILE} not found. Is GRUB installed?")
        sys.exit(1)
    grub_dir, cmd = detect_grub()

    if args.restore:
        restore_config(cmd)
        return
    if args.uninstall:
        uninstall_themes(grub_dir, cmd)
        return

    if args.theme:
        matches = find_theme(data, args.theme)
        if len(matches) != 1:
            reason = "is ambiguous" if matches else "was not found"
            print(f"{BG_RED} ERROR {C_RESET} Theme '{args.theme}' {reason}. Use --list to see available themes.")
            sys.exit(1)
        final_path = matches[0]
        theme_name, variant_name, char_color = get_display_name(os.path.basename(final_path)), None, BG_RED
    else:
        clear_screen()
        print_header("PERSONA GRUB THEME INSTALLER")
        final_path, theme_name, variant_name, char_color = interactive_select(data)
        clear_screen()

    # --- INSTALLATION ---
    print_header("Installation", char_color)
    print(f"Theme: {C_BOLD}{theme_name}{C_RESET}")
    if variant_name:
        print(f"Style: {C_BOLD}{variant_name}{C_RESET}")
    print(f"Target: {os.path.join(grub_dir, 'themes', os.path.basename(final_path))}")
    print("-" * 30)
    
    if not args.yes:
        confirm = input("Proceed with installation? [Y/n]: ")
        if confirm.lower() in ["n", "no"]:
            print("Aborted.")
            return

    if not install_theme(final_path, grub_dir, cmd):
        sys.exit(1)

    if DRY_RUN:
        print(f"\n{BG_YELLOW} DRY RUN {C_RESET} Nothing was changed.")
        return

    print("\nEnjoy your Persona GRUB Theme! :)")
    print(f"\n{BG_GREEN} SUCCESS {C_RESET} Installation complete!")
    print("You need to reboot to see the changes.")
    print("To undo: sudo python3 install.py --restore")

    if not args.yes:
        ask_reboot()

if __name__ == "__main__": # Ne touche pas à ça
    main()
