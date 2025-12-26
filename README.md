# 🎭 Persona GRUB Themes Collection

<div align="center">

![Persona Banner](https://img.shields.io/badge/Persona-GRUB_Themes-E60012?style=for-the-badge&logo=linux&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge)](https://github.com/yourusername/Persona_GRUB_Themes/pulls)

**Transform your GRUB bootloader into a stylish Persona experience!**

*Featuring themes from Persona 5 Royal, Persona 5: The Phantom X, and Persona 3 Reload*

</div>

---
## 📸 Previews

### 🎭 Persona 5 Royal
<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="./previews/persona5_royal/joker.png" width="250px" alt="Joker">
        <br /><strong>Joker</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_royal/violet.png" width="250px" alt="Violet">
        <br /><strong>Violet</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_royal/crow.png" width="250px" alt="Crow">
        <br /><strong>Crow</strong>
      </td>
    </tr>
     <tr>
      <td align="center">
        <img src="./previews/persona5_royal/queen.png" width="250px" alt="Queen">
        <br /><strong>Queen</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_royal/oracle.png" width="250px" alt="Navi">
        <br /><strong>Navi (Oracle)</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_royal/fox.png" width="250px" alt="Fox">
        <br /><strong>Fox</strong>
      </td>
    </tr>
  </table>
</div>

### ✖️ Persona 5: The Phantom X
<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="./previews/persona5_phantom_x/wonder.png" width="250px" alt="Wonder">
        <br /><strong>Wonder</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_phantom_x/wonder_valentine.png" width="250px" alt="Wonder Valentine">
        <br /><strong>Wonder (Valentine)</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_phantom_x/messa.png" width="250px" alt="Messa">
        <br /><strong>Messa</strong>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="./previews/persona5_phantom_x/bui.png" width="250px" alt="Bui">
        <br /><strong>Bui</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_phantom_x/rin.png" width="250px" alt="Rin">
        <br /><strong>Rin</strong>
      </td>
      <td align="center">
        <img src="./previews/persona5_phantom_x/closer.png" width="250px" alt="Motoha">
        <br /><strong>Motoha (Closer)</strong>
      </td>
    </tr>
  </table>
</div>

### 🌕 Persona 3 Reload
<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="./previews/persona3_reload/makoto.png" width="250px" alt="Makoto">
        <br /><strong>Makoto</strong>
      </td>
      <td align="center">
        <img src="./previews/persona3_reload/kotone.png" width="250px" alt="Kotone">
        <br /><strong>Kotone</strong>
      </td>
      <td align="center">
        <img src="./previews/persona3_reload/aigis_fes.png" width="250px" alt="Aigis">
        <br /><strong>Aigis ( FES )</strong>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="./previews/persona3_reload/shinji.png" width="250px" alt="Shinji">
        <br /><strong>Shinji</strong>
      </td>
      <td align="center">
        <img src="./previews/persona3_reload/metis.png" width="250px" alt="Metis">
        <br /><strong>Metis</strong>
      </td>
      <td align="center">
        <img src="./previews/persona3_reload/junpei.png" width="250px" alt="Junpei">
        <br /><strong>Junpei</strong>
      </td>
    </tr>
  </table>
</div>

## ✨ Features

- 🎨 **70+ Character Themes** across three Persona games
- 🎮 **Game Collections:**
  - Persona 5 Royal (13 characters)
  - Persona 5: The Phantom X (42+ characters)
  - Persona 3 Reload (13 characters)
- 🔧 **Easy Installation** with interactive Python script
- 🎨 **Color-coded Interface** for each character
- 📦 **Multiple Installation Methods** (Script, Manual, or Grub Customizer)
- 🖼️ **High-Quality Assets** from official game sources
- 🔄 **Multiple Variants** for select characters (Beach, CNY, Special editions)

## 📋 Table of Contents

- [Requirements](#-requirements)
- [Installation](#-installation)
- [Available Themes](#-available-themes)
- [Customization](#-customization)
- [Uninstallation](#-uninstallation)
- [Credits](#-credits)
- [License](#-license)
- [Contributing](#-contributing)

## 🔧 Requirements

### System Requirements
- Linux distribution with GRUB2
- Python 3.8 or higher
- Root/sudo access

### Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pil grub2-common

# Fedora/RHEL
sudo dnf install python3 python3-pillow grub2-tools

# Arch Linux
sudo pacman -S python python-pillow grub
```

### Optional (for manual customization)
```bash
# ImageMagick for image processing
sudo apt install imagemagick

# grub-customizer for GUI management
sudo apt install grub-customizer
```

## 🚀 Installation

### Method 1: Interactive Script (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Persona_GRUB_Themes.git
   cd Persona_GRUB_Themes
   ```

2. **Run the installer**
   ```bash
   sudo python3 install.py
   ```

3. **Follow the interactive prompts:**
   - Select your game (Persona 3/5/5X)
   - Choose your character
   - Pick a variant (if available)
   - Confirm installation

4. **Reboot to see your new theme!**
   ```bash
   sudo reboot
   ```

### Method 2: Manual Installation

1. **Download and extract a theme**
   ```bash
   # Download from releases or use a specific theme folder
   cd themes/persona5_royal/joker
   ```

2. **Copy to GRUB themes directory**
   ```bash
   sudo mkdir -p /boot/grub/themes
   sudo cp -r joker /boot/grub/themes/
   ```

3. **Edit GRUB configuration**
   ```bash
   sudo nano /etc/default/grub
   ```
   
   Add or modify this line:
   ```
   GRUB_THEME="/boot/grub/themes/joker/theme.txt"
   ```
   
   Comment out this line if present:
   ```
   #GRUB_TERMINAL_OUTPUT="console"
   ```

4. **Update GRUB**
   ```bash
   # Ubuntu/Debian
   sudo update-grub
   
   # Fedora/Arch/Other
   sudo grub-mkconfig -o /boot/grub/grub.cfg
   ```

5. **Reboot**
   ```bash
   sudo reboot
   ```

### Method 3: Using grub-customizer

1. Install grub-customizer
2. Open grub-customizer with sudo
3. Go to `Appearance Settings` → `Theme`
4. Click `+` and navigate to your theme folder
5. Select the theme and apply
6. Save and reboot

## 🎨 Available Themes

### Persona 5 Royal
- Joker (Ren Amamiya)
- Skull (Ryuji Sakamoto)
- Panther (Ann Takamaki)
- Mona (Morgana)
- Fox (Yusuke Kitagawa)
- Queen (Makoto Niijima)
- Oracle (Futaba Sakura)
- Noir (Haru Okumura)
- Crow (Goro Akechi)
- Black Mask (Goro Akechi)
- Violet (Kasumi Yoshizawa)
- Caroline & Justine
- Lavenza

### Persona 5: The Phantom X
*42+ characters including Wonder, Cattle, Mont, Closer, and many more!*

### Persona 3 Reload
- Makoto Yuki
- Yukari Takeba
- Junpei Iori
- Akihiko Sanada
- Mitsuru Kirijo
- Fuuka Yamagishi
- Aigis
- Ken Amada
- Koromaru
- Shinjiro Aragaki
- Kotone Shiomi (FeMC)
- Metis
- Aigis (FES)

## 🎨 Customization

### Changing Selection Colors

Use the included Python script to customize selection colors:

```bash
cd themes
python3 change_colors.py persona5_royal
```

The script will prompt you for each character, allowing you to:
- Press ENTER to skip
- Enter a hex color code (e.g., `#FF0000` or `FF0000`)

### Manual Color Editing

Edit `select_*.png` files in each theme folder or modify `theme.txt` for advanced customization.

## 🗑️ Uninstallation

### Remove Specific Theme
```bash
sudo rm -rf /boot/grub/themes/[theme-name]
```

### Restore Default GRUB
```bash
# Edit GRUB config
sudo nano /etc/default/grub

# Remove or comment out:
# GRUB_THEME="/boot/grub/themes/..."

# Update GRUB
sudo update-grub  # or sudo grub-mkconfig -o /boot/grub/grub.cfg

# Reboot
sudo reboot
```

## 👏 Credits

### Inspiration & References
This project was heavily inspired by:
- **[StarRailGrubThemes](https://github.com/voidlhf/StarRailGrubThemes)** by voidlhf - The main inspiration for this project's structure and installation script
- **[Persona5GrubThemes](https://github.com/SiriusLL/Persona5GrubThemes)** by SiriusLL - Original Persona 5 Royal GRUB themes
- **[Starfield Theme](https://github.com/endlessm/grub/tree/master/themes/starfield)** - Reference for theme structure

### Asset Sources
- **All Out Attack Images**: Ripped from Persona 5 Royal
  - [Reddit Post 1](https://www.reddit.com/r/Persona5/comments/fxqgmf/p5r_clean_all_out_attack_finisher_images_ripped/)
  - [Reddit Post 2](https://imgur.com/gallery/1mtkoBr)
- **Distribution Icons**: [Linux Icon Set](https://www.reddit.com/r/linux/comments/nt1tm9/i_made_a_uniform_icon_set_of_linux_distribution/)
  - Icons were color-adjusted to match each game's theme

### Special Thanks
- **ATLUS** - For creating the Persona series
- All contributors who helped expand the theme collection

## 📜 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### Important Notice
**All Persona artwork, characters, and game assets are © ATLUS.** This project is a fan-made tribute and is not affiliated with or endorsed by ATLUS. All rights to the original content belong to their respective copyright holders.

If you are a copyright holder and have concerns about the use of any assets in this project, please [contact us](mailto:hamza.karrouchi.dev@gmail.com) and we will address the issue promptly.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Ways to Contribute
- 🎨 Add new character themes
- 🐛 Report bugs or issues
- 📖 Improve documentation
- 🌍 Add translations
- 💡 Suggest new features

## 🐛 Known Issues

- Some distributions may require additional GRUB configuration
- Theme may not work with UEFI Secure Boot (disable or add exception)
- High-resolution displays may need scaling adjustments

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/HamzaKarrouchi/Persona_GRUB_Themes/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HamzaKarrouchi/Persona_GRUB_Themes/discussions)
- **Email**: hamza.karrouchi.dev@gmail.com

## ⭐ Show Your Support

If you like this project, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💬 Sharing with friends
- 🤝 Contributing

---

<div align="center">

**Made with ❤️ by Persona fans, for Persona fans**

*"I am thou, thou art I..."*

[![GitHub Stars](https://img.shields.io/github/stars/HamzaKarrouchi/Persona_GRUB_Themes?style=social)](https://github.com/HamzaKarrouchi/Persona_GRUB_Themes)
[![GitHub Forks](https://img.shields.io/github/forks/HamzaKarrouchi/Persona_GRUB_Themes?style=social)](https://github.com/HamzaKarrouchi/Persona_GRUB_Themes/fork)
[![GitHub Issues](https://img.shields.io/github/issues/HamzaKarrouchi/Persona_GRUB_Themes)](https://github.com/HamzaKarrouchi/Persona_GRUB_Themes/issues)

</div>