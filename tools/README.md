# 🛠️ Tools

The scripts that build, check and document the themes. Everything here is a
development tool: nothing in this folder is needed to *install* a theme, only to
rebuild one.

All of them are standard library only, except where Pillow is noted.

```bash
pip install pillow   # only for change_colors.py, check_contrast.py, readme_assets.py
```

---

## Building a theme

### `generate_theme_txt.sh`

Writes a default `theme.txt` into every character folder of a game that does not
have one yet. Existing files are left alone.

```bash
cd themes && ../tools/generate_theme_txt.sh persona5_phantom_x
```

### `copy_select_images.sh`

Copies the `select_*.png` selection bars from `persona5_royal/skull` into every
theme folder that is missing them.

```bash
cd themes && ../tools/copy_select_images.sh
```

### `change_colors.py`

Recolours the `select_*.png` selection bars of each character. It walks the
folders and asks for a hex colour per character, so it is the step that gives
every theme its own accent colour.

```bash
python3 tools/change_colors.py themes/persona3_reload
```

---

## Checking a theme

### `check_contrast.py`

Measures the contrast of the menu text, the selected item and the progress bar
against the artwork behind them, for all 68 themes. It is what the CI runs, so a
theme that fails here fails the build.

```bash
python3 tools/check_contrast.py          # report
python3 tools/check_contrast.py --fix    # rewrite theme.txt where it fails
```

Thresholds: menu ≥ 4.5, selected ≥ 3.0, progress bar ≥ 3.0.

---

## Previews

### `prev.py`

Renders a theme the way it will really look: it builds a bootable ISO with
`grub-mkrescue`, boots it in QEMU, and screenshots the GRUB menu. The result is
a genuine GRUB render, not a mock-up.

```bash
python3 tools/prev.py --list
python3 tools/prev.py --theme persona5_royal/joker
python3 tools/prev.py --folder persona3_reload
python3 tools/prev.py --all
```

It needs a Linux toolchain:

```bash
sudo apt install grub-common grub-pc-bin grub-efi-amd64-bin \
                 xorriso mtools qemu-system-x86 imagemagick
```

On Windows or macOS, run it in a container instead:

```bash
docker build -t grubbox tools/grubbox
docker run --rm -v "$PWD:/work" grubbox python3 tools/prev.py --all
```

`prev.py` screenshots in a loop until GRUB has actually drawn the theme, rather
than waiting a fixed time: a frame that is still blank has only one colour. With
KVM the theme appears after 2–3 s, without it after 15–20 s, so the same command
works either way. `--wait` sets the ceiling (60 s by default).

---

## Documentation

### `readme_assets.py`

Generates the animated README visuals (banner, quotes, game headers, dividers,
calling card), the thumbnails, the showcase GIF, and fills in the gallery of the
68 themes with the Arcana, the HD status and the All-Out Attack phrases.

```bash
python3 tools/readme_assets.py
```

Run it after `prev.py`, since the thumbnails come from `previews/`.

### `personadle_sync.py`

Compares the themes here with the official All-Out Attacks listed in
[personadle](https://github.com/CodeByHaamza/personadle), and reports the ones
that have no theme yet. A weekly GitHub Action runs it and opens an issue per
missing character.

```bash
python3 tools/personadle_sync.py
```

---

## Rebuilding everything

The order matters, because each step reads what the previous one wrote:

```bash
cd themes && ../tools/generate_theme_txt.sh persona5_phantom_x && cd ..
cd themes && ../tools/copy_select_images.sh && cd ..
python3 tools/change_colors.py themes/persona5_phantom_x
python3 tools/check_contrast.py --fix
python3 tools/prev.py --all          # ~40 min without KVM
python3 tools/readme_assets.py
```
