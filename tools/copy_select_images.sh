#!/bin/bash

# Script pour copier les select_*.png de skull vers tous les dossiers qui n'en ont pas
# Usage: ./copy_select_images.sh

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "  COPIE DES SELECT_*.PNG MANQUANTS"
echo "========================================"

# Dossier de référence contenant les select_*.png
SOURCE_DIR="persona5_royal/skull"

# Vérifier si le dossier source existe
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ Erreur: Le dossier $SOURCE_DIR n'existe pas!${NC}"
    exit 1
fi

# Vérifier si les fichiers source existent
if [ ! -f "$SOURCE_DIR/select_c.png" ] || [ ! -f "$SOURCE_DIR/select_e.png" ] || [ ! -f "$SOURCE_DIR/select_w.png" ]; then
    echo -e "${RED}❌ Erreur: Les fichiers select_*.png sont manquants dans $SOURCE_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Fichiers source trouvés dans $SOURCE_DIR${NC}\n"

# Compteurs
total=0
copied=0
skipped=0

# Fonction pour copier les select dans un dossier
copy_select_to_folder() {
    local target_dir="$1"
    local folder_name=$(basename "$target_dir")
    
    # Vérifier si les select_*.png existent déjà
    if [ -f "$target_dir/select_c.png" ] && [ -f "$target_dir/select_e.png" ] && [ -f "$target_dir/select_w.png" ]; then
        echo -e "${YELLOW}⏭️  $folder_name - déjà présent${NC}"
        ((skipped++))
        return
    fi
    
    # Copier les fichiers
    echo -e "${BLUE}📋 $folder_name${NC}"
    cp "$SOURCE_DIR/select_c.png" "$target_dir/" && echo "   ✓ select_c.png"
    cp "$SOURCE_DIR/select_e.png" "$target_dir/" && echo "   ✓ select_e.png"
    cp "$SOURCE_DIR/select_w.png" "$target_dir/" && echo "   ✓ select_w.png"
    ((copied++))
}

# Parcourir persona5_royal
echo -e "${BLUE}━━━ PERSONA 5 ROYAL ━━━${NC}"
if [ -d "persona5_royal" ]; then
    for dir in persona5_royal/*/; do
        # Ignorer les dossiers spéciaux
        if [[ $(basename "$dir") == _* ]]; then
            continue
        fi
        
        # Vérifier si c'est un dossier avec theme.txt
        if [ -f "$dir/theme.txt" ]; then
            ((total++))
            copy_select_to_folder "$dir"
        fi
    done
fi

# Parcourir persona3_reload
echo -e "\n${BLUE}━━━ PERSONA 3 RELOAD ━━━${NC}"
if [ -d "persona3_reload" ]; then
    for dir in persona3_reload/*/; do
        # Ignorer les dossiers spéciaux
        if [[ $(basename "$dir") == _* ]]; then
            continue
        fi
        
        # Vérifier si c'est un dossier avec theme.txt
        if [ -f "$dir/theme.txt" ]; then
            ((total++))
            copy_select_to_folder "$dir"
        fi
    done
fi

# Parcourir persona5_phantom_x
echo -e "\n${BLUE}━━━ PERSONA 5 PHANTOM X ━━━${NC}"
if [ -d "persona5_phantom_x" ]; then
    for dir in persona5_phantom_x/*/; do
        # Ignorer les dossiers spéciaux
        if [[ $(basename "$dir") == _* ]]; then
            continue
        fi
        
        # Vérifier si c'est un dossier avec theme.txt
        if [ -f "$dir/theme.txt" ]; then
            ((total++))
            copy_select_to_folder "$dir"
        fi
    done
fi

# Résumé
echo ""
echo "========================================"
echo -e "${GREEN}✅ TERMINÉ!${NC}"
echo "========================================"
echo "Total de dossiers traités: $total"
echo -e "${GREEN}Copiés: $copied${NC}"
echo -e "${YELLOW}Ignorés (déjà présents): $skipped${NC}"
echo "========================================"
