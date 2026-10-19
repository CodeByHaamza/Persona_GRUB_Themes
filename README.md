# 🎭 Persona GRUB Themes Collection

<div align="center">

![Persona Banner](https://img.shields.io/badge/Persona-GRUB_Themes-E60012?style=for-the-badge&logo=linux&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge)](https://github.com/CodeByHaamza/Persona_GRUB_Themes/pulls)

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
        <img src="./previews/persona5_royal/oracle.png" width="250px" alt="Oracle">
        <br /><strong>Oracle</strong>
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
        <img src="./previews/persona5_phantom_x/closer.png" width="250px" alt="Closer">
        <br /><strong>Closer</strong>
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
        <img src="./previews/persona3_reload/aigis_fes.png" width="250px" alt="Aigis FES">
        <br /><strong>Aigis (FES)</strong>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="./previews/persona3_reload/shinji.png" width="250px" alt="Shinji">
        <br /><strong>Shinjiro</strong>
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

- 🎨 **68 Character Themes** across three Persona games
- 🎮 **Game Collections:**
  - Persona 5 Royal (13 themes)
  - Persona 5: The Phantom X (42 themes, 29 characters)
  - Persona 3 Reload (13 themes)
- 🔧 **Easy Installation** with interactive Python script
- 🎨 **Unique Color Scheme** for each character
- 📦 **Multiple Installation Methods** (Script, Manual, or Grub Customizer)
- 🃏 **Official All-Out Attack artwork** for every character
- 🔄 **Multiple Variants** for select characters (Beach, CNY, Special editions)
- 🐧 **Cross-Distribution Support** (Ubuntu, Debian, Arch, Fedora, openSUSE, and more)
- ↩️ **Safe Install**: original GRUB config backed up, one-command restore

## 📋 Table of Contents

- [Requirements](#-requirements)
- [Installation](#-installation)
- [Available Themes](#-available-themes)
- [Customization](#-customization)
- [Uninstallation](#-uninstallation)
- [Troubleshooting](#-troubleshooting)
- [Credits](#-credits)
- [License](#-license)
- [Contributing](#-contributing)

## 🔧 Requirements

### System Requirements
- Linux distribution with GRUB2
- Python 3.8 or higher
- Root/sudo access
- At least 50MB free space in `/boot`

### Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 grub2-common

# Fedora/RHEL
sudo dnf install python3 grub2-tools

# Arch Linux
sudo pacman -S python grub

# openSUSE
sudo zypper install python3 grub2
```

### Optional Tools
```bash
# grub-customizer for GUI theme management
sudo apt install grub-customizer
```

## 🚀 Installation

### Method 1: Interactive Script (Recommended)

1. **Clone the repository**
```bash
   git clone https://github.com/CodeByHaamza/Persona_GRUB_Themes.git
   cd Persona_GRUB_Themes
```

2. **Run the installer**
```bash
   sudo python3 install.py
```

3. **Follow the interactive prompts:**
   - Select your game (Persona 3 Reload / Persona 5 Royal / Persona 5: The Phantom X)
   - Choose your character from the list
   - Pick a variant if multiple versions are available
   - Confirm installation

4. **Reboot to see your new theme!**
```bash
   sudo reboot
```

#### Installer options
```bash
sudo python3 install.py --theme joker      # install a theme directly (folder name)
python3 install.py --list                  # list every available theme
sudo python3 install.py --dry-run          # show what would change, touch nothing
sudo python3 install.py --uninstall        # remove the Persona themes from GRUB
sudo python3 install.py --restore          # restore /etc/default/grub as it was before the first install
sudo python3 install.py --theme joker -y   # no questions (scripts)
```

The installer:
- detects `/boot/grub` or `/boot/grub2` and runs `update-grub`, `grub-mkconfig` or `grub2-mkconfig`,
- keeps your original `/etc/default/grub` in `/etc/default/grub.persona.orig` (never overwritten) and a timestamped backup on every change,
- sets `GRUB_GFXMODE` to your screen resolution if you have not set one,
- disables `GRUB_TERMINAL=console` / `GRUB_TERMINAL_OUTPUT="console"`, which prevent themes from showing.

### Method 2: Manual Installation

1. **Choose and copy your theme**
```bash
   # Example: Installing Joker theme
   sudo mkdir -p /boot/grub/themes
   sudo cp -r themes/persona5_royal/joker /boot/grub/themes/
```
   On Fedora / openSUSE / RHEL, use `/boot/grub2/themes` instead of `/boot/grub/themes` (also in `GRUB_THEME` below).

2. **Edit GRUB configuration**
```bash
   sudo nano /etc/default/grub
```
   
   Add or modify these lines:
```bash
   GRUB_THEME="/boot/grub/themes/joker/theme.txt"
   GRUB_GFXMODE=1920x1080
   GRUB_GFXPAYLOAD_LINUX=keep
```
   
   Comment out these lines if present:
```bash
   #GRUB_TERMINAL_OUTPUT="console"
   #GRUB_TERMINAL=console
```

3. **Update GRUB**
```bash
   # Ubuntu/Debian/Mint
   sudo update-grub
   
   # Arch/Manjaro
   sudo grub-mkconfig -o /boot/grub/grub.cfg
   
   # Fedora/openSUSE/RHEL 9+
   sudo grub2-mkconfig -o /boot/grub2/grub.cfg
   
   # Older RHEL/CentOS (UEFI)
   sudo grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg
```

4. **Reboot**
```bash
   sudo reboot
```

### Method 3: Using grub-customizer

1. **Install grub-customizer**
```bash
   sudo apt install grub-customizer  # Ubuntu/Debian
```

2. **Launch with sudo**
```bash
   sudo grub-customizer
```

3. **Navigate to Appearance Settings**
   - Click on `Appearance Settings` tab
   - Select `Theme` section

4. **Add the theme**
   - Click the `+` button
   - Navigate to `themes/persona5_royal/joker` (or your chosen theme)
   - Select the folder

5. **Apply and save**
   - Click `Save`
   - Reboot your system

## 🎨 Available Themes

### Persona 5 Royal (13 themes)
<details>
<summary>Click to expand character list</summary>

- **Joker** (Ren Amamiya) - Leader of the Phantom Thieves
- **Skull** (Ryuji Sakamoto) - The speedster
- **Panther** (Ann Takamaki) - The femme fatale
- **Mona** (Morgana) - The feline mascot
- **Fox** (Yusuke Kitagawa) - The eccentric artist
- **Queen** (Makoto Niijima) - The strategist
- **Oracle** (Futaba Sakura) - The hacker
- **Noir** (Haru Okumura) - The elegant fighter
- **Crow** (Goro Akechi) - The detective prince
- **Black Mask** (Goro Akechi) - Alternative form
- **Violet** (Kasumi Yoshizawa) - The gymnast
- **Caroline & Justine** - Twin wardens
- **Lavenza** - True form of the twins

</details>

### Persona 5: The Phantom X (42 themes)
<details>
<summary>Click to expand character list</summary>

- **Wonder** - Default, Beach, Chinese New Year, Valentine
- **Ange**
- **Berry**
- **Bui** - Default, Stellar
- **Cattle**
- **Cherish**
- **Chord**
- **Closer** - Default, Beach
- **Fleuret**
- **Howler**
- **Key**
- **Leon**
- **Luce** - Default, Notte
- **Marian** - Default, Beach
- **Matoi**
- **Messa**
- **Moko** - Default, Beach
- **Mont** - Default, Music
- **Okyann**
- **Phoebe**
- **Puppet** - Default, Beach
- **Riddle**
- **Rin** - Default, Chinese New Year
- **Sepia**
- **Soy** - Default, Frontiere
- **Turbo**
- **Vino**
- **Wind** - Default, Vast
- **Yuki**

</details>

### Persona 3 Reload (13 themes)
<details>
<summary>Click to expand character list</summary>

- **Makoto Yuki** - The protagonist
- **Yukari Takeba** - The archer
- **Junpei Iori** - The comic relief
- **Akihiko Sanada** - The boxer
- **Mitsuru Kirijo** - The leader
- **Fuuka Yamagishi** - The navigator
- **Aigis** - The android
- **Ken Amada** - The youngest member
- **Koromaru** - The loyal dog
- **Shinjiro Aragaki** - The lone wolf
- **Kotone Shiomi** (FeMC) - Female protagonist
- **Metis** - Aigis's sister
- **Aigis (FES)** - The Answer version

</details>

## 🎨 Customization

### Adjusting Screen Resolution

If the theme doesn't fit your screen properly:
```bash
sudo nano /etc/default/grub
```

Modify or add:
```bash
GRUB_GFXMODE=1920x1080  # Change to your resolution
GRUB_GFXPAYLOAD_LINUX=keep
```

Common resolutions:
- `1920x1080` (Full HD)
- `2560x1440` (2K)
- `3840x2160` (4K)
- `1366x768` (Laptop)

### Modifying Theme Elements

Each theme folder contains:
- `theme.txt` - Main configuration file
- `background.png` - Background image
- `select_*.png` - Selection highlight images
- `*.pf2` - Font files
- `icons/` - OS icons (if present)

You can customize any of these files to your liking.

### Creating Your Own Theme

1. Copy an existing theme as a template
2. Replace `background.png` with your image (1920x1080 recommended)
3. Adjust colors in `theme.txt`
4. Modify selection images if needed
5. Test with the installation script

## 🗑️ Uninstallation

### With the installer
```bash
sudo python3 install.py --uninstall   # remove the Persona themes and the GRUB_THEME line
sudo python3 install.py --restore     # or: put back your original /etc/default/grub
```

### Remove Specific Theme
```bash
sudo rm -rf /boot/grub/themes/[theme-name]
```

### Restore Default GRUB
```bash
# Edit GRUB config
sudo nano /etc/default/grub

# Remove or comment out the GRUB_THEME line:
#GRUB_THEME="/boot/grub/themes/..."

# Update GRUB
sudo update-grub  # Ubuntu/Debian
# OR
sudo grub-mkconfig -o /boot/grub/grub.cfg  # Arch
# OR
sudo grub2-mkconfig -o /boot/grub2/grub.cfg  # Fedora/openSUSE

# Reboot
sudo reboot
```

## 🐛 Troubleshooting

### Theme doesn't appear after installation

**Check GRUB configuration:**
```bash
grep GRUB_THEME /etc/default/grub
```

**Verify theme files exist:**
```bash
ls -la /boot/grub/themes/[theme-name]/theme.txt
```

**Regenerate GRUB config:**
```bash
sudo update-grub
```

### Low resolution or wrong aspect ratio

Edit `/etc/default/grub`:
```bash
GRUB_GFXMODE=1920x1080
GRUB_GFXPAYLOAD_LINUX=keep
```

### UEFI Secure Boot issues

Some systems with Secure Boot may not load custom themes. Options:
1. Disable Secure Boot in BIOS/UEFI
2. Sign the GRUB modules (advanced)
3. Use a distribution-provided theme

### Theme shows but images are missing

Ensure all theme files were copied:
```bash
sudo cp -r themes/persona5_royal/joker /boot/grub/themes/
```

### Grub doesn't show at boot

Edit `/etc/default/grub`:
```bash
GRUB_TIMEOUT=10  # Show menu for 10 seconds
#GRUB_HIDDEN_TIMEOUT=0  # Comment out this line
```

## 👏 Credits

### Inspiration & References
This project was heavily inspired by:
- **[StarRailGrubThemes](https://github.com/voidlhf/StarRailGrubThemes)** by voidlhf - Main inspiration for project structure and installation system
- **[Persona5GrubThemes](https://github.com/SiriusLL/Persona5GrubThemes)** by SiriusLL - Original Persona 5 Royal GRUB themes
- **[Starfield Theme](https://github.com/endlessm/grub/tree/master/themes/starfield)** - Reference for GRUB theme structure

### Asset Sources
- **All Out Attack Images**: Extracted from Persona 5 Royal game files
  - [Reddit Post 1](https://www.reddit.com/r/Persona5/comments/fxqgmf/p5r_clean_all_out_attack_finisher_images_ripped/)
  - [Reddit Post 2](https://imgur.com/gallery/1mtkoBr)
- **Persona 5X Assets**: From official game promotional materials
- **Persona 3 Reload Assets**: From official game and promotional materials
- **Distribution Icons**: [Uniform Linux Icon Set](https://www.reddit.com/r/linux/comments/nt1tm9/i_made_a_uniform_icon_set_of_linux_distribution/)
  - Icons color-adjusted to match each game's aesthetic

### Special Thanks
- **ATLUS/SEGA** - For creating the incredible Persona series
- **voidlhf** - For the StarRail GRUB themes that inspired this project
- **SiriusLL** - For the original Persona 5 GRUB themes
- All contributors and the Persona community

## 🤝 Contributing

Contributions are warmly welcomed! Here's how you can help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
```bash
   git checkout -b feature/AmazingNewTheme
```
3. **Make your changes**
   - Add new themes
   - Fix bugs
   - Improve documentation
4. **Commit your changes**
```bash
   git commit -m 'Add Persona 4 Golden themes'
```
5. **Push to your branch**
```bash
   git push origin feature/AmazingNewTheme
```
6. **Open a Pull Request**

### Contribution Ideas

- 🎨 **Add new character themes** that have an official All-Out Attack (new P5X characters, Persona 4 Revival on release...)
- 🗺️ **Pick an item** from the [Roadmap](./ROADMAP.md)
- 🐛 **Report bugs** or compatibility issues
- 📖 **Improve documentation** or add translations
- 💡 **Suggest features** or enhancements
- 🎭 **Create theme variants** (seasonal, alternate colors)
- 🔧 **Improve installation script** with new features

### Guidelines

- **Official All-Out Attacks only**: a character is added only if an official All-Out Attack finisher image exists for them (see the [Roadmap](./ROADMAP.md#-golden-rule-official-all-out-attacks-only))
- Follow existing theme structure
- Check readability with `python3 tools/check_contrast.py` (needs Pillow; `--fix` adjusts the text colours)
- Test themes before submitting
- Provide preview images
- Use high-quality assets
- Respect copyright and give credit

## 🐛 Known Issues

- Some distributions may require additional GRUB configuration tweaks
- Theme may not display on systems with UEFI Secure Boot enabled
- High-resolution displays (4K+) may need manual scaling adjustments
- Older GRUB versions (< 2.0) may have limited theme support

## 📞 Support

Need help? Have questions?

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/CodeByHaamza/Persona_GRUB_Themes/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/CodeByHaamza/Persona_GRUB_Themes/discussions)
- 📧 **Email**: [hamza.karrouchi.dev@gmail.com](mailto:hamza.karrouchi.dev@gmail.com)
- ⭐ **Star the repo** if you find it useful!

## ⭐ Show Your Support

If you enjoy this project, please consider:

- ⭐ **Starring the repository** on GitHub
- 🐛 **Reporting bugs** to help improve the project
- 💬 **Sharing with friends** who love Persona
- 🤝 **Contributing** new themes or improvements
- 📢 **Spreading the word** on social media

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/CodeByHaamza/Persona_GRUB_Themes?style=social)
![GitHub forks](https://img.shields.io/github/forks/CodeByHaamza/Persona_GRUB_Themes?style=social)
![GitHub issues](https://img.shields.io/github/issues/CodeByHaamza/Persona_GRUB_Themes)
![GitHub pull requests](https://img.shields.io/github/issues-pr/CodeByHaamza/Persona_GRUB_Themes)
![GitHub last commit](https://img.shields.io/github/last-commit/CodeByHaamza/Persona_GRUB_Themes)
![GitHub repo size](https://img.shields.io/github/repo-size/CodeByHaamza/Persona_GRUB_Themes)

---

<div align="center">

**Made with ❤️ by Persona fans, for Persona fans**

*"I am thou, thou art I... Thou hast acquired a new bootloader theme!"*

[![GitHub Profile](https://img.shields.io/badge/GitHub-CodeByHaamza-181717?style=for-the-badge&logo=github)](https://github.com/CodeByHaamza)
[![Email](https://img.shields.io/badge/Email-Contact_Me-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:hamza.karrouchi.dev@gmail.com)

[⬆ Back to top](#-persona-grub-themes-collection)

</div>