#!/usr/bin/env python3
"""
Génère les visuels du README dans .github/readme/ :
  - banner.svg, quotes.svg, calling_card.svg      (SVG animés)
  - game_p5r.svg, game_p5x.svg, game_p3r.svg      (bandeaux par jeu)
  - divider_p5.svg, divider_p3.svg                (séparateurs animés)
  - showcase.gif                                  (diaporama des previews)
  - thumbs/<jeu>/<theme>.jpg                      (miniatures de la galerie)
et met à jour la galerie du README (entre les balises <!-- gallery:<jeu> -->)
ainsi que le badge de progression HD (<!-- hd-progress -->).

Le texte des SVG est converti en tracés : le rendu est identique partout,
même sans les polices installées.

Usage :
    python3 tools/readme_assets.py

Dépendances (outil de dev uniquement) : Pillow, fontTools, ffmpeg (optionnel, GIF plus léger)
"""
import glob
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes")
PREVIEWS_DIR = os.path.join(ROOT, "previews")
OUT_DIR = os.path.join(ROOT, ".github", "readme")
README = os.path.join(ROOT, "README.md")

RED = "#E60012"
DARK_RED = "#8B0010"
BLACK = "#0D0D0D"
WHITE = "#FFFFFF"
P3_BLUE = "#1E6BFF"
P3_NAVY = "#06102B"
P3_CYAN = "#7FE3FF"

FONT_FILES = {
    "inter_black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "inter_black_italic": "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf",
    "inter_bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "inter_light": "/usr/share/fonts/opentype/inter/InterDisplay-Light.otf",
    "inter_semibold": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "serif_bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold_italic": "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
    "dejavu_serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
}

GAMES = {
    "persona5_royal": "Persona 5 Royal",
    "persona5_phantom_x": "Persona 5: The Phantom X",
    "persona3_reload": "Persona 3 Reload",
}


# --- TEXTE -> TRACÉS SVG ---
class Font:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]
        self.cap_height = getattr(self.font["OS/2"], "sCapHeight", 0) or self.upm * 0.7

    def _glyph(self, char):
        return self.cmap.get(ord(char)) or self.cmap.get(ord("?"))

    def width(self, text, size, spacing=0):
        scale = size / self.upm
        advance = sum(self.hmtx[self._glyph(c)][0] for c in text) * scale
        return advance + spacing * max(len(text) - 1, 0)

    def cap(self, size):
        return self.cap_height * size / self.upm

    def path(self, text, size, x, y, spacing=0):
        """Tracé du texte, ligne de base en (x, y)"""
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs)
        cursor = x
        for char in text:
            glyph = self._glyph(char)
            self.glyphs[glyph].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
            cursor += self.hmtx[glyph][0] * scale + spacing
        return pen.getCommands()

    def centered(self, text, size, cx, cy, spacing=0):
        """Tracé centré horizontalement et verticalement (sur la hauteur des capitales)"""
        return self.path(text, size, cx - self.width(text, size, spacing) / 2, cy + self.cap(size) / 2, spacing)


FONTS = {name: Font(path) for name, path in FONT_FILES.items()}
RANSOM_FONTS = ["inter_black", "serif_bold", "sans_bold", "sans_bold_italic", "dejavu_serif_bold", "inter_black_italic"]
RANSOM_STYLES = [  # (fond, lettre)
    (BLACK, WHITE), (WHITE, BLACK), (RED, WHITE), (WHITE, RED), (BLACK, RED), (RED, BLACK),
]


def ransom(text, cx, cy, size, seed, delay=0.0, step=0.06, styles=RANSOM_STYLES, gap=6):
    """Lettres découpées façon carte de visite des Phantom Thieves. Retourne (svg, largeur)"""
    rng = random.Random(seed)
    letters = []
    for char in text:
        if char == " ":
            letters.append(None)
            continue
        font = FONTS[rng.choice(RANSOM_FONTS)]
        letter_size = size * rng.uniform(0.86, 1.08)
        bg, fg = rng.choice(styles)
        w = font.width(char, letter_size)
        letters.append((char, font, letter_size, bg, fg, w, rng.uniform(-9, 9), rng.uniform(-size * 0.08, size * 0.08)))

    pad = size * 0.16
    boxes = [(l[5] + pad * 2) if l else size * 0.32 for l in letters]
    total = sum(boxes) + gap * (len(boxes) - 1)
    x = cx - total / 2
    parts = []
    for i, (letter, box_w) in enumerate(zip(letters, boxes)):
        if letter:
            char, font, letter_size, bg, fg, w, angle, dy = letter
            h = font.cap(letter_size) + pad * 2.2
            lx = x + box_w / 2
            d = font.centered(char, letter_size, 0, 0)
            stroke = f' stroke="{BLACK}" stroke-width="2"' if bg != BLACK else ""
            parts.append(
                f'<g class="pop" style="animation-delay:{delay + i * step:.2f}s">'
                f'<g transform="translate({lx:.1f} {cy + dy:.1f}) rotate({angle:.1f})">'
                f'<rect x="{-box_w / 2:.1f}" y="{-h / 2:.1f}" width="{box_w:.1f}" height="{h:.1f}" fill="{bg}"{stroke}/>'
                f'<path d="{d}" fill="{fg}"/></g></g>'
            )
        x += box_w + gap
    return "".join(parts), total


def svg(width, height, body, style="", defs=""):
    reduced = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f"<style>{style}{reduced}</style><defs>{defs}</defs>{body}</svg>\n"
    )


P5_STYLE = """
.pop{animation:pop .45s cubic-bezier(.3,1.6,.5,1) both;transform-box:fill-box;transform-origin:center}
@keyframes pop{0%{transform:scale(0) rotate(-25deg);opacity:0}100%{transform:scale(1) rotate(0);opacity:1}}
.slide{animation:slide .8s cubic-bezier(.2,.9,.2,1) both}
@keyframes slide{0%{transform:translateX(-1400px)}100%{transform:translateX(0)}}
.slide-r{animation:slider .8s cubic-bezier(.2,.9,.2,1) both}
@keyframes slider{0%{transform:translateX(1400px)}100%{transform:translateX(0)}}
.spin{animation:spin 60s linear infinite;transform-box:fill-box;transform-origin:center}
@keyframes spin{to{transform:rotate(360deg)}}
.fade{animation:fade 1s ease both}
@keyframes fade{0%{opacity:0}100%{opacity:1}}
.flash{animation:flash 1.4s ease-out 1.2s both}
@keyframes flash{0%{transform:translateX(-400px) skewX(-25deg);opacity:0}20%{opacity:.9}100%{transform:translateX(1700px) skewX(-25deg);opacity:0}}
"""

HALFTONE = (
    f'<pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
    f'<circle cx="6" cy="6" r="2.4" fill="{RED}"/></pattern>'
    f'<pattern id="dots-dark" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
    f'<circle cx="6" cy="6" r="2.6" fill="#000" fill-opacity=".35"/></pattern>'
)


def star_points(cx, cy, outer, inner, spikes, rng=None):
    points = []
    for i in range(spikes * 2):
        r = outer if i % 2 == 0 else inner
        if rng:
            r *= rng.uniform(0.85, 1.12)
        angle = math.pi * i / spikes
        points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
    return " ".join(points)


def diamond(cx, cy, r, fill):
    return f'<polygon points="{cx},{cy - r} {cx + r},{cy} {cx},{cy + r} {cx - r},{cy}" fill="{fill}"/>'


def separated_line(segments, font, size, cy, total_width, fill, spacing=2.5, sep_fill=RED):
    """Texte centré avec des losanges entre les segments"""
    gap = size * 2.2
    widths = [font.width(s, size, spacing) for s in segments]
    total = sum(widths) + gap * (len(segments) - 1)
    x = (total_width - total) / 2
    parts = []
    for i, (segment, w) in enumerate(zip(segments, widths)):
        parts.append(f'<path d="{font.path(segment, size, x, cy + font.cap(size) / 2, spacing)}" fill="{fill}"/>')
        x += w
        if i < len(segments) - 1:
            parts.append(diamond(x + gap / 2, cy, size * 0.28, sep_fill))
            x += gap
    return "".join(parts)


# --- BANNIÈRE ---
def banner():
    w, h = 1280, 420
    rng = random.Random(5)
    title, _ = ransom("PERSONA", w / 2, 150, 92, seed=12, delay=0.5, step=0.07)
    sub_font = FONTS["inter_black_italic"]
    sub = "GRUB THEMES"
    sub_size = 56
    sub_w = sub_font.width(sub, sub_size, 4)
    bar_x = w / 2 - sub_w / 2 - 50
    body = f"""
<rect width="{w}" height="{h}" fill="{BLACK}"/>
<g class="fade"><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".22" mask="url(#fade-mask)"/></g>
<g class="spin" style="animation-delay:0s"><polygon points="{star_points(1080, 210, 330, 150, 14, rng)}" fill="{DARK_RED}" opacity=".55"/></g>
<g class="spin" style="animation-direction:reverse"><polygon points="{star_points(170, 260, 260, 110, 12, rng)}" fill="#1a1a1a"/></g>
<g class="slide"><polygon points="-40,70 1320,0 1320,70 -40,150" fill="{RED}"/></g>
<g class="slide-r" style="animation-delay:.15s"><polygon points="-40,250 1320,215 1320,290 -40,335" fill="{WHITE}"/></g>
<g class="slide" style="animation-delay:.25s"><polygon points="-40,262 1320,226 1320,281 -40,325" fill="{BLACK}"/></g>
<g class="slide-r" style="animation-delay:.35s"><polygon points="-40,345 1320,300 1320,312 -40,360" fill="{RED}"/></g>
{title}
<g class="slide" style="animation-delay:.9s">
  <polygon points="{bar_x + 30},{226} {bar_x + sub_w + 120},{218} {bar_x + sub_w + 90},{300} {bar_x},{306}" fill="{BLACK}" stroke="{RED}" stroke-width="4"/>
  <path d="{sub_font.centered(sub, sub_size, w / 2 + 5, 263 + 4, 4)}" fill="{RED}"/>
  <path d="{sub_font.centered(sub, sub_size, w / 2, 263, 4)}" fill="{WHITE}"/>
</g>
<g class="fade" style="animation-delay:1.3s">{separated_line(["PERSONA 5 ROYAL", "PERSONA 5: THE PHANTOM X", "PERSONA 3 RELOAD"], FONTS["inter_bold"], 17, 388, w, WHITE)}</g>
<rect class="flash" x="0" y="0" width="90" height="{h}" fill="{WHITE}"/>
"""
    defs = HALFTONE + (
        '<radialGradient id="fade-grad" cx=".75" cy=".5" r=".7"><stop offset="0" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#000"/></radialGradient>'
        f'<mask id="fade-mask"><rect width="{w}" height="{h}" fill="url(#fade-grad)"/></mask>'
    )
    return svg(w, h, body, P5_STYLE, defs)


# --- CITATIONS QUI S'ÉCRIVENT ---
QUOTES = [
    "I am thou, thou art I...",
    "Take your heart.",
    "Memento mori.",
    "Looking cool, Joker!",
    "Thou hast acquired a new bootloader theme!",
]


def quotes():
    w, h = 1280, 76
    font = FONTS["inter_black_italic"]
    size = 28
    slot = 4.0  # secondes par citation
    total = slot * len(QUOTES)
    body = [
        f'<rect x="140" y="8" width="1000" height="60" rx="6" fill="{BLACK}"/>',
        f'<polygon points="140,8 160,8 150,68 140,68" fill="{RED}"/>',
        f'<polygon points="1120,8 1140,8 1140,68 1110,68" fill="{RED}"/>',
        f'<rect width="0" height="0"><animate id="cycle" attributeName="width" from="0" to="0" dur="{total}s" begin="0s;cycle.end"/></rect>',
    ]
    defs = []
    for i, text in enumerate(QUOTES):
        tw = font.width(text, size, 1)
        x0 = w / 2 - tw / 2
        start = i * slot
        clip = f"clip{i}"
        defs.append(
            f'<clipPath id="{clip}"><rect x="{x0 - 4:.1f}" y="0" width="0" height="{h}">'
            f'<animate attributeName="width" values="0;0;{tw + 8:.1f};{tw + 8:.1f};0;0" '
            f'keyTimes="0;{start / total:.4f};{(start + 1.4) / total:.4f};{(start + 3.4) / total:.4f};{(start + 3.8) / total:.4f};1" '
            f'dur="{total}s" begin="cycle.begin"/></rect></clipPath>'
        )
        body.append(f'<path clip-path="url(#{clip})" d="{font.path(text, size, x0, 38 + font.cap(size) / 2, 1)}" fill="{WHITE}"/>')
        body.append(
            f'<rect y="22" width="12" height="32" fill="{RED}" opacity="0">'
            f'<animate attributeName="x" values="{x0:.1f};{x0:.1f};{x0 + tw + 6:.1f};{x0 + tw + 6:.1f};{x0:.1f};{x0:.1f}" '
            f'keyTimes="0;{start / total:.4f};{(start + 1.4) / total:.4f};{(start + 3.4) / total:.4f};{(start + 3.8) / total:.4f};1" '
            f'dur="{total}s" begin="cycle.begin"/>'
            f'<animate attributeName="opacity" values="0;1;0;1;0;1;0;1;0;0" calcMode="discrete" '
            f'keyTimes="0;{start / total:.4f};{(start + 1.6) / total:.4f};{(start + 2.0) / total:.4f};{(start + 2.4) / total:.4f};'
            f'{(start + 2.8) / total:.4f};{(start + 3.2) / total:.4f};{(start + 3.5) / total:.4f};{(start + 3.9) / total:.4f};1" '
            f'dur="{total}s" begin="cycle.begin"/></rect>'
        )
    return svg(w, h, "".join(body), "", "".join(defs))


# --- BANDEAUX PAR JEU ---
def count_themes(game):
    return len(glob.glob(os.path.join(THEMES_DIR, game, "*", "theme.txt")))


def tag(text, x, cy, font, size, bg, fg, skew=12):
    tw = font.width(text, size, 2)
    pad = 18
    h = font.cap(size) + 22
    return (
        f'<polygon points="{x + skew},{cy - h / 2} {x + tw + pad * 2 + skew},{cy - h / 2} {x + tw + pad * 2},{cy + h / 2} {x},{cy + h / 2}" fill="{bg}"/>'
        f'<path d="{font.centered(text, size, x + pad + tw / 2 + skew / 2, cy, 2)}" fill="{fg}"/>'
    )


def game_p5(game, title_line, kicker, seed, accent_shape):
    w, h = 1280, 180
    count = count_themes(game)
    title, title_w = ransom(title_line, 0, 0, 58, seed=seed, delay=0.3, step=0.04)
    tx = 70 + title_w / 2
    title, _ = ransom(title_line, tx, 100, 58, seed=seed, delay=0.3, step=0.04)
    kicker_svg = f'<path d="{FONTS["inter_black_italic"].path(kicker, 20, 72, 46, 3)}" fill="{RED}"/>' if kicker else ""
    body = f"""
<rect width="{w}" height="{h}" fill="{BLACK}"/>
<rect width="{w}" height="{h}" fill="url(#dots)" opacity=".18"/>
{accent_shape}
<g class="slide"><polygon points="-20,140 {tx + title_w / 2 + 140},128 {tx + title_w / 2 + 110},150 -20,160" fill="{RED}"/></g>
<g class="fade">{kicker_svg}</g>
{title}
<g class="slide-r" style="animation-delay:.6s">{tag(f"{count} THEMES", 1040, 100, FONTS["inter_black"], 26, WHITE, BLACK)}</g>
"""
    return svg(w, h, body, P5_STYLE, HALFTONE)


def game_p5r():
    rng = random.Random(3)
    accent = f'<g class="spin"><polygon points="{star_points(1150, 90, 150, 70, 12, rng)}" fill="{DARK_RED}" opacity=".7"/></g>'
    return game_p5("persona5_royal", "PERSONA 5 ROYAL", "", seed=21, accent_shape=accent)


def game_p5x():
    accent = (
        f'<g class="slide-r"><polygon points="900,-10 960,-10 1240,190 1180,190" fill="{RED}" opacity=".85"/>'
        f'<polygon points="1180,-10 1240,-10 960,190 900,190" fill="{WHITE}" opacity=".9"/></g>'
    )
    return game_p5("persona5_phantom_x", "THE PHANTOM X", "PERSONA 5", seed=34, accent_shape=accent)


P3_STYLE = """
.wave{animation:wave 9s linear infinite}
.wave2{animation:wave 14s linear infinite reverse}
@keyframes wave{to{transform:translateX(-400px)}}
.moon{animation:moon 5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes moon{0%,100%{opacity:.85;transform:scale(1)}50%{opacity:1;transform:scale(1.04)}}
.rise{animation:rise 1.1s cubic-bezier(.2,.9,.2,1) both}
@keyframes rise{0%{transform:translateY(30px);opacity:0}100%{transform:translateY(0);opacity:1}}
"""


def wave_path(y, amplitude, length, width):
    d = f"M0 {y}"
    x = 0
    while x < width + 800:
        d += f" q{length / 4} {-amplitude} {length / 2} 0 t{length / 2} 0"
        x += length
    return d


def game_p3r():
    w, h = 1280, 180
    count = count_themes("persona3_reload")
    title_font = FONTS["inter_light"]
    body = f"""
<rect width="{w}" height="{h}" fill="url(#p3bg)"/>
<g class="moon"><circle cx="1110" cy="70" r="46" fill="url(#moon)"/><circle cx="1110" cy="70" r="80" fill="{P3_CYAN}" opacity=".08"/></g>
<g class="wave" opacity=".35"><path d="{wave_path(140, 10, 200, w)}" stroke="{P3_CYAN}" stroke-width="2" fill="none"/></g>
<g class="wave2" opacity=".25"><path d="{wave_path(155, 8, 160, w)}" stroke="{WHITE}" stroke-width="1.5" fill="none"/></g>
<g class="wave" opacity=".18"><path d="{wave_path(168, 6, 260, w)}" stroke="{P3_CYAN}" stroke-width="1.5" fill="none"/></g>
<g class="rise">
  <path d="{FONTS["inter_bold"].path("MEMENTO MORI", 16, 72, 52, 6)}" fill="{P3_CYAN}"/>
  <path d="{title_font.path("PERSONA 3 RELOAD", 56, 70, 112, 6)}" fill="{WHITE}"/>
  <rect x="72" y="126" width="120" height="3" fill="{P3_BLUE}"/>
</g>
<g class="rise" style="animation-delay:.3s">
  <rect x="860" y="84" width="170" height="40" fill="none" stroke="{WHITE}" stroke-width="2"/>
  <path d="{FONTS["inter_semibold"].centered(f"{count} THEMES", 20, 945, 104, 3)}" fill="{WHITE}"/>
</g>
"""
    defs = (
        f'<linearGradient id="p3bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{P3_NAVY}"/>'
        f'<stop offset=".6" stop-color="#0B2A6B"/><stop offset="1" stop-color="{P3_BLUE}"/></linearGradient>'
        f'<radialGradient id="moon"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".7" stop-color="#E8FBFF"/>'
        f'<stop offset="1" stop-color="{P3_CYAN}"/></radialGradient>'
    )
    return svg(w, h, body, P3_STYLE, defs)


# --- SÉPARATEURS ---
def divider_p5():
    w, h = 1280, 22
    shards = "".join(
        f'<polygon points="{x},{h} {x + 14},0 {x + 44},0 {x + 30},{h}" fill="{RED if (x // 60) % 3 else BLACK}"/>'
        for x in range(-120, w + 240, 60)
    )
    style = ".run{animation:run 3s linear infinite}@keyframes run{to{transform:translateX(120px)}}"
    return svg(w, h, f'<g class="run">{shards}</g>', style)


def divider_p3():
    w, h = 1280, 22
    body = (
        f'<g class="wave"><path d="{wave_path(11, 7, 160, w)}" stroke="{P3_BLUE}" stroke-width="2.5" fill="none"/></g>'
        f'<g class="wave2" opacity=".6"><path d="{wave_path(12, 5, 220, w)}" stroke="{P3_CYAN}" stroke-width="1.5" fill="none"/></g>'
    )
    return svg(w, h, body, P3_STYLE)


# --- CARTE DE VISITE ---
def calling_card():
    w, h = 1000, 600
    rng = random.Random(9)
    card_w, card_h = 760, 470
    cx, cy = w / 2, h / 2
    x0, y0 = cx - card_w / 2, cy - card_h / 2
    body_font = FONTS["inter_bold"]
    lines = [
        "To the user still booting into a plain black-and-white menu,",
        "you are a sinner who has forgotten what a stylish boot feels like.",
        "We have decided to make you confess your crimes with our own hands.",
    ]
    text = "".join(
        f'<path d="{body_font.centered(line, 17, cx, y0 + 70 + i * 32)}" fill="{BLACK}"/>' for i, line in enumerate(lines)
    )
    line1, _ = ransom("WE WILL TAKE", cx, y0 + 215, 46, seed=41, delay=0.4, step=0.05)
    line2, _ = ransom("YOUR BOOTLOADER", cx, y0 + 300, 44, seed=42, delay=1.0, step=0.05)
    sign_font = FONTS["inter_black_italic"]
    body = f"""
<rect width="{w}" height="{h}" fill="{RED}"/>
<rect width="{w}" height="{h}" fill="url(#dots-dark)"/>
<g class="spin"><polygon points="{star_points(cx, cy, 520, 260, 16, rng)}" fill="{BLACK}" opacity=".25"/></g>
<g class="float">
  <g transform="rotate(-2 {cx} {cy})">
    <rect x="{x0 + 10}" y="{y0 + 12}" width="{card_w}" height="{card_h}" fill="#000" opacity=".45"/>
    <rect x="{x0}" y="{y0}" width="{card_w}" height="{card_h}" fill="#F7F3EA" stroke="{BLACK}" stroke-width="6"/>
    <polygon points="{x0},{y0} {x0 + 120},{y0} {x0},{y0 + 90}" fill="{RED}"/>
    <polygon points="{x0 + card_w},{y0 + card_h} {x0 + card_w - 120},{y0 + card_h} {x0 + card_w},{y0 + card_h - 90}" fill="{BLACK}"/>
    {text}
    {line1}
    {line2}
    <g class="fade" style="animation-delay:1.9s">
      <path d="{sign_font.centered("— THE PHANTOM THIEVES OF HEARTS", 20, cx, y0 + 390, 2)}" fill="{RED}"/>
      <path d="{FONTS["inter_semibold"].centered("Star the repo to send your own calling card", 14, cx, y0 + 425, 1)}" fill="#555"/>
    </g>
  </g>
</g>
"""
    style = P5_STYLE + (
        ".float{animation:float 6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-8px) rotate(.8deg)}}"
    )
    return svg(w, h, body, style, HALFTONE)


# --- MINIATURES ET DIAPORAMA ---
def thumbnails():
    count = 0
    for preview in sorted(glob.glob(os.path.join(PREVIEWS_DIR, "*", "*.png"))):
        game = os.path.basename(os.path.dirname(preview))
        out = os.path.join(OUT_DIR, "thumbs", game, os.path.basename(preview)[:-4] + ".jpg")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        image = Image.open(preview).convert("RGB")
        image.thumbnail((480, 270), Image.LANCZOS)
        image.save(out, "JPEG", quality=84, optimize=True, progressive=True)
        count += 1
    return count


SHOWCASE = [
    ("persona5_royal", "joker", "Joker"),
    ("persona5_phantom_x", "wonder", "Wonder"),
    ("persona3_reload", "makoto", "Makoto Yuki"),
    ("persona5_royal", "queen", "Queen"),
    ("persona5_phantom_x", "puppet", "Puppet"),
    ("persona3_reload", "aigis", "Aigis"),
    ("persona5_royal", "violet", "Violet"),
    ("persona5_phantom_x", "rin_cny", "Rin (Chinese New Year)"),
    ("persona3_reload", "mitsuru", "Mitsuru"),
    ("persona5_royal", "crow", "Crow"),
]


def pil_font(name, size):
    return ImageFont.truetype(FONT_FILES[name], size)


def label(image, character, game):
    """Étiquette en bas à gauche : nom du perso + jeu"""
    draw = ImageDraw.Draw(image)
    p3 = "persona3" in game
    accent = (30, 107, 255) if p3 else (230, 0, 18)
    big, small = pil_font("inter_black_italic", 26), pil_font("inter_bold", 13)
    name = character.upper()
    nw = draw.textlength(name, font=big)
    gw = draw.textlength(GAMES[game].upper(), font=small)
    x, y, hgt = 18, image.height - 70, 40
    width = max(nw, gw) + 40
    draw.polygon([(x + 10, y), (x + width + 10, y), (x + width, y + hgt), (x, y + hgt)], fill=(13, 13, 13))
    draw.polygon([(x, y + hgt), (x + width, y + hgt), (x + width - 2, y + hgt + 6), (x - 2, y + hgt + 6)], fill=accent)
    draw.text((x + 18, y + 5), name, font=big, fill=(255, 255, 255))
    draw.text((x + 14, y + hgt + 9), GAMES[game].upper(), font=small, fill=(255, 255, 255),
              stroke_width=3, stroke_fill=(13, 13, 13))


def showcase():
    size = (640, 360)
    slides = []
    for game, theme, name in SHOWCASE:
        image = Image.open(os.path.join(PREVIEWS_DIR, game, theme + ".png")).convert("RGB").resize(size, Image.LANCZOS)
        label(image, name, game)
        slides.append((image, game))

    frames, durations = [], []
    w, h = size
    for i, (image, game) in enumerate(slides):
        frames.append(image)
        durations.append(2200)
        nxt, next_game = slides[(i + 1) % len(slides)]
        accent = (30, 107, 255) if "persona3" in next_game else (230, 0, 18)
        # Transition façon P5 : un éclat coloré balaie l'écran en diagonale
        for step in range(1, 9):
            t = step / 9
            frame = image.copy()
            mask = Image.new("L", size, 0)
            edge = -260 + (w + 260) * t
            ImageDraw.Draw(mask).polygon([(-300, 0), (edge + 160, 0), (edge, h), (-300, h)], fill=255)
            frame.paste(nxt, (0, 0), mask)
            draw = ImageDraw.Draw(frame)
            draw.polygon([(edge + 160, 0), (edge + 240, 0), (edge + 80, h), (edge, h)], fill=accent)
            draw.polygon([(edge + 240, 0), (edge + 262, 0), (edge + 102, h), (edge + 80, h)], fill=(13, 13, 13))
            frames.append(frame)
            durations.append(35)

    out = os.path.join(OUT_DIR, "showcase.gif")
    if shutil.which("ffmpeg"):
        # ffmpeg compresse beaucoup mieux (palette commune + seules les zones modifiées sont réécrites)
        with tempfile.TemporaryDirectory() as tmp:
            lines = []
            for i, (frame, duration) in enumerate(zip(frames, durations)):
                frame.save(os.path.join(tmp, f"{i:03d}.png"))
                lines.append(f"file '{tmp}/{i:03d}.png'\nduration {duration / 1000}")
            lines.append(f"file '{tmp}/{len(frames) - 1:03d}.png'")
            with open(os.path.join(tmp, "list.txt"), "w") as f:
                f.write("\n".join(lines))
            subprocess.run([
                "ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt"),
                "-vf", "split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
                "-loop", "0", out,
            ], check=True)
    else:
        palette_frames = [f.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
        palette_frames[0].save(out, save_all=True, append_images=palette_frames[1:], duration=durations, loop=0, optimize=True)
    return out


# --- GALERIE DU README ---
# Ordre d'affichage : l'équipe dans l'ordre du jeu, puis le reste par ordre alphabétique
ORDER = {
    "persona5_royal": ["joker", "skull", "panther", "morgana", "fox", "queen", "oracle", "noir", "crow", "violet"],
    "persona5_phantom_x": ["wonder", "wonder_valentine", "wonder_summer", "wonder_cny"],
    "persona3_reload": ["makoto", "kotone", "yukari", "junpei", "akihiko", "mitsuru", "fuuka", "aigis", "aigis_fes",
                        "ken", "koromaru", "shinji", "metis"],
}
VISIBLE = 6
COLUMNS = 3
NAMES = {"aigis_fes": "Aigis (FES)"}


def is_hd(game, theme):
    """Fond d'au moins 1920x1080 et en 16:9 (à 1 % près) : sinon, l'image est à ré-extraire"""
    with Image.open(os.path.join(THEMES_DIR, game, theme, "background.png")) as bg:
        w, h = bg.size
    return w >= 1920 and h >= 1080 and abs(w / h - 16 / 9) / (16 / 9) < 0.01


def gallery_rows(game, themes):
    import install  # noms d'affichage des variantes (wonder_cny -> Wonder (Chinese New Year))
    cells = []
    for theme in themes:
        name = NAMES.get(theme) or install.CHARACTER_DISPLAY_NAMES.get(theme) or theme.replace("_", " ").title()
        cells.append(
            f'<td align="center"><a href="previews/{game}/{theme}.png">'
            f'<img src=".github/readme/thumbs/{game}/{theme}.jpg" width="260" alt="{name}"></a>'
            f"<br><b>{name}</b><br><sub>{'✅ HD' if is_hd(game, theme) else '⏳ HD soon'}</sub></td>"
        )
    rows = ["<tr>" + "".join(cells[i:i + COLUMNS]) + "</tr>" for i in range(0, len(cells), COLUMNS)]
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def gallery(game):
    themes = sorted(os.path.basename(os.path.dirname(p))
                    for p in glob.glob(os.path.join(THEMES_DIR, game, "*", "theme.txt")))
    order = ORDER.get(game, [])
    themes.sort(key=lambda t: (order.index(t) if t in order else len(order), t))
    themes = [t for t in themes if os.path.exists(os.path.join(OUT_DIR, "thumbs", game, t + ".jpg"))]
    html = '<div align="center">\n\n' + gallery_rows(game, themes[:VISIBLE]) + "\n"
    if len(themes) > VISIBLE:
        html += (f"\n<details>\n<summary><b>Show {len(themes) - VISIBLE} more {GAMES[game]} themes</b></summary>\n<br>\n\n"
                 + gallery_rows(game, themes[VISIBLE:]) + "\n\n</details>\n")
    return html + "\n</div>"


def hd_badge():
    themes = [p.split(os.sep)[-3:-1] for p in glob.glob(os.path.join(THEMES_DIR, "*", "*", "theme.txt"))]
    hd = sum(is_hd(game, theme) for game, theme in themes)
    color = "2EA043" if hd == len(themes) else "E60012"
    return (f"[![HD artwork](https://img.shields.io/badge/HD_artwork-{hd}%2F{len(themes)}-{color}"
            f"?style=for-the-badge&labelColor=0D0D0D)](#-the-gallery)")


def update_readme():
    sys.path.insert(0, ROOT)
    with open(README) as f:
        text = f.read()
    text = re.sub(r"(<!-- hd-progress -->).*?(<!-- /hd-progress -->)", lambda m: m.group(1) + hd_badge() + m.group(2), text)
    for game in GAMES:
        pattern = re.compile(rf"(<!-- gallery:{game} -->).*?(<!-- /gallery:{game} -->)", re.S)
        text = pattern.sub(lambda m: m.group(1) + "\n" + gallery(game) + "\n" + m.group(2), text)
    with open(README, "w") as f:
        f.write(text)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = {
        "banner.svg": banner(),
        "quotes.svg": quotes(),
        "game_p5r.svg": game_p5r(),
        "game_p5x.svg": game_p5x(),
        "game_p3r.svg": game_p3r(),
        "divider_p5.svg": divider_p5(),
        "divider_p3.svg": divider_p3(),
        "calling_card.svg": calling_card(),
    }
    for name, content in files.items():
        with open(os.path.join(OUT_DIR, name), "w") as f:
            f.write(content)
        print(f"{name:20} {len(content) // 1024} KB")
    print(f"thumbs               {thumbnails()} files")
    gif = showcase()
    print(f"showcase.gif         {os.path.getsize(gif) // 1024} KB")
    update_readme()
    print("README.md            gallery updated")


if __name__ == "__main__":
    main()
