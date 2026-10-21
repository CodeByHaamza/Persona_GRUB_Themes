# 🗺️ Roadmap

This document lists everything planned for the next versions of **Persona GRUB Themes**: what is wrong today, what we want to add, and **how to integrate each item**.

Items are grouped by area and ordered by priority inside each section. Check a box when the item is merged.

---

## 📋 Table of Contents

- [Golden Rule: Official All-Out Attacks Only](#-golden-rule-official-all-out-attacks-only)
- [1. Audit of the Current State](#1-audit-of-the-current-state)
- [2. Image Quality](#2-image-quality)
- [3. New Characters](#3-new-characters)
- [4. Theme Design](#4-theme-design)
- [5. Installer](#5-installer)
- [6. Repository Structure & Build Pipeline](#6-repository-structure--build-pipeline)
- [7. CI / Automation](#7-ci--automation)
- [8. README & Documentation](#8-readme--documentation)
- [9. Distribution & Visibility](#9-distribution--visibility)
- [10. Full Persona Boot Experience](#10-full-persona-boot-experience)
- [11. Legal](#11-legal)
- [Done So Far](#-done-so-far)
- [To Do Later (needs Hamza)](#-to-do-later-needs-hamza)
- [Suggested Order](#-suggested-order)

---

## 🃏 Golden Rule: Official All-Out Attacks Only

Every character theme in this collection is built on an **official All-Out Attack (AOA) finisher image** from the games.

- ✅ A character is added **only if an official All-Out Attack finisher image exists** for them (or for that specific outfit/variant).
- ❌ No fan art, no edited promo art passed off as an AOA, no "made-up" themes for characters that never got an AOA.
- ❌ No themes based on Personas, locations or UI mock-ups as a replacement for a missing AOA.
- 📎 Every new theme must come with a **source link** for its AOA image (see [`SOURCES.md`](#26-sourcesmd)).

**How to integrate**
1. Add this rule to the `Guidelines` section of the README's Contributing part.
2. Add a "Character request" issue template that **requires** a link to the official AOA image (see [8.4](#84-issue-templates)).
3. Reject PRs without a verifiable AOA source.

---

## 1. Audit of the Current State

What was found while reviewing the repository (68 themes).

### 1.1 Backgrounds below 1920×1080

GRUB stretches `desktop-image` to the screen size, so any low-resolution background ends up blurry.

| Game | Theme | Current size |
|---|---|---|
| P5X | 41 of 42 themes | ~1000 px wide (Leon: 1290×701) |
| P5X | `puppet` | **680×384** (upscaled ×2.8) |
| P5X | `moko` | **736×414** (upscaled ×2.6) |
| P5X | `okyann` | 900×506 |
| P3R | `shinji` | 1280×720 |
| P3R | `kotone` | 1778×1000 |
| P3R | `fuuka` | 1000×430 |
| P5R | `black_mask`, `caroline_justine`, `lavenza` | ~1000×560 |

### 1.2 Wrong aspect ratio → stretched characters

✅ **Fixed.** Not by re-sourcing the artwork, but by telling GRUB to stop stretching it: `desktop-image-scale-method: "padding"` scales the image keeping its proportions and fills the rest with `desktop-color`, taken from the edges of the illustration so the band blends in. Applied to all themes by [`tools/fix_aspect.py`](tools/fix_aspect.py), checked by the CI, and verified by booting the themes in QEMU.

These backgrounds are ~1000×430 (close to 21:9). Before the fix, stretched to 16:9, the characters were **distorted vertically**, not just blurry:

`ange`, `berry`, `bui_cosmic`, `fleuret`, `key`, `luce`, `luce_notte`, `puppet_summer`, `soy_pioneer`, `turbo`, `vino`, `wonder_summer` (P5X) and `fuuka` (P3R).

The 10 P5R backgrounds at 3000×1680 are sharp, but:
- their ratio is 1.786 instead of 1.778 (no longer stretched, now a 3 px band),
- they weigh 3–5.6 MB each, which slows down the boot.

### 1.3 P5X images come from the Chinese promo

All P5X backgrounds carry the Chinese logo and the `©[2023] Perfect World` line. Global versions should be preferred when they exist (keep the copyright lines, see [11](#11-legal)).

### 1.4 Readability issues

- `fuuka`: black menu text on a dark background → nearly unreadable.
- The menu overlaps text printed in the artwork: "GO BEYOND" (`wonder`), "SUPPORT." (`fuuka`), "Shattered Dreams" (`puppet`).
- Progress bar colors are swapped: **dark red `#8B0000` on P3R** (a blue game), **blue `#0066FF` on P5X** (clashes with red characters like Wonder).
- `persona3_reload/junpei` uses the red P5 icon set instead of the P3R icons.
- No scrollbar pixmaps: with many entries, GRUB draws its default scrollbar.

### 1.5 Repository

- The 102 icons, fonts and selection images are **copied in all 68 themes** (~8,500 files). `.git` weighs **215 MB**.
- `themes/_shared/` already exists but is not used by anything.
- The development scripts (`change_colors.py`, `generate_theme_txt.sh`, `prev.py`) are git-ignored, so nobody can rebuild the themes.

### 1.6 README

- Links point to `HamzaKarrouchi/Persona_GRUB_Themes`, the repository is now `CodeByHaamza/Persona_GRUB_Themes`.
- Says "70+ themes" (there are 68) and "High-Quality Assets" (see 1.1).
- Only lists 8 P5X characters out of 42 themes, and shows 6 previews per game.
- Asks to install Pillow, but `install.py` does not use it.

### 1.7 Installer (`install.py`)

- `/boot/grub/themes` is hard-coded: **Fedora and openSUSE** use `/boot/grub2` and `grub2-mkconfig`, so the install fails there even though the README says they are supported.
- `/etc/default/grub.bak` is overwritten on every run: after a second install, the user's original config is lost.
- Never sets `GRUB_GFXMODE`, does not handle `GRUB_TERMINAL=console` (which also disables themes).
- No uninstall / restore option.
- Character colors and display names are hard-coded dictionaries: every new character requires a code change.

---

## 2. Image Quality

### 2.1 Fix the distorted themes first
- [ ] Replace or re-crop the 13 themes listed in [1.2](#12-wrong-aspect-ratio--stretched-characters).

**How to integrate:** find a 16:9 version of the same AOA image (see 2.2). If only the wide version exists, **pad** it to 16:9 (extend the background color/pattern above and below) instead of stretching it. Never stretch.

### 2.2 Get higher-resolution sources
- [ ] Re-source every background below 1920×1080 ([1.1](#11-backgrounds-below-19201080)).

**Where to look, in order of preference:**
1. **Game files (PC versions)**, which give native resolution and no watermark:
   - **P3R** (Unreal Engine 4) → [FModel](https://fmodel.app/) to browse and export the UI textures.
   - **P5R PC** (CPK archives) → Persona modding tools (e.g. CriFsV2Lib / Amicitia) to extract the AOA finisher textures.
   - **P5X Global** (Unity) → [AssetStudio](https://github.com/Perfare/AssetStudio) / [AssetRipper](https://github.com/AssetRipper/AssetRipper) for the AOA finisher of each character and outfit.
2. **Official channels**: official game websites, official P5X Global social accounts (new character and outfit announcements), official artbooks.
3. **Existing clean rips** shared by the community (credit them in `SOURCES.md`).

### 2.3 AI upscaling as a stopgap
- [ ] Upscale the current low-res images while waiting for better sources.

**How to integrate:** run [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) with the `realesrgan-x4plus-anime` model (or waifu2x / [Upscayl](https://upscayl.org/) for a GUI) on every background < 1920 px wide, then downscale to the target size. Mark these images as `upscaled: true` in `characters.yaml` (see [6.2](#62-charactersyaml-single-source-of-truth)) so they get replaced first when a real source is found.

### 2.4 Multiple resolutions and aspect ratios
- [ ] Generate each background in several sizes instead of shipping one huge PNG.

| Target | Size |
|---|---|
| Laptop | 1366×768 |
| Full HD | 1920×1080 |
| 2K | 2560×1440 |
| 4K | 3840×2160 |
| 16:10 | 1920×1200 / 2560×1600 |
| 3:2 | 2256×1504 |
| Ultrawide 21:9 | 2560×1080 / 3440×1440 |

**How to integrate:** store one master image per theme in `assets/` plus a **focal point** (x, y in %) in `characters.yaml`. `build.py` crops around the focal point for each ratio, then resizes. The installer picks the right size from the detected resolution (see [5.3](#53-resolution-detection)). This also fixes the P5R 1.786 ratio and the 3–5 MB files.

### 2.5 Compression
- [ ] Optimise every PNG (`oxipng -o 4 --strip safe`), or use high-quality JPEG (GRUB supports `.jpg`) for backgrounds. Expect 50–70 % smaller backgrounds and faster boots.

### 2.6 SOURCES.md
- [ ] Create `SOURCES.md` with, for each theme: game, character, outfit, AOA image source (link), **game the image was extracted from** (when different, e.g. Kotone Shiomi from P5X), extraction method, original resolution, upscaled yes/no.

---

## 3. New Characters

> ⚠️ Everything in this section follows the [Golden Rule](#-golden-rule-official-all-out-attacks-only): **a character is added only once its official All-Out Attack finisher image is found and linked.** The lists below are leads to check, not confirmed additions.

### 3.1 Persona 5: The Phantom X

**Reference list:** [personadle / allOutAttackMode](https://github.com/CodeByHaamza/personadle/tree/main/allOutAttackMode) has the official All-Out Attack of 80 characters and outfits (P3, P5, P5X). Its images are 800×450 animations, too small for GRUB, but they confirm **which official AOAs exist**, and the last frame shows which art to extract in high resolution from the game.

Compared with the original 68 themes, every P3 and P5 character was already in, and **12 P5X themes were missing**, all with an official AOA. **10 of them have now been added** from the official “Finishing Touch” illustrations on the [Megami Tensei Wiki](https://megamitensei.fandom.com/) — see [`SOURCES.md`](SOURCES.md). The wiki files P5X art under the character's **real name**, not their codename, which is what personadle's mapping is for.

| New theme | Folder | Type |
|---|---|---|
| Anri (Aran Hirano) | `anri` ❌ | New Phantom Idol |
| Pinky (Narumi Nashimoto) | `pinky` ✅ | New Phantom Idol |
| Blitz (Kumi Katayama) | `blitz` ✅ | New Phantom Idol |
| Miku (Hatsune Miku) | `miku` ✅ | Collaboration |
| Joker (Starlight) | `joker_starlight` ✅ | P5 character, P5X outfit |
| Mona (Starlight) | `mona_starlight` ✅ | P5 character, P5X outfit |
| Panther (Starlight) | `panther_starlight` ✅ | P5 character, P5X outfit |
| Wonder (Velvet) | `wonder_velvet` ✅ | Outfit (different from Valentine) |
| Wonder (Shujin) | `wonder_shujin` ✅ | Outfit |
| Closer (Radiance) | `closer_radiance` ❌ | Outfit |
| Chord (Summer) | `chord_summer` ✅ | Outfit |
| Berry (Summer) | `berry_summer` ✅ | Outfit |

The Starlight outfits come from P5X, so they go in `persona5_phantom_x/`. P5R keeps the original outfits. The collection is now at **78 themes**.

❌ **Anri** and **Closer (Radiance)** are still missing, and deliberately so. Anri only has promotional art on the wiki, not an All-Out Attack, and the Golden Rule forbids passing one off as the other. Closer Radiance (“Closer Sol” in English) only has a cut-out character render with no background or text. Both exist as animated captures in personadle, but at 640×360 and 800×450 with a capture ID burnt into the frame, below the quality of every theme here. See [`SOURCES.md`](SOURCES.md#known-gaps).

**Official outfit names:** personadle uses the official names (checked on lufel.net). Some current folders use datamine or approximate names. They are the same outfits, checked image by image:

| Old folder | Official name | New folder |
|---|---|---|
| `bui_stellar` | Bui Cosmic | `bui_cosmic` |
| `soy_frontiere` | Soy Pioneer | `soy_pioneer` |
| `wonder_beach`, `closer_beach`, `moko_beach`, `marian_beach`, `puppet_beach` | Summer | `wonder_summer`, `closer_summer`, `moko_summer`, `marian_summer`, `puppet_summer` |
| `wonder_cny`, `rin_cny` | Chinese New Year | keep (the display name is already "Chinese New Year") |
| `wind_vast`, `mont_music` | to check (personadle files: `Wind_V`, `Mount_Ice` / `Mount_Wind`) | keep until checked |

- [x] Rename the variants to their official names (folders, previews, display names in `install.py`). The old names still work with `install.py --theme`, and `--uninstall` also removes themes installed under an old name.
- [ ] Add the 12 missing themes above, extracted in high resolution from P5X.
- [ ] Keep the list up to date: each new P5X character or outfit added to personadle → a new theme here.
- [ ] For each one, find its official AOA finisher image → add it.
- [ ] Same for **new outfits** (seasonal, collab, event): each outfit with its own AOA becomes a variant (`<name>_<outfit>`), like the existing `wonder_summer`, `rin_cny`, etc.
- [ ] Replace the current P5X images with their Global versions when available.

### 3.2 Persona 5 Royal & spin-offs
- [ ] P5R: all playable Phantom Thieves are already in. Re-source the low-res ones (`black_mask`, `caroline_justine`, `lavenza`).
- [ ] **Persona 5 Strikers** and **Persona 5 Tactica**: check whether official AOA finisher images exist for their new characters. Add them only if they do.

### 3.3 Persona 3 Reload
- [ ] All party members are in. Re-source `shinji`, `kotone`, `fuuka`.
- [ ] **Kotone Shiomi** (P3 female protagonist, not Kotone Montagne / Mont from P5X): no need for the P3P FeMC mod anymore. She is in Persona 5: The Phantom X, so her official All-Out Attack is extracted from P5X. The theme **stays in `persona3_reload/`**; `SOURCES.md` notes that the image comes from P5X.
- [ ] **Fuuka**: she is also in Persona 5: The Phantom X → extract her official All-Out Attack from P5X. The current background is 1000×430 and stretched, so this is a big upgrade. The theme stays in `persona3_reload/`.
- [ ] Same idea for other characters that appear in several games: the theme stays in its original game, and the image comes from whichever game has the best official All-Out Attack.
- [ ] **Episode Aigis**: check for AOA finishers that differ from the base game.

### 3.4 Persona 4 Revival 🔜
Being first with P4 Revival themes on release day is the biggest visibility opportunity for the repo.

- [ ] **When Persona 4 Revival releases**, add the full cast from their official All-Out Attack finisher images.
- [ ] Theme assets in the P4 palette (yellow / black, TV static): selection pixmaps, progress bar, icons.
- [x] README: "coming soon" section with an animated P4 header (`game_p4r.svg`, yellow and black with TV static) and the official key art.
- [x] Installer: the P4 Revival colours are ready in `install_ui.py` (`GAME_STYLES["persona4_revival"]`) and its name in `install.py` (`GAME_NAMES`). The game appears as soon as `themes/persona4_revival/` has themes. Set `hero` to the protagonist's folder name.
- [ ] Do **not** create an empty `themes/persona4_revival/` folder before release: the installer would show a game with no themes.
- [ ] On release: extract the AOAs, add the themes, add a `<!-- gallery:persona4_revival -->` block and the game to `GAMES` in `tools/readme_assets.py`, replace the "coming soon" section with the gallery.

### 3.5 How to add a character (process)
1. Find the **official AOA image** and its source link.
2. Add an entry to `characters.yaml` (game, id, display name, outfit, colours, focal point, source).
3. Put the master image in `assets/<game>/<id>.png`.
4. Run `python3 tools/build.py <id>` → generates `themes/<game>/<id>/` and `previews/<game>/<id>.png`.
5. Check the preview (readability, menu position).
6. Open a PR with the source link.

Until the build pipeline ([6](#6-repository-structure--build-pipeline)) exists: copy an existing theme of the same game, replace `background.png`, adjust colours in `theme.txt`, add the preview, add the display name / colour in `install.py`.

---

## 4. Theme Design

### 4.1 Readability
- [x] Fix `fuuka` text colour (and every theme with black text on the dark menu panel).
- [ ] Add a **semi-transparent dark panel** behind the menu (`menu_pixmap_style` with ~60–70 % opacity), so text stays readable on any background.
- [ ] Make the **menu position configurable per theme** (left or right, depending on where the character is), so it never covers the character or the text printed in the artwork.
  - **The menu covers the character** (the menu is always on the left, 12–45 % of the width): `aigis_fes`, `yukari`, `mitsuru`, and partly `koromaru`. Move their menu to the right: in `theme.txt`, `left = 55%` for `boot_menu` and `left = 57%` for `progress_bar`. No new files needed, only the previews to regenerate afterwards. Check again with the HD images, in case the character is placed differently.
  - **The menu covers the text of the All-Out Attack** (not the character): `fuuka`, `lavenza`, `caroline_justine`, `ange`, `rin`, `messa`. Less urgent: decide case by case once the HD images are in.
- [x] Contrast checker: `tools/check_contrast.py` (`--fix` corrects `theme.txt`). Still to wire into CI (see [7.1](#71-theme-validation)).

### 4.2 Per-character colours
- [ ] Use each character's own colour for the selection bar, progress bar and icons (green icons for Oracle, teal for Fuuka…), instead of one colour per game.
- [x] Fix the swapped progress bar colours (red on P3R, blue on P5X): they now use each character's selection colour.
- [x] Fix the `junpei` icon set.

**How to integrate:** colours come from `characters.yaml`. `build.py` recolours the icons and selection pixmaps from the shared greyscale masks (the existing `change_colors.py` logic).

### 4.3 Game-styled UI
- [ ] **P5 / P5R / P5X**: slanted (parallelogram) selection bar, red / black / white, like the in-game menus.
- [ ] **P3R**: blue "water" style selection bar.
- [ ] **P4 Revival**: yellow / black with a TV-static touch.
- [ ] Matching **scrollbar pixmaps** (`scrollbar_frame` / `scrollbar_thumb`) for each game.

### 4.4 Countdown text
- [ ] Replace "Your OS will be booted in %d seconds" with a short themed line per game (P5: *"Taking your heart in %d…"*, P3R: *"Memento Mori — %d"*). Keep a plain English fallback option in the installer.

### 4.5 Fonts & HiDPI
- [ ] Ship fonts in several sizes (16 / 24 / 32 / 48) and icons in 32 / 48 / 64 / 96. DejaVu 14 is microscopic on a 4K screen.
- [ ] Add an open-licence display font closer to the Persona look (e.g. Anton, Bebas Neue, Oswald), converted with `grub-mkfont -s <size> font.ttf -o font_<size>.pf2`.
- [ ] Pick font and icon sizes from the target resolution at build/install time.

### 4.6 Extras
- [ ] Optional `+ label` with the game logo or the character name.
- [ ] Optional startup jingle with `GRUB_INIT_TUNE` (off by default).

---

## 5. Installer

### 5.1 Distro support (bug fixes first)
- [x] Detect the GRUB directory: `/boot/grub` or `/boot/grub2`.
- [x] Detect the update command: `update-grub`, `grub-mkconfig` or `grub2-mkconfig`, with the right output path (`/boot/grub2/grub.cfg` on Fedora / openSUSE).
- [x] Comment out `GRUB_TERMINAL=console` as well as `GRUB_TERMINAL_OUTPUT`.

### 5.2 Safe config handling
- [x] **Timestamped backups** (`/etc/default/grub.bak.2026-10-19_14-03-11`) and never overwrite the first original backup.
- [x] `--restore`: put back the original `/etc/default/grub` and regenerate GRUB.
- [x] `--uninstall`: remove the installed theme(s) and the `GRUB_THEME` line.
- [x] `--dry-run`: print what would change without touching anything.

### 5.3 Resolution detection
- [x] Read the screen resolution (`/sys/class/drm/*/modes`) and set `GRUB_GFXMODE=<res>,auto` when the user has not set one.
- [ ] Install the matching background size (see [2.4](#24-multiple-resolutions-and-aspect-ratios)).

### 5.4 Dual-boot
- [x] Offer to enable `os-prober` (`GRUB_DISABLE_OS_PROBER=false`). Many dual-boot users do not see Windows in the menu. The installer asks when `os-prober` is installed but switched off, and `--os-prober` does it without asking.

### 5.4b Velvet Room entry
- [x] `--velvet-room`: a "Velvet Room (UEFI Firmware Settings)" GRUB entry (`fwsetup`) with a butterfly icon, offered by the interactive installer on UEFI machines.

### 5.4c Ventoy
- [x] `--ventoy MOUNTPOINT`: install a theme on a Ventoy USB drive (`ventoy/themes/` + `ventoy/ventoy.json`), documented in the README.

### 5.5 Better interface
- [x] Persona flavour: ransom-note title, "Welcome to the Velvet Room.", a quote from the game after the install, "Take your time." when aborting.
- [x] Arrow-key interface (`install_ui.py`, standard library only): animated intro, P5-style diagonal transitions, game cards, character and outfit lists in each character's colour, live **colour preview of every theme in the terminal** (half-block pixels from `themes/_shared/terminal_previews.json`, built by `tools/readme_assets.py`), the All-Out Attack phrase, HD status, and a confirmation screen with the Velvet Room option. Falls back to numbered menus (`--plain`, `NO_COLOR`, no terminal).
- [ ] Search by name in the lists.
- [x] **Shuffle Time** (`--shuffle-time` or **S**): tarot cards are dealt, shuffled, a roulette slows down, and the chosen card flips over to reveal a random theme.
- [x] **Dark Hour**: between midnight and 1 a.m., the interface turns green (blood red stays) and the intro says the Dark Hour has begun. `PERSONA_DARK_HOUR=1` forces it, `0` disables it.
- [x] **Easter eggs**, each with its own animation: the Konami code (All-Out Attack), `igor` (a butterfly crosses the Velvet Room), `mona` (Morgana).
- [x] **Arcana** of each P3 and P5 character in the installer and the README gallery (`THEME_ARCANA` in `install.py`, from personadle's `database/characters_clean.js`).
  - [ ] P5X characters and Metis have no Arcana in personadle. Add them there first if they have an official one (e.g. from the Megami Tensei wiki), then here.
- [x] **6 languages** (`lang/*.json`: en, fr, de, es, it, pt, the same as personadle): system language by default, `--lang`, or **L** in the interface. Arcana names come from personadle's translations. Official game lines (All-Out Attack phrases, "Welcome to the Velvet Room.", "Looking cool, Joker!") stay as written in the games.
  - [ ] `character_names` in each language file can rename characters for one language. It is empty because personadle uses the same names in these 6 languages. For a Japanese translation, Oracle would become "Navi" there.
  - [ ] Technical messages (copy, GRUB update, `--dry-run`) are still in English.
- [x] Non-interactive CLI (`--theme`, `--list`, `--uninstall`, `--restore`, `--dry-run`, `-y`). Still to add: `--game`, `--random`.
- Planned CLI:
  ```bash
  sudo python3 install.py --game p5r --char joker
  sudo python3 install.py --list
  sudo python3 install.py --random
  sudo python3 install.py --uninstall
  sudo python3 install.py --restore
  sudo python3 install.py --dry-run
  ```

### 5.6 Data-driven
- [ ] Remove `CHARACTER_COLORS` and `CHARACTER_DISPLAY_NAMES` from the code: read them from `characters.yaml` (or a generated `themes/index.json` so the installer stays dependency-free).

### 5.7 Try before installing
- [ ] `install.py --try joker`: build a small GRUB ISO with the theme (`grub-mkrescue`) and boot it in QEMU, so users can see it without touching their bootloader.

### 5.8 Shuffle & seasonal modes
- [ ] **Shuffle**: a systemd service that swaps the installed `background.png` at shutdown. The theme path stays the same, so no GRUB regeneration is needed.
- [ ] **Seasonal**: automatically use the matching official variant when it exists (Beach in summer, CNY around Chinese New Year, Valentine on February 14).

### 5.9 Lightweight install
- [ ] One-line installer that downloads **only the selected theme** from the GitHub Releases instead of cloning 215 MB:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/CodeByHaamza/Persona_GRUB_Themes/main/get.sh | sudo bash -s -- joker
  ```

---

## 6. Repository Structure & Build Pipeline

### 6.1 Target layout
```
Persona_GRUB_Themes/
├── assets/                    # master AOA images (one per theme)
│   └── persona5_royal/joker.png
├── shared/                    # icons, fonts, pixmap masks (stored once)
│   ├── icons/
│   ├── fonts/
│   └── pixmaps/<game>/
├── characters.yaml            # single source of truth
├── tools/
│   ├── build.py               # generates themes/ + previews/ + index.json
│   ├── recolor.py             # (from change_colors.py)
│   └── preview.py             # (from prev.py)
├── themes/                    # generated (or built at install time)
├── previews/                  # generated
├── install.py
├── SOURCES.md
└── ROADMAP.md
```

### 6.2 characters.yaml (single source of truth)
```yaml
- id: joker
  game: persona5_royal
  name: Joker
  real_name: Ren Amamiya
  variant: Default
  colors:
    accent: "#E60012"
    text: "#ECE9DB"
    progress: "#EE2424"
  menu_side: left            # left | right
  focal_point: [70, 40]      # % of the image, used for cropping
  source:
    type: aoa                # always aoa (Golden Rule)
    url: https://...
    method: game files (CPK)
  upscaled: false
```

### 6.3 Steps
- [ ] Publish the existing scripts (`change_colors.py`, `generate_theme_txt.sh`, `prev.py`) under `tools/` and remove them from `.gitignore`.
- [ ] Write `characters.yaml` from the current 68 themes.
- [ ] Write `tools/build.py` (theme.txt from a template + recoloured shared assets + background crops + preview).
- [ ] Move shared files to `shared/`; have `build.py` (or `install.py`) assemble each theme. This removes ~8,000 duplicated files.
- [ ] Generate the README character tables and the installer's `index.json` from `characters.yaml`.
- [ ] **Colours from the artwork**: a script extracts the dominant colours of the All-Out Attack (k-means) and suggests the selection and progress bar colours. `tools/check_contrast.py` then checks readability. Adding a character becomes: drop the image, run the script.
- [ ] Optional: rewrite history (`git filter-repo`) or start a fresh `v2` branch to shrink the 215 MB `.git`, then tag `v2.0`.

---

## 7. CI / Automation

### 7.1 Theme validation
- [x] `tests/` (standard library only, `python3 -m unittest discover -s tests`) and `.github/workflows/tests.yml`, run on every pull request with Python 3.8 and 3.12:
  - installer: install, backups, restore, uninstall, `--dry-run`, user settings kept, old outfit names, numbered menus, French, Shuffle Time
  - Velvet Room, Ventoy, All-Out Attack phrases and Arcana
  - every theme complete, files referenced by `theme.txt`, previews, unique folder names
  - languages: same keys and placeholders in the 6 files
  - interface: rendering, previews, Dark Hour, and a real run in a pseudo-terminal
  - `pyflakes` and `tools/check_contrast.py`
- [ ] GitHub Action on every PR:
  - every `theme.txt` parses and every referenced file exists,
  - background ≥ 1920×1080 and the correct aspect ratio,
  - a preview exists for each theme,
  - `characters.yaml` entry has a `source.url` (Golden Rule),
  - text / background contrast in the menu area is above a threshold (WCAG ratio ≥ 4.5),
  - `python3 -m py_compile install.py` and a `--dry-run` in a container.

### 7.2 Real GRUB previews
- [ ] Generate the previews with **real GRUB**: `grub-mkrescue` an ISO with the theme → boot it in headless QEMU → `screendump`. The previews then match exactly what users get.

### 7.3 personadle tracking
- [x] Weekly GitHub Action (`.github/workflows/personadle-sync.yml` + `tools/personadle_sync.py`): every official All-Out Attack listed in personadle without a theme here gets a "[Missing theme]" issue, never twice.

### 7.4 Releases
- [ ] On tag push: build every theme, publish one `.tar.gz` per character + one archive per game in GitHub Releases, plus a `CHANGELOG.md` entry.

---

## 8. README & Documentation

### 8.1 Fixes
- [x] Update every link to `CodeByHaamza/Persona_GRUB_Themes`.
- [x] Correct the theme count. Still to generate it automatically (see [6](#6-repository-structure--build-pipeline)).
- [x] Remove Pillow from the dependencies (unless the installer starts using it).
- [x] Remove "High-Quality Assets" until 2.x is done.

### 8.2 Full gallery
- [x] Show **every** theme (generated tables, collapsible per game), not only 6 per game.
- [x] Animated showcase GIF at the top (`tools/readme_assets.py`).
- [x] HD status in the gallery (✅ HD / ⏳ HD soon) and an "HD artwork" progress badge, computed from the background size.
- [ ] Replace it with a **video of a real boot**.

### 8.3 Translations
- [ ] README in **Chinese** and **Japanese** (P5X is huge in Asia), plus **French**.

### 8.4 Issue templates
- [x] `.github/ISSUE_TEMPLATE/character_request.yml` with a **required** "Official All-Out Attack image link" field.
- [x] `bug_report.yml` asking for distro, GRUB version, BIOS / UEFI, resolution.
- [ ] GitHub Discussions with a poll for the next characters (among those with an official AOA).

### 8.5 Contributing
- [x] Golden Rule in the README Contributing guidelines.
- [ ] Add the "How to add a character" process ([3.5](#35-how-to-add-a-character-process)) to the README / a `CONTRIBUTING.md`.

---

## 9. Distribution & Visibility

- [ ] **Packages**: AUR (`persona-grub-themes`), Nix flake, Fedora COPR, `.deb`.
- [ ] **Pling / gnome-look.org** ("GRUB Themes" category).
- [ ] **GitHub Pages site**: gallery filterable by game / colour / character, with a click-to-copy install command.
- [ ] **Posts**: r/unixporn, r/Persona5, r/PERSoNA, r/P5X, r/linux, X / Twitter (#P5X), and a short boot video on YouTube Shorts / TikTok.
- [ ] Repository topics: `grub`, `grub-theme`, `persona`, `persona5`, `persona3`, `p5x`, `linux`, `ricing`.
- [ ] Social preview image (Settings → Social preview) showing several themes.

---

## 10. Full Persona Boot Experience

Matching themes for every step of the boot, built from the same official AOA images:

- [ ] **Plymouth** themes (boot splash after GRUB, can be animated).
- [ ] **SDDM** (KDE) and **GDM** (GNOME) login themes.
- [ ] **rEFInd** themes.
- [ ] Desktop wallpapers in all resolutions (already produced by `build.py`).
- [ ] Terminal colour schemes (kitty, alacritty, foot) and a **fastfetch** config per game.

**How to integrate:** each target gets its own folder (`plymouth/`, `sddm/`, `refind/`…) generated by `build.py` from `characters.yaml`, and an option in the installer (`--with plymouth,sddm`).

---

## 11. Legal

- [ ] State clearly in the README / LICENSE that **MIT covers the code only**; all artwork remains © ATLUS / © SEGA (and © Perfect World for P5X).
- [ ] **Never remove copyright lines** from official images.
- [ ] Credit every rip / source in `SOURCES.md`.
- [ ] Stay non-commercial.

---

## ✔️ Done So Far

| Area | What was done |
|---|---|
| Readability | `tools/check_contrast.py` measures menu / selected / progress bar text contrast for every theme and fixes `theme.txt` with `--fix`. 17 themes had black text on the dark menu panel, 25 had light text on light selection bars: all fixed. Fox and Noir got a darker menu panel. All 68 themes pass. |
| Progress bar | P3R and P5X progress bars now use each character's colour instead of one colour for the whole game. |
| Icons | `junpei` now uses the P3R icon set. |
| Installer | `/boot/grub` vs `/boot/grub2`, `update-grub` / `grub-mkconfig` / `grub2-mkconfig`, original config kept once + timestamped backups, `GRUB_TERMINAL=console` handled, `GRUB_GFXMODE` from the detected resolution, `--theme`, `--list`, `--uninstall`, `--restore`, `--dry-run`, `-y`. |
| README | Links, theme count, dependencies, full P5X list, installer options, Fedora / openSUSE commands, AOA rule. |
| Issues | Character request template (official AOA link required), bug report template. |
| Variant names | P5X outfits renamed to their official names: Bui Cosmic, Soy Pioneer, Summer (instead of Stellar, Frontiere, Beach). |
| Installer extras | Velvet Room entry (`--velvet-room`), Ventoy support (`--ventoy`), Persona-styled messages, and the phrase of each theme's All-Out Attack after the install (63/68). |
| Installer interface | Arrow-key menus with animations, game cards and a live colour preview of each theme in the terminal (`install_ui.py`). |
| Tests | 38 tests and a GitHub Action on every pull request (lint, tests, readability). |
| Installer fun | Shuffle Time, the Dark Hour, 3 animated easter eggs, Arcana, 6 languages. |
| HD tracking | ✅ / ⏳ per theme in the gallery and an "HD artwork 20/68" badge, updated by `tools/readme_assets.py`. |
| personadle tracking | Weekly GitHub Action opening a "[Missing theme]" issue for each official All-Out Attack without a theme. |
| Icons | The 102 distribution icons take the colour of each theme's character instead of being red everywhere, via `tools/recolor_icons.py`. Also fixed the pack's flattened colour variants (`alma_green`, `centos_blue`… were all red) and `mx_black`, a black logo on dark red at a contrast of 1.49. Rewritten as indexed PNG: 36.6 MB → 14.3 MB. |
| Stretched artwork | GRUB no longer stretches the illustrations: `desktop-image-scale-method: "padding"` with a `desktop-color` sampled from each artwork's edges, via `tools/fix_aspect.py`. Fixes the 14 backgrounds that are not 16:9, and any screen that is not 16:9. |
| New themes | 10 of the 12 missing P5X themes added from the official “Finishing Touch” art on the Megami Tensei Wiki, built by `tools/new_theme.py`. Kotone Shiomi now uses her **official** P5X All-Out Attack instead of a fan-made image. |
| Sources | [`SOURCES.md`](SOURCES.md) credits the artwork of every theme added since, and records the two characters whose AOA has no usable still. |
| README design | Animated Persona-styled banner, quotes, game headers, dividers and calling card; showcase GIF; full gallery of the 68 themes; star history chart. All generated by `tools/readme_assets.py`, which also fills the README gallery. |

---

## 🧑‍🎨 To Do Later (needs Hamza)

These items need files or actions that are not in the repository. Each one should land as its own PR.

### Needs the private scripts
- [ ] **Publish the dev scripts**: move `change_colors.py`, `generate_theme_txt.sh` and `prev.py` into `tools/`, remove them from `.gitignore`. Everything in [6](#6-repository-structure--build-pipeline) builds on them.
- [ ] **Regenerate the previews**: the readability and progress bar fixes changed the colours of 61 themes, so `previews/` no longer matches the themes exactly. Re-run `prev.py` on every theme, then `python3 tools/readme_assets.py` to refresh the README thumbnails and the showcase GIF.
- [ ] **Build pipeline**: turn the scripts into `tools/build.py` + `characters.yaml` (see [6.2](#62-charactersyaml-single-source-of-truth)).

### What extracting from the games actually costs

Tried, so the next person does not have to:

- **P5X** — the asset bundles are **encrypted** (UnityCN). The key is not in `global-metadata.dat`, `GameAssembly.dll`, `UnityPlayer.dll` or `P5X.exe`; it is built at runtime. The one P5X-specific tool (`Asset-Studio-P5X`) is from 2023 and is reported broken on current builds. Reading the key out of the running game would mean attaching to an online Perfect World title, which risks the account. **The wiki is the practical source.**
- **P3R** — the IoStore containers are AES-encrypted with a single default key. Scanning all 366 MB of `P3R.exe` for it found nothing, so it is assembled at runtime too. The wiki has the P3R All-Out Attack renders at up to 2048 px anyway, already cut out with transparency.
- **P5R** — the CPK archives open fine (CRILAYLA, no encryption), but the All-Out Attack finisher is **not stored as an image**: it is a rendered 3D scene (`BATTLE/EVENT/BCD/GOODBYE/*.EPL`). What is in there is the eye cut-ins (`BATTLE/CUTIN/BCT_P_BC*.DDS`, 3840×1536) and the art gallery (`MYPALACE/GALLERY/IMG/*.DDS`, up to 4096×4096) — both official and high resolution, but neither is an All-Out Attack finisher.

### Needs the images (official All-Out Attacks only)
- [x] **Kotone Shiomi** now uses her official P5X All-Out Attack, replacing the fan-made image ([`SOURCES.md`](SOURCES.md)). Stays in `persona3_reload/`.
- [ ] **Fuuka** from P5X (stays in `persona3_reload/`, see [3.3](#33-persona-3-reload)).
- [x] ~~**Re-source the 13 stretched themes**~~ — not needed: GRUB was told to stop stretching them instead ([1.2](#12-wrong-aspect-ratio--stretched-characters)).
- [ ] **Re-source the low-res backgrounds** ([1.1](#11-backgrounds-below-19201080)): P5X from the Global game files, P3R `shinji` / `kotone` / `fuuka`, P5R `black_mask` / `caroline_justine` / `lavenza`.
- [x] **10 of the 12 missing P5X themes** added from the wiki's official Finishing Touch art ([3.1](#31-persona-5-the-phantom-x)). Still missing: **Anri** (only promo art exists) and **Closer Radiance** (only a cut-out render) — see [`SOURCES.md`](SOURCES.md#known-gaps).
- [ ] **Persona 4 Revival** on release, from its official AOAs ([3.4](#34-persona-4-revival-)).
- [x] [`SOURCES.md`](SOURCES.md) created, with the source of every theme added since. The 67 older themes still need theirs filled in as they are re-sourced.

### All-Out Attack phrases
- [ ] Each theme shows the phrase written on its All-Out Attack after the install (`THEME_QUOTES` in `install.py`). 5 are missing because the text is cut, unreadable or absent on the current image: `mont_music`, `puppet_summer`, `rin`, `vino`, `yuki`. Add them from the HD images.

### personadle (the reference list)
- [ ] Add **Wonder (Valentine)** to personadle: it has an official AOA and a theme here, but is missing from the list.
- [ ] Check the official names of `wind_vast` and `mont_music` (personadle files: `Wind_V`, `Mount_Ice` / `Mount_Wind`), then rename them here if needed.

### Needs a decision
- [ ] Rewrite the git history to shrink the 215 MB `.git`, or start a clean `v2` (see [6.3](#63-steps)).
- [ ] Repository settings: topics, social preview image, enable Discussions.
- [ ] Packages (AUR, COPR, Nix) and posts (Reddit, Pling): they should wait for the new images.

### Can be done without Hamza (next PRs)
- [ ] CI workflow running `tools/check_contrast.py` and checking that every theme folder is complete.
- [x] Scrollbar pixmaps, one set per theme in the character's colour (`tools/add_scrollbar.py`), rather than per game ([4.3](#43-game-styled-ui)).
- [x] Installer: os-prober prompt ([5.4](#54-dual-boot)) and `--random`. TUI still open.
- [ ] Translations of the README ([8.3](#83-translations)).

---

## ✅ Suggested Order

1. **Images**: fix the 13 distorted themes, upscale or re-source the low-res ones (2.1 → 2.3).
2. **Installer bug fixes**: Fedora / openSUSE paths, backups, `GRUB_TERMINAL` (5.1, 5.2).
3. **README fixes** + Golden Rule in Contributing + issue templates (8.1, 8.4, 8.5).
4. **Build pipeline**: `characters.yaml` + `tools/build.py` + `shared/` (6).
5. **CI** validation and releases (7).
6. Add the **12 missing P5X themes** (3.1).
7. **Persona 4 Revival** on release day (3.4).
8. Design upgrades, installer TUI, distribution, full boot experience (4, 5.5+, 9, 10).
