#!/usr/bin/env python3
import os
import sys
import shutil
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
    "bui_stellar":   "Bui (Stellar)",
    "luce_notte":    "Luce (Notte)",
    "moko_beach":    "Moko (Beach)",
    "soy_frontiere": "Soy (Frontiere)",
    "wind_vast":     "Wind (Vast)",
    "wonder_cny":    "Wonder (Chinese New Year)",
    "wonder_beach":  "Wonder (Beach)",
    "wonder_valentine": "Wonder (Valentine)", # AJOUTÉ ICI
    "marian_beach":  "Marian (Beach)",
    "closer_beach":  "Closer (Beach)",
    "puppet_beach":  "Puppet (Beach)",
    "rin_cny":       "Rin (Chinese New Year)",
    "mont_music":    "Mont (Music)"
}

# Chemins
PWD = os.path.dirname(os.path.realpath(__file__))
THEMES_DIR = os.path.join(PWD, "themes")
GRUB_THEMES_TARGET = "/boot/grub/themes"
GRUB_CONFIG_FILE = "/etc/default/grub"

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
        # Match exact ou préfixe (pour gérer wonder_beach, wonder_cny, etc.)
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

def update_grub_config(theme_path):
    print(f"Updating {GRUB_CONFIG_FILE}...")
    shutil.copyfile(GRUB_CONFIG_FILE, f"{GRUB_CONFIG_FILE}.bak")
    
    with open(GRUB_CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    theme_set = False
    
    for line in lines:
        if line.strip().startswith("GRUB_THEME="):
            new_lines.append(f'GRUB_THEME="{theme_path}/theme.txt"\n')
            theme_set = True
        elif line.strip().startswith("GRUB_TERMINAL_OUTPUT=") or line.strip().startswith("#GRUB_TERMINAL_OUTPUT="):
            new_lines.append('#GRUB_TERMINAL_OUTPUT="console"\n')
        else:
            new_lines.append(line)
            
    if not theme_set:
        new_lines.append(f'GRUB_THEME="{theme_path}/theme.txt"\n')
        
    with open(GRUB_CONFIG_FILE, 'w') as f:
        f.writelines(new_lines)

def update_grub_binary():
    print_header("Updating GRUB Binary...", BG_BLUE)
    cmd = None
    if shutil.which("update-grub"):
        cmd = ["update-grub"]
    elif shutil.which("grub-mkconfig"):
        cmd = ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"]
    
    if cmd:
        try:
            subprocess.run(cmd, check=True)
            print(f"\n{BG_GREEN} SUCCESS {C_RESET} GRUB has been updated successfully!")
        except subprocess.CalledProcessError:
            print(f"\n{BG_RED} ERROR {C_RESET} Failed to update GRUB.")
    else:
        print(f"{BG_RED} WARNING {C_RESET} Could not find 'update-grub' or 'grub-mkconfig'.")

def main():
    clear_screen()
    check_root()
    
    print_header("PERSONA GRUB THEME INSTALLER")
    data = scan_themes()
    
    if not data:
        print("No themes found.")
        return

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
    final_path = ""
    
    if len(variants) == 1:
        final_path = list(variants.values())[0]
    else:
        clear_screen()
        print_header(f"{selected_char_key} Styles", char_color)
        print(f"{C_BOLD}Select a Style:{C_RESET}")
        selected_variant_key = select_from_dict(variants, "Choose a style", char_color)
        final_path = variants[selected_variant_key]

    # --- INSTALLATION ---
    folder_name = os.path.basename(final_path)
    target_path = os.path.join(GRUB_THEMES_TARGET, folder_name)
    
    clear_screen()
    print_header("Installation", char_color)
    print(f"Theme: {C_BOLD}{selected_char_key}{C_RESET}")
    if len(variants) > 1:
        print(f"Style: {C_BOLD}{selected_variant_key}{C_RESET}")
        
    print(f"Target: {target_path}")
    print("-" * 30)
    
    confirm = input("Proceed with installation? [Y/n]: ")
    if confirm.lower() in ["n", "no"]:
        print("Aborted.")
        return

    if not os.path.exists(GRUB_THEMES_TARGET):
        os.makedirs(GRUB_THEMES_TARGET)
        
    print(f"Copying files to {target_path}...")
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    shutil.copytree(final_path, target_path)
    
    update_grub_config(target_path)
    update_grub_binary()
    
    print("\nEnjoy your Persona GRUB Theme! :)")
    print(f"\n{BG_GREEN} SUCCESS {C_RESET} Installation complete!")
    print("You need to reboot to see the changes.")
    
    reboot = input(f"\n{C_BOLD}Do you want to reboot now? [y/N]: {C_RESET}")
    if reboot.lower() in ["y", "yes"]:
        print("Rebooting...")
        os.system("reboot")
    else:
        print("Okay. Don't forget to reboot later!")

if __name__ == "__main__": # Ne touche pas à ça
    main()