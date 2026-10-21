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

### `recolor_icons.py`

Gives the 102 distribution icons the colour of each theme's character, taken
from `fg_color` in `theme.txt`. It darkens or lightens that colour where the
logo would not be readable on it, and writes the icons as indexed PNG.

```bash
python3 tools/recolor_icons.py --all
python3 tools/recolor_icons.py --theme persona3_reload/makoto
python3 tools/recolor_icons.py --check    # what the CI runs
```

### `fix_aspect.py`

Stops GRUB stretching the artwork. By default GRUB scales `desktop-image` to
the edges of the screen, which distorts every background that is not exactly
the screen's ratio. This writes `desktop-image-scale-method: "padding"` into
each `theme.txt`, with a `desktop-color` sampled from the edges of the artwork
so the band blends in rather than showing black.

```bash
python3 tools/fix_aspect.py --all
python3 tools/fix_aspect.py --check       # what the CI runs
```

### `add_scrollbar.py`

Gives each theme a scrollbar in its character's colour. Without pixmaps GRUB
draws its own plain grey one as soon as there are more boot entries than fit,
which looks nothing like the theme.

```bash
python3 tools/add_scrollbar.py --all
python3 tools/add_scrollbar.py --check    # what the CI runs
```

The slices are 1×1, like `boot_menu_c.png`. With 5×5 slices GRUB silently gives
up on drawing the scrollbar below roughly 60 px wide, because the corners do not
fit; at 1×1 any width works.

---

## Adding a theme

### `new_theme.py`

Builds a whole theme from one All-Out Attack illustration: it takes an existing
theme as a template, swaps the artwork in, and recolours the selection bars and
the 102 icons to the character's colour. That colour is read off the
illustration unless `--accent` says otherwise.

```bash
python3 tools/new_theme.py --game persona5_phantom_x --name blitz \
    --art blitz.png --from wonder
python3 tools/check_contrast.py --fix
python3 tools/fix_aspect.py --all
python3 tools/prev.py --theme persona5_phantom_x/blitz
```

Every theme must be built on an **official All-Out Attack image**: see the
Golden Rule in [`ROADMAP.md`](../ROADMAP.md) and credit the source in
[`SOURCES.md`](../SOURCES.md).

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
python3 tools/recolor_icons.py --all
python3 tools/fix_aspect.py --all
python3 tools/add_scrollbar.py --all
python3 tools/prev.py --all          # ~40 min without KVM
python3 tools/readme_assets.py
```
