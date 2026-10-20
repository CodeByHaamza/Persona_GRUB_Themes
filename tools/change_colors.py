#!/usr/bin/env python3
"""
Persona GRUB Theme - Selection Color Changer
Change les couleurs des images select_*.png pour chaque personnage
"""

import sys
from pathlib import Path
from PIL import Image

def changer_couleur_image(chemin_image, nouvelle_couleur):
    """
    Change les pixels non-noirs d'une image PNG en une nouvelle couleur
    
    Args:
        chemin_image: Path vers l'image PNG
        nouvelle_couleur: tuple RGB (r, g, b) de la nouvelle couleur
    """
    img = Image.open(chemin_image).convert('RGBA')
    pixels = img.load()
    
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            
            # Si le pixel n'est pas noir (tolérance pour quasi-noir)
            if not (r < 10 and g < 10 and b < 10):
                # Remplacer par la nouvelle couleur en gardant l'alpha
                pixels[x, y] = (nouvelle_couleur[0], nouvelle_couleur[1], nouvelle_couleur[2], a)
    
    img.save(chemin_image, 'PNG')

def hex_to_rgb(hex_color):
    """
    Convertit une couleur hexadécimale en tuple RGB
    
    Args:
        hex_color: string comme "#FF0000" ou "FF0000"
    
    Returns:
        tuple (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def traiter_personnage(dossier_perso, couleur_rgb):
    """
    Change la couleur des select_*.png pour un personnage
    
    Args:
        dossier_perso: Path vers le dossier du personnage
        couleur_rgb: tuple RGB (r, g, b)
    """
    fichiers_select = ['select_c.png', 'select_e.png', 'select_w.png']
    modifies = 0
    
    for fichier in fichiers_select:
        chemin = dossier_perso / fichier
        if chemin.exists():
            try:
                changer_couleur_image(chemin, couleur_rgb)
                modifies += 1
            except Exception as e:
                print(f"      ⚠️  Erreur avec {fichier}: {e}")
    
    return modifies

def parcourir_dossier(dossier_base):
    """
    Parcourt tous les sous-dossiers et demande la couleur pour chaque personnage
    
    Args:
        dossier_base: Path vers le dossier contenant les thèmes
    """
    print("=" * 70)
    print("  PERSONA GRUB THEME - COLOR CHANGER")
    print("=" * 70)
    print(f"\n📂 Dossier: {dossier_base}")
    print("\n💡 Instructions:")
    print("   • Appuyez sur ENTRÉE pour ignorer ce personnage")
    print("   • Entrez un code hexadécimal (ex: #FF0000 ou FF0000) pour changer la couleur")
    print("=" * 70)
    
    # Lister tous les sous-dossiers
    sous_dossiers = [d for d in dossier_base.iterdir() 
                     if d.is_dir() and not d.name.startswith('_')]
    
    if not sous_dossiers:
        print("\n❌ Aucun dossier de personnage trouvé!")
        return
    
    sous_dossiers = sorted(sous_dossiers)
    total_dossiers = len(sous_dossiers)
    dossiers_modifies = 0
    fichiers_modifies = 0
    
    print(f"\n📊 {total_dossiers} personnages trouvés\n")
    
    # Parcourir chaque sous-dossier
    for i, dossier_perso in enumerate(sous_dossiers, 1):
        nom_perso = dossier_perso.name
        
        # Vérifier si les fichiers select existent
        has_select = any((dossier_perso / f).exists() for f in ['select_c.png', 'select_e.png', 'select_w.png'])
        
        if not has_select:
            print(f"[{i}/{total_dossiers}] ⏭️  {nom_perso} - Pas de fichiers select_*.png")
            continue
        
        # Demander la couleur
        print(f"\n[{i}/{total_dossiers}] 🎨 Quelle couleur attribuer à [{nom_perso}] ?")
        reponse = input("      Couleur (ENTRÉE=ignorer): ").strip()
        
        # Si vide, on ignore
        if not reponse:
            print("      ⏭️  Ignoré")
            continue
        
        # Ajouter # si manquant
        if not reponse.startswith('#'):
            reponse = '#' + reponse
        
        # Valider le format
        if len(reponse) != 7:
            print("      ❌ Format invalide (attendu: #RRGGBB)")
            continue
        
        try:
            couleur_rgb = hex_to_rgb(reponse)
        except ValueError:
            print("      ❌ Code hexadécimal invalide")
            continue
        
        # Appliquer la couleur
        print(f"      🔄 Application de la couleur {reponse}...")
        nb_modifies = traiter_personnage(dossier_perso, couleur_rgb)
        
        if nb_modifies > 0:
            print(f"      ✅ {nb_modifies} fichier(s) modifié(s)")
            dossiers_modifies += 1
            fichiers_modifies += nb_modifies
        else:
            print("      ⚠️  Aucun fichier modifié")
    
    # Résumé final
    print("\n" + "=" * 70)
    print("✅ TRAITEMENT TERMINÉ!")
    print("=" * 70)
    print("📊 Statistiques:")
    print(f"   • Total de personnages: {total_dossiers}")
    print(f"   • Personnages modifiés: {dossiers_modifies}")
    print(f"   • Fichiers modifiés: {fichiers_modifies}")
    print("=" * 70)

def main():
    """Point d'entrée principal"""
    print()
    
    # Vérifier si un dossier est passé en argument
    if len(sys.argv) > 1:
        dossier_base = Path(sys.argv[1])
    else:
        # Demander le chemin du dossier
        print("📂 Veuillez spécifier le dossier à traiter:")
        chemin = input("   Chemin: ").strip()
        
        if not chemin:
            print("❌ Aucun chemin spécifié!")
            sys.exit(1)
        
        dossier_base = Path(chemin)
    
    # Vérifier que le dossier existe
    if not dossier_base.exists():
        print(f"\n❌ Le dossier '{dossier_base}' n'existe pas!")
        sys.exit(1)
    
    if not dossier_base.is_dir():
        print(f"\n❌ '{dossier_base}' n'est pas un dossier!")
        sys.exit(1)
    
    # Lancer le traitement
    parcourir_dossier(dossier_base)

if __name__ == "__main__":
    main()