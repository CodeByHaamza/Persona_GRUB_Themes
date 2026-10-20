#!/bin/bash

# Script pour générer les theme.txt manquants
# Usage: ./generate_theme_txt.sh <dossier>

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Template theme.txt
create_theme_txt() {
    local target_dir="$1"
    local theme_file="$target_dir/theme.txt"
    
    cat > "$theme_file" << 'EOF'
title-text: ""
desktop-image: "background.png"
terminal-left: "0"
terminal-top: "0"
terminal-border: "0"
terminal-width: "100%"
terminal-height: "100%"
+ boot_menu {
  left = 12%
  top = 20%
  width = 33%
  height = 62%
  item_color = "#ECE9DB"
  item_font = "DejaVu Sans Regular 14"
  selected_item_font = "DejaVu Sans Bold 14"
  selected_item_color = "#ECE9DB"
  icon_width = 48
  icon_height = 48
  item_icon_space = 20
  item_height = 64
  item_padding = 10
  item_spacing = 40
  selected_item_pixmap_style = "select_*.png"
  menu_pixmap_style = "../../_shared/boot_menu_*.png"
}
#progress bar
+ progress_bar {
	id = "__timeout__"
	left = 14%
	top = 80%
	height = 5%
	width = 29%
  font = "DejaVu Sans Bold 14"
	text_color = "#fff"
	fg_color = "#0066FF"
	border_color = "#000"
	bg_color = "#000"
	text = "Your OS will be booted in %d seconds"
}
EOF
}

# Vérifier l'argument
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <dossier>${NC}"
    echo "Exemple: $0 persona5_phantom_x"
    exit 1
fi

DOSSIER="$1"

if [ ! -d "$DOSSIER" ]; then
    echo -e "${RED}❌ Le dossier '$DOSSIER' n'existe pas!${NC}"
    exit 1
fi

echo "========================================"
echo "  GÉNÉRATION DES THEME.TXT"
echo "========================================"
echo -e "${BLUE}📂 Dossier: $DOSSIER${NC}\n"

total=0
created=0
skipped=0

# Parcourir tous les sous-dossiers
for dir in "$DOSSIER"/*/; do
    # Ignorer les dossiers spéciaux
    if [[ $(basename "$dir") == _* ]]; then
        continue
    fi
    
    folder_name=$(basename "$dir")
    ((total++))
    
    # Vérifier si theme.txt existe déjà
    if [ -f "$dir/theme.txt" ]; then
        echo -e "${YELLOW}⏭️  $folder_name - theme.txt existe déjà${NC}"
        ((skipped++))
        continue
    fi
    
    # Créer theme.txt
    echo -e "${GREEN}✅ $folder_name - création du theme.txt${NC}"
    create_theme_txt "$dir"
    ((created++))
done

# Résumé
echo ""
echo "========================================"
echo -e "${GREEN}✅ TERMINÉ!${NC}"
echo "========================================"
echo "Total de dossiers: $total"
echo -e "${GREEN}Créés: $created${NC}"
echo -e "${YELLOW}Ignorés (déjà présents): $skipped${NC}"
echo "========================================"
