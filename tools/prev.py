import os
import shutil
import subprocess
import time
import sys
import argparse

# --- DÉTECTION INTELLIGENTE DES CHEMINS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.exists(os.path.join(SCRIPT_DIR, "themes")):
    PROJECT_ROOT = SCRIPT_DIR
elif os.path.exists(os.path.join(os.path.dirname(SCRIPT_DIR), "themes")):
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
else:
    print(f"❌ CRITIQUE : Impossible de trouver le dossier 'themes' depuis {SCRIPT_DIR}")
    sys.exit(1)

TEMP_DIR = os.path.join(PROJECT_ROOT, "temp_grub_preview")
ISO_FILE = os.path.join(TEMP_DIR, "grub_preview.iso")
RAW_IMAGE = os.path.join(TEMP_DIR, "screenshot.ppm")
RESOLUTION = "1920x1080"

def create_realistic_grub_cfg(theme_path_iso, resolution="1920x1080"):
    """Crée un grub.cfg avec des vraies entrées de boot"""
    return f"""
set timeout=30
set default=0

# Configuration graphique
set gfxmode={resolution}
set gfxpayload=keep

# Modules vidéo
insmod all_video
insmod vbe
insmod vga
insmod video_bochs
insmod video_cirrus
insmod gfxterm
insmod png
insmod jpeg
insmod gfxmenu

# Terminal graphique
terminal_output gfxterm

# Polices
loadfont {theme_path_iso}/dejavu_14.pf2
loadfont {theme_path_iso}/dejavu_bold_14.pf2

# Thème
set theme={theme_path_iso}/theme.txt
export theme

# ========== ENTRÉES RÉALISTES ==========

menuentry 'Ubuntu 24.04 LTS' --class ubuntu --class gnu-linux --class gnu --class os {{
    set root='hd0,gpt2'
    echo 'Loading Linux kernel...'
    sleep 1
}}

menuentry 'Ubuntu (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os {{
    set root='hd0,gpt2'
    echo 'Loading recovery mode...'
    sleep 1
}}

menuentry 'Kali Linux' --class kali --class gnu-linux --class gnu --class os {{
    set root='hd0,gpt3'
    echo 'Loading Kali Linux...'
    sleep 1
}}

menuentry 'Kali Linux (Failsafe)' --class kali --class gnu-linux --class gnu --class os {{
    set root='hd0,gpt3'
    echo 'Loading failsafe mode...'
    sleep 1
}}

menuentry 'Windows 11' --class windows --class os {{
    set root='hd0,gpt1'
    echo 'Loading Windows Boot Manager...'
    sleep 1
}}

menuentry 'Windows 11 (Safe Mode)' --class windows --class os {{
    set root='hd0,gpt1'
    echo 'Loading Windows Safe Mode...'
    sleep 1
}}

submenu 'Advanced options' {{
    menuentry 'UEFI Firmware Settings' {{
        echo 'Rebooting to firmware...'
        sleep 1
    }}
    
    menuentry 'System setup' {{
        echo 'Loading setup...'
        sleep 1
    }}
}}

menuentry 'Memtest86+' {{
    echo 'Loading memory test...'
    sleep 1
}}

menuentry 'Reboot' {{
    echo 'Rebooting...'
    sleep 1
}}

menuentry 'Power Off' {{
    echo 'Shutting down...'
    sleep 1
}}
"""

def find_themes():
    """Liste tous les thèmes disponibles"""
    themes_dir = os.path.join(PROJECT_ROOT, "themes")
    themes = []
    
    if not os.path.exists(themes_dir):
        return themes
    
    for game in os.listdir(themes_dir):
        game_path = os.path.join(themes_dir, game)
        # Ignorer les fichiers ou dossiers cachés/système
        if os.path.isdir(game_path) and not game.startswith('.') and game not in ['icons', 'assets', 'docs']:
            for character in os.listdir(game_path):
                character_path = os.path.join(game_path, character)
                if os.path.isdir(character_path) and not character.startswith('_'):
                    theme_txt = os.path.join(character_path, "theme.txt")
                    if os.path.exists(theme_txt):
                        themes.append({
                            "game": game,
                            "character": character,
                            "path": character_path,
                            "name": f"{game}/{character}"
                        })
    
    return themes

# Un écran GRUB encore noir ne contient qu'une poignée de couleurs ; un
# thème dessiné en contient des milliers.
MIN_COLORS = 256


def screen_colors(path):
    """Nombre de couleurs distinctes dans une capture, 0 si illisible"""
    try:
        out = subprocess.run(["identify", "-format", "%k", path],
                             capture_output=True, text=True, check=True)
        return int(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return 0


def generate_preview(theme_path, output_path, resolution="1920x1080", wait_time=25):
    """Génère une preview pour un thème donné"""
    
    print(f"\n{'='*60}")
    print(f"🎨 Génération preview : {os.path.basename(os.path.dirname(theme_path))}/{os.path.basename(theme_path)}")
    print(f"{'='*60}")
    
    # Nettoyage
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Structure ISO
    iso_build_dir = os.path.join(TEMP_DIR, "iso_root")
    target_theme_dir = os.path.join(iso_build_dir, "boot", "grub", "themes", "preview_theme")
    os.makedirs(target_theme_dir, exist_ok=True)
    
    print("📂 Copie du thème...")
    try:
        shutil.copytree(theme_path, target_theme_dir, dirs_exist_ok=True)
        
        # Vérifications
        theme_txt = os.path.join(target_theme_dir, "theme.txt")
        if not os.path.exists(theme_txt):
            print("   ❌ theme.txt manquant !")
            return False
        
        print("   ✓ Thème copié")
        
    except Exception as e:
        print(f"❌ Erreur copie : {e}")
        return False

    # Création grub.cfg
    grub_dir = os.path.join(iso_build_dir, "boot", "grub")
    os.makedirs(grub_dir, exist_ok=True)
    with open(os.path.join(grub_dir, "grub.cfg"), "w") as f:
        f.write(create_realistic_grub_cfg("/boot/grub/themes/preview_theme", resolution))
    
    print("   ✓ Configuration GRUB créée")

    print("💿 Génération ISO...")
    try:
        subprocess.run(
            ["grub-mkrescue", "-o", ISO_FILE, iso_build_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        iso_size = os.path.getsize(ISO_FILE) // 1024
        print(f"   ✓ ISO créée ({iso_size} KB)")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur : {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("❌ grub-mkrescue non trouvé")
        return False

    print(f"🖥️  Lancement QEMU ({resolution})...")
    
    qemu_cmd = [
        "qemu-system-x86_64",
        "-cdrom", ISO_FILE,
        "-m", "2048M",
        "-vga", "std",
        "-display", "none",
        "-monitor", "stdio",
        "-boot", "d",
        "-no-reboot"
    ]
    
    if os.path.exists("/dev/kvm"):
        qemu_cmd.insert(1, "-enable-kvm")

    proc = None
    final_image = RAW_IMAGE
    
    try:
        proc = subprocess.Popen(
            qemu_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # On capture en boucle jusqu'à ce que GRUB ait vraiment dessiné le
        # thème. Un écran encore noir n'a qu'une seule couleur : tant qu'on est
        # dans ce cas, la capture est rejouée. Sans KVM le thème apparaît vers
        # 15-20 s, avec KVM en 2-3 s : la boucle s'adapte au lieu d'attendre à
        # l'aveugle.
        print(f"⏳ Attente GRUB (max {wait_time}s)...")
        drawn = False
        for elapsed in range(2, wait_time + 1, 2):
            time.sleep(2)
            if os.path.exists(RAW_IMAGE):
                os.remove(RAW_IMAGE)
            proc.stdin.write(f"screendump {RAW_IMAGE}\n")
            proc.stdin.flush()
            time.sleep(1)
            if not os.path.exists(RAW_IMAGE):
                continue
            if screen_colors(RAW_IMAGE) >= MIN_COLORS:
                size_kb = os.path.getsize(RAW_IMAGE) // 1024
                print(f"   ✓ thème dessiné à {elapsed}s ({size_kb} KB)")
                drawn = True
                break
            print(f"   {elapsed}s : écran encore vide...")

        if not drawn:
            print(f"   ❌ Rien de dessiné après {wait_time}s")
            proc.stdin.write("quit\n")
            proc.stdin.flush()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            return False

        
        proc.stdin.write("quit\n")
        proc.stdin.flush()
        
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        
    except Exception as e:
        print(f"❌ Erreur QEMU : {e}")
        if proc and proc.poll() is None:
            proc.kill()
        return False

    # Conversion PNG
    if os.path.exists(final_image):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Vérifie et force la résolution
            identify_result = subprocess.run(
                ["identify", "-format", "%wx%h", final_image],
                capture_output=True,
                text=True
            )
            dimensions = identify_result.stdout.strip()
            print(f"\n📐 Dimensions : {dimensions}")
            
            # Force toujours à la résolution demandée
            width, height = resolution.split('x')
            subprocess.run(
                ["convert", final_image, "-resize", f"{width}x{height}!", output_path],
                check=True,
                stdout=subprocess.DEVNULL
            )
            
            png_size = os.path.getsize(output_path) // 1024
            print("✅ Preview créée !")
            print(f"   📁 {output_path}")
            print(f"   📊 {png_size} KB")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur conversion : {e}")
            return False
    else:
        print("❌ Aucune capture")
        return False

def main():
    parser = argparse.ArgumentParser(description="Générateur de previews pour thèmes GRUB")
    parser.add_argument("--theme", help="Chemin du thème (ex: persona5_royal/joker)")
    parser.add_argument("--folder", help="Générer pour tout un dossier (ex: persona5_phantom_x)")
    parser.add_argument("--all", action="store_true", help="Générer pour tous les thèmes")
    parser.add_argument("--list", action="store_true", help="Lister les thèmes disponibles")
    parser.add_argument("--resolution", default="1920x1080", help="Résolution (défaut: 1920x1080)")
    parser.add_argument("--wait", type=int, default=60, help="Attente maximale en secondes (défaut: 60)")
    
    args = parser.parse_args()
    
    # Liste des thèmes
    themes = find_themes()
    
    if args.list:
        print("\n📚 Thèmes disponibles :\n")
        current_game = ""
        for theme in sorted(themes, key=lambda x: x['name']):
            if theme['game'] != current_game:
                print(f"\n📁 {theme['game'].upper()} :")
                current_game = theme['game']
            print(f"  • {theme['character']}")
        print(f"\n  Total : {len(themes)} thème(s)")
        return
    
    if args.all:
        print(f"\n🎯 Génération de {len(themes)} preview(s) (TOUT)...\n")
        themes_to_process = themes
    elif args.folder:
        # Filtrer les thèmes qui appartiennent au dossier demandé
        themes_to_process = [t for t in themes if t['game'] == args.folder]
        
        if not themes_to_process:
            print(f"❌ Aucun thème trouvé dans le dossier '{args.folder}'")
            print("Utilisez --list pour voir les dossiers disponibles.")
            return
            
        print(f"\n🎯 Génération de {len(themes_to_process)} preview(s) pour le dossier '{args.folder}'...\n")
    elif args.theme:
        # Thème spécifique
        parts = args.theme.split('/')
        if len(parts) != 2:
            print("❌ Format: --theme game/character (ex: persona5_royal/joker)")
            return
        
        target_name = args.theme
        themes_to_process = [t for t in themes if t['name'] == target_name]
        
        if not themes_to_process:
            print(f"❌ Thème non trouvé : {target_name}")
            return
    else:
        parser.print_help()
        print("\n💡 Exemples :")
        print("  python prev.py --list")
        print("  python prev.py --theme persona5_royal/joker")
        print("  python prev.py --folder persona5_phantom_x   <-- Nouveau !")
        print("  python prev.py --all")
        return

    # Lancement de la génération pour la liste sélectionnée
    success = 0
    failed = 0
    
    for theme in themes_to_process:
        output_path = os.path.join(
            PROJECT_ROOT, 
            "previews", 
            theme['game'], 
            f"{theme['character']}.png"
        )
        
        if generate_preview(theme['path'], output_path, args.resolution, args.wait):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Succès : {success}")
    print(f"❌ Échecs : {failed}")
    print(f"{'='*60}")

    # Nettoyage
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    main()