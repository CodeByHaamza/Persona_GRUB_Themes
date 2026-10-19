#!/usr/bin/env python3
"""
Interface terminal de l'installeur : menus aux flèches, aperçu en couleur de chaque
thème directement dans le terminal, animations façon Persona.

install.py l'utilise quand le terminal le permet, sinon il garde les menus numérotés.
Aucune dépendance : uniquement la bibliothèque standard de Python.
"""
import base64
import json
import math
import os
import random
import select
import shutil
import struct
import sys
import unicodedata
import time
import zlib

import install_i18n
from install_i18n import t

try:
    import termios
    import tty
except ImportError:  # pas de terminal POSIX (Windows)
    termios = None

PWD = os.path.dirname(os.path.realpath(__file__))
PREVIEWS_FILE = os.path.join(PWD, "themes", "_shared", "terminal_previews.json")

# --- COULEURS ---
RED = (230, 0, 18)
DARK_RED = (120, 0, 12)
BLACK = (13, 13, 13)
WHITE = (255, 255, 255)
GREY = (120, 120, 120)
DIM = (70, 70, 70)
P3_BLUE = (30, 107, 255)
P3_NAVY = (6, 16, 43)
P3_CYAN = (127, 227, 255)

GAME_STYLES = {
    "persona5_royal": {"accent": RED, "bg": BLACK, "title": "PERSONA 5 ROYAL", "tagline": "TAKE YOUR HEART",
                       "hero": "joker"},
    "persona5_phantom_x": {"accent": RED, "bg": (22, 8, 10), "title": "PERSONA 5: THE PHANTOM X",
                           "tagline": "GO BEYOND", "hero": "wonder"},
    "persona3_reload": {"accent": P3_BLUE, "bg": P3_NAVY, "title": "PERSONA 3 RELOAD", "tagline": "MEMENTO MORI",
                        "hero": "makoto"},
    # Prêt pour la sortie de Persona 4 Revival : affiché dès que themes/persona4_revival/ a des thèmes
    "persona4_revival": {"accent": (255, 212, 0), "bg": (20, 18, 6), "title": "PERSONA 4 REVIVAL",
                         "tagline": "REACH OUT TO THE TRUTH", "hero": "yu"},
}

# (fond, lettre) des lettres découpées : sur fond noir, et sur la bande rouge des en-têtes P5
RANSOM_STYLES = [(RED, WHITE), (WHITE, BLACK), (CHARCOAL := (52, 52, 52), WHITE), (WHITE, RED), (RED, BLACK)]
RANSOM_ON_RED = [(WHITE, BLACK), (BLACK, WHITE), (WHITE, RED)]


def available():
    """Interface stylée seulement dans un vrai terminal qui gère les couleurs"""
    if termios is None or os.environ.get("NO_COLOR") or os.environ.get("PERSONA_PLAIN"):
        return False
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return False
    return os.environ.get("TERM", "") not in ("", "dumb", "linux")


def truecolor():
    """sudo efface COLORTERM : on se fie aussi à TERM, que sudo garde"""
    if os.environ.get("PERSONA_COLORS") == "256":
        return False
    term = os.environ.get("TERM", "")
    return (os.environ.get("COLORTERM") in ("truecolor", "24bit")
            or term.endswith("256color") or any(t in term for t in ("kitty", "alacritty", "foot", "wezterm")))


def rgb_to_256(rgb):
    r, g, b = rgb
    if abs(r - g) < 10 and abs(g - b) < 10:
        return 232 + min(23, max(0, round((r - 8) / 10)))
    return 16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def luminance(rgb):
    return (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255


def text_on(rgb):
    return BLACK if luminance(rgb) > 0.6 else WHITE


def dark_hour():
    """La Dark Hour de P3 : entre minuit et 1 h (ou PERSONA_DARK_HOUR=1 pour la voir)"""
    if os.environ.get("PERSONA_DARK_HOUR"):
        return os.environ["PERSONA_DARK_HOUR"] == "1"
    return time.localtime().tm_hour == 0


def dark_hour_tint(rgb):
    """Tout devient vert, sauf le rouge du sang qui reste visible"""
    r, g, b = rgb
    l = luminance(rgb)
    green = (int(15 + l * 80), int(35 + l * 210), int(20 + l * 95))
    reddish = r > g + 60 and r > b + 60
    return mix(rgb, green, 0.35 if reddish else 0.85)


def char_width(char):
    return 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1


def text_width(text):
    return sum(char_width(c) for c in text)


# --- APERÇUS ---
class Previews:
    def __init__(self):
        self.width = self.height = 0
        self.themes = {}
        try:
            with open(PREVIEWS_FILE) as f:
                data = json.load(f)
            self.width, self.height, self.themes = data["width"], data["height"], data["themes"]
        except (OSError, ValueError, KeyError):
            pass
        self.cache = {}

    def pixels(self, key):
        if key not in self.themes:
            return None
        if key not in self.cache:
            self.cache[key] = zlib.decompress(base64.b64decode(self.themes[key]))
        return self.cache[key]

    def scaled(self, key, w, h):
        """Image réduite à w x h pixels (moyenne des pixels de chaque zone)"""
        raw = self.pixels(key)
        if raw is None:
            return None
        sw, sh = self.width, self.height
        rows = []
        for y in range(h):
            y0, y1 = y * sh // h, max(y * sh // h + 1, (y + 1) * sh // h)
            row = []
            for x in range(w):
                x0, x1 = x * sw // w, max(x * sw // w + 1, (x + 1) * sw // w)
                r = g = b = n = 0
                for yy in range(y0, y1):
                    base = (yy * sw) * 3
                    for xx in range(x0, x1):
                        i = base + xx * 3
                        r += raw[i]
                        g += raw[i + 1]
                        b += raw[i + 2]
                        n += 1
                row.append((r // n, g // n, b // n))
            rows.append(row)
        return rows


# --- CANEVAS ---
class Canvas:
    """Grille de cellules (caractère, couleur du texte, fond, style) rendue en une fois"""

    def __init__(self, w, h, bg=BLACK):
        self.w, self.h = w, h
        self.cells = [[[" ", WHITE, bg, ""] for _ in range(w)] for _ in range(h)]

    def put(self, x, y, char, fg=None, bg=None, style=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            cell = self.cells[y][x]
            cell[0] = char
            if fg is not None:
                cell[1] = fg
            if bg is not None:
                cell[2] = bg
            if style is not None:
                cell[3] = style

    def text(self, x, y, text, fg=WHITE, bg=None, style=""):
        for char in text:
            self.put(x, y, char, fg, bg, style)
            if char_width(char) == 2:
                self.put(x + 1, y, "", fg, bg, style)  # 2e colonne d'un caractère large
            x += char_width(char)
        return x

    def center(self, y, text, fg=WHITE, bg=None, style="", x0=0, w=None):
        w = self.w if w is None else w
        return self.text(x0 + (w - text_width(text)) // 2, y, text, fg, bg, style)

    def fill(self, x, y, w, h, bg, char=" ", fg=WHITE):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, char, fg, bg, "")

    def box(self, x, y, w, h, color, heavy=False):
        tl, tr, bl, br, hz, vt = ("┏", "┓", "┗", "┛", "━", "┃") if heavy else ("┌", "┐", "└", "┘", "─", "│")
        for xx in range(x + 1, x + w - 1):
            self.put(xx, y, hz, color)
            self.put(xx, y + h - 1, hz, color)
        for yy in range(y + 1, y + h - 1):
            self.put(x, yy, vt, color)
            self.put(x + w - 1, yy, vt, color)
        self.put(x, y, tl, color)
        self.put(x + w - 1, y, tr, color)
        self.put(x, y + h - 1, bl, color)
        self.put(x + w - 1, y + h - 1, br, color)

    def image(self, x, y, pixels):
        """Image en demi-blocs : chaque caractère affiche 2 pixels (haut et bas)"""
        for row in range(len(pixels) // 2):
            top, bottom = pixels[row * 2], pixels[row * 2 + 1]
            for col in range(len(top)):
                self.put(x + col, y + row, "▀", top[col], bottom[col], "")

    def ransom(self, x, y, text, seed=0, styles=RANSOM_STYLES):
        """Lettres découpées : chaque lettre a ses propres couleurs"""
        for i, char in enumerate(text):
            if char == " ":
                x += 2
                continue
            bg, fg = styles[(i * 7 + seed) % len(styles)]
            self.text(x, y, f" {char} ", fg, bg, "b")
            x += 3
        return x

    def moon(self, x, y, size=8):
        """Pleine lune de P3, en demi-blocs, avec un halo"""
        pixels = []
        c = (size - 1) / 2
        for py in range(size):
            row = []
            for px in range(size):
                d = ((px - c) ** 2 + (py - c) ** 2) ** 0.5 / (size / 2)
                row.append(mix((240, 252, 255), P3_CYAN, d) if d <= 0.85 else None)
            pixels.append(row)
        for row in range(size // 2):
            for col in range(size):
                top, bottom = pixels[row * 2][col], pixels[row * 2 + 1][col]
                if top or bottom:
                    under = self.cells[y + row][x + col][2] if 0 <= y + row < self.h and 0 <= x + col < self.w else BLACK
                    self.put(x + col, y + row, "▀", top or under, bottom or under, "")

    def render(self, color256, tint=None):
        out = ["\x1b[H"]
        last = None
        for y, row in enumerate(self.cells):
            out.append(f"\x1b[{y + 1};1H")
            for char, fg, bg, style in row:
                if char == "":
                    continue
                if tint:
                    fg, bg = tint(fg), tint(bg)
                state = (fg, bg, style)
                if state != last:
                    codes = ["0"]
                    if "b" in style:
                        codes.append("1")
                    if "i" in style:
                        codes.append("3")
                    if color256:
                        codes += [f"38;5;{rgb_to_256(fg)}", f"48;5;{rgb_to_256(bg)}"]
                    else:
                        codes += [f"38;2;{fg[0]};{fg[1]};{fg[2]}", f"48;2;{bg[0]};{bg[1]};{bg[2]}"]
                    out.append(f"\x1b[{';'.join(codes)}m")
                    last = state
                out.append(char)
        out.append("\x1b[0m")
        return "".join(out)


def ransom_width(text):
    return sum(2 if c == " " else 3 for c in text)


# --- TERMINAL ---
class Terminal:
    def __init__(self, animations=True):
        self.fd = sys.stdin.fileno()
        self.color256 = not truecolor()
        self.animations = animations and not os.environ.get("PERSONA_NO_ANIM")
        self.dark_hour = dark_hour()
        self.saved = None
        self.history = []

    def __enter__(self):
        self.saved = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[2J")
        sys.stdout.flush()
        return self

    def __exit__(self, *exc):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)
        sys.stdout.write("\x1b[0m\x1b[2J\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()

    def size(self):
        size = shutil.get_terminal_size((100, 30))
        return max(size.columns, 40), max(size.lines, 16)

    def tint(self, rgb):
        return dark_hour_tint(rgb) if self.dark_hour else rgb

    def draw(self, canvas):
        sys.stdout.write(canvas.render(self.color256, dark_hour_tint if self.dark_hour else None))
        sys.stdout.flush()

    def key_waiting(self, timeout=0.0):
        return bool(select.select([self.fd], [], [], timeout)[0])

    def read_key(self):
        """Lit une touche. Une séquence secrète lance son easter egg et renvoie « redraw »."""
        key = self.raw_key()
        self.history = (self.history + [key])[-12:]
        for sequence, egg in EASTER_EGGS:
            if self.history[-len(sequence):] == sequence:
                self.history = []
                egg(self)
                return "redraw"
        return key

    def raw_key(self):
        char = os.read(self.fd, 1)
        if char == b"\x1b":
            if not self.key_waiting(0.05):
                return "esc"
            seq = os.read(self.fd, 8).decode("ascii", "ignore")
            for prefix, key in (("[5~", "pageup"), ("[6~", "pagedown"), ("[A", "up"), ("[B", "down"),
                                ("[C", "right"), ("[D", "left"), ("OA", "up"), ("OB", "down"),
                                ("OC", "right"), ("OD", "left")):
                if seq.startswith(prefix):
                    return key
            return "esc"
        if char in (b"\r", b"\n"):
            return "enter"
        if char in (b"\x7f", b"\x08"):
            return "back"
        if char == b" ":
            return "space"
        key = char.decode("utf-8", "ignore").lower()
        return {"k": "up", "j": "down"}.get(key, key)

    def pause(self, seconds):
        """Attend, sauf si une touche est pressée (pour passer l'animation)"""
        if self.key_waiting(seconds):
            os.read(self.fd, 16)
            return True
        return False


# --- ANIMATIONS ---
def intro(term):
    w, h = term.size()
    title = "PERSONA"
    x0 = (w - ransom_width(title)) // 2
    y0 = max(1, h // 2 - 4)
    canvas = Canvas(w, h, BLACK)
    if term.animations:
        # Éclats rouges qui traversent l'écran
        for step in range(1, 9):
            canvas = Canvas(w, h, BLACK)
            edge = int((w + h) * step / 8)
            for y in range(h):
                end = edge - y
                canvas.fill(0, y, max(0, min(w, end)), 1, DARK_RED if y % 4 else RED)
            term.draw(canvas)
            if term.pause(0.025):
                break
        canvas = Canvas(w, h, BLACK)
        # Les lettres apparaissent une à une
        for i in range(1, len(title) + 1):
            draw_intro(canvas, w, h, x0, y0, title[:i], "")
            term.draw(canvas)
            if term.pause(0.07):
                break
        # Texte qui s'écrit
        welcome = intro_text(term)
        for i in range(0, len(welcome) + 1, 2):
            draw_intro(canvas, w, h, x0, y0, title, welcome[:i], term.dark_hour)
            term.draw(canvas)
            if term.pause(0.03):
                break
    draw_intro(canvas, w, h, x0, y0, title, intro_text(term), term.dark_hour)
    term.draw(canvas)
    if term.animations:
        term.pause(0.6)


def intro_text(term):
    # Réplique officielle d'Igor : laissée telle quelle, comme les phrases des All-Out Attacks
    return t("dark_hour") if term.dark_hour else "Welcome to the Velvet Room."


def draw_intro(canvas, w, h, x0, y0, title, welcome, dark=False):
    canvas.fill(0, 0, w, h, BLACK)
    for y in range(h):  # bande rouge en diagonale
        start = w - h // 2 - 22 + y // 2
        canvas.fill(start, y, 6, 1, DARK_RED)
    if dark:  # la pleine lune de la Dark Hour
        canvas.moon(4, 1, 14)
    canvas.ransom(x0, y0, title, seed=3)
    if len(title) == 7:
        sub = " GRUB THEMES "
        sx = (w - len(sub)) // 2
        canvas.text(sx, y0 + 3, sub, WHITE, RED, "b")
        canvas.text(sx - 1, y0 + 3, "▐", RED, BLACK)
        canvas.text(sx + len(sub), y0 + 3, "▌", RED, BLACK)
    canvas.center(y0 + 6, welcome, (200, 200, 220), BLACK, "i")


def wipe(term, color):
    """Transition façon P5 : une bande colorée balaie l'écran en diagonale"""
    if not term.animations:
        return
    color = term.tint(color)
    w, h = term.size()
    steps = 8
    for step in range(1, steps + 1):
        out = []
        edge = int((w + h + 8) * step / steps)
        for y in range(h):
            end = max(0, min(w, edge - y))
            out.append(f"\x1b[{y + 1};1H")
            if term.color256:
                out.append(f"\x1b[48;5;{rgb_to_256(color)}m")
            else:
                out.append(f"\x1b[48;2;{color[0]};{color[1]};{color[2]}m")
            out.append(" " * end)
            if end < w:  # bord noir de la bande, comme dans les menus de P5
                out.append(("\x1b[48;5;16m" if term.color256 else "\x1b[48;2;0;0;0m") + " " * min(2, w - end))
        out.append("\x1b[0m")
        sys.stdout.write("".join(out))
        sys.stdout.flush()
        if term.pause(0.018):
            break


# --- ÉCRANS ---
def footer(canvas, hints, accent):
    y = canvas.h - 1
    canvas.fill(0, y, canvas.w, 1, (20, 20, 20))
    x = 2
    for key, label in hints:
        x = canvas.text(x, y, f" {key} ", WHITE, accent, "b")
        x = canvas.text(x, y, f" {label}   ", (190, 190, 190), (20, 20, 20))


def header(canvas, game, subtitle):
    style = GAME_STYLES[game]
    w = canvas.w
    if game == "persona3_reload":
        for x in range(w):  # dégradé bleu nuit -> bleu
            canvas.fill(x, 0, 1, 3, mix(P3_NAVY, P3_BLUE, x / max(1, w - 1)))
        canvas.text(2, 1, " ".join(style["title"]), WHITE, None, "b")
        canvas.text(2 + len(" ".join(style["title"])) + 3, 1, style["tagline"], P3_CYAN, None, "")
        canvas.moon(w - 10, 0, 6)
    else:
        canvas.fill(0, 0, w, 3, BLACK)
        for y in range(3):  # bande rouge inclinée
            canvas.fill(0, y, min(w, ransom_width(style["title"]) + 8 - y * 2), 1, style["accent"])
        canvas.ransom(2, 1, style["title"], seed=len(style["title"]), styles=RANSOM_ON_RED)
        canvas.text(w - len(style["tagline"]) - 3, 1, style["tagline"], RED, None, "bi")
    canvas.text(2, 3, subtitle, (170, 170, 170), None, "i")


def game_screen(term, games, counts, previews, selected):
    w, h = term.size()
    canvas = Canvas(w, h, BLACK)
    canvas.ransom(2, 1, "PERSONA", seed=3)
    canvas.text(25, 1, " GRUB THEMES ", WHITE, RED, "b")
    canvas.text(2, 3, t("choose_game"), (170, 170, 170), None, "i")
    lang = f" {install_i18n.language_name(install_i18n.current)} · {install_i18n.current.upper()} "
    canvas.text(w - len(lang) - 2, 1, lang, WHITE, (40, 40, 40), "b")

    horizontal = w >= 3 * 30 + 6
    card_w = (w - 4 - 2 * 2) // 3 if horizontal else w - 4
    space = h - 7 if horizontal else (h - 7) // 3
    # Hauteur ajustée au contenu : image 16:9 sur toute la largeur + 4 lignes de texte + bordures
    image_rows = min((card_w - 4) * 9 // 16 // 2, space - 7)
    card_h = max(7, min(space, image_rows + 7))
    top = 5 + max(0, (space - card_h) // 2) if horizontal else 5
    for i, game in enumerate(games):
        style = GAME_STYLES[game]
        cx = 2 + i * (card_w + 2) if horizontal else 2
        cy = top if horizontal else 5 + i * space
        active = i == selected
        draw_card(canvas, cx, cy, card_w, card_h - (0 if horizontal else 1), game, style, counts[game], previews, active)
    footer(canvas, [("←→", t("key_move")), ("Enter", t("key_choose")), ("S", t("key_shuffle")),
                    ("L", t("key_language")), ("q", t("key_quit"))], RED)
    term.draw(canvas)


def draw_card(canvas, x, y, w, h, game, style, count, previews, active):
    accent = style["accent"]
    canvas.fill(x, y, w, h, style["bg"] if active else (18, 18, 18))
    canvas.box(x, y, w, h, accent if active else DIM, heavy=active)
    inner_w = w - 4
    text_rows = 4
    img_rows = h - 3 - text_rows
    if img_rows >= 3:
        pw = min(inner_w, int(img_rows * 2 * 16 / 9))
        ph = (pw * 9 // 16) // 2 * 2
        pixels = previews.scaled(f"{game}/{style['hero']}", pw, max(2, ph))
        if pixels:
            if not active:  # cartes non choisies plus sombres
                pixels = [[mix(p, BLACK, 0.55) for p in row] for row in pixels]
            canvas.image(x + 2 + (inner_w - pw) // 2, y + 1, pixels)
    ty = y + h - 1 - text_rows
    title = style["title"]
    canvas.fill(x + 1, ty, w - 2, 1, accent if active else (35, 35, 35))
    canvas.center(ty, title if len(title) <= inner_w else title.replace("PERSONA ", "P"), WHITE, None, "b", x, w)
    canvas.center(ty + 1, t("themes_count", n=count), WHITE if active else GREY, None, "b", x, w)
    canvas.center(ty + 2, style["tagline"], P3_CYAN if game == "persona3_reload" else RED, None, "i", x, w)


def list_screen(term, game, subtitle, items, selected, previews, offset):
    """items : liste de dict (label, extra, key, color, quote, hd). Retourne le décalage de défilement."""
    w, h = term.size()
    style = GAME_STYLES[game]
    canvas = Canvas(w, h, style["bg"])
    header(canvas, game, subtitle)

    list_w = min(34, max(22, w // 3))
    top, rows = 5, h - 7
    if selected < offset:
        offset = selected
    if selected >= offset + rows:
        offset = selected - rows + 1
    for i, item in enumerate(items[offset:offset + rows]):
        index = offset + i
        y = top + i
        color = item["color"]
        if index == selected:
            canvas.fill(1, y, list_w, 1, color)
            canvas.text(2, y, "▶ " + item["label"], text_on(color), None, "b")
            if item["extra"]:
                canvas.text(1 + list_w - len(item["extra"]) - 1, y, item["extra"], text_on(color), None, "")
        else:
            canvas.text(2, y, "● ", color)
            canvas.text(4, y, item["label"], (215, 215, 215))
            if item["extra"]:
                canvas.text(1 + list_w - len(item["extra"]) - 1, y, item["extra"], GREY)
    if offset > 0:
        canvas.text(list_w - 2, top - 1, "▲", GREY)
    if offset + rows < len(items):
        canvas.text(list_w - 2, top + rows, "▼", GREY)

    # Aperçu du thème survolé
    item = items[selected]
    px = list_w + 4
    avail_w, avail_h = w - px - 3, h - top - 6
    pw = min(avail_w, int(avail_h * 2 * 16 / 9), previews.width or 80)
    ph = (pw * 9 // 16) // 2 * 2
    pixels = previews.scaled(item["key"], pw, ph) if pw >= 8 and ph >= 4 else None
    if pixels:
        canvas.box(px - 1, top - 1, pw + 2, ph // 2 + 2, item["color"], heavy=True)
        canvas.image(px, top, pixels)
        qy = top + ph // 2 + 2
    else:
        qy = top
    if item.get("quote"):
        quote = f"“{item['quote']}”"
        canvas.text(px, qy, quote[:max(0, w - px - 2)], WHITE, None, "bi")
        canvas.text(px, qy + 1, f"— {item['name']}", item["color"] if luminance(item["color"]) > 0.25 else GREY, None, "")
    info = "✔ " + t("hd") if item.get("hd") else "○ " + t("hd_soon")
    x = canvas.text(px, qy + 2, info, (120, 200, 120) if item.get("hd") else GREY)
    if item.get("arcana"):
        canvas.text(x + 3, qy + 2, f"✦ {t('arcana')} : {install_i18n.arcana(item['arcana'])}", (230, 200, 120))

    footer(canvas, [("↑↓", t("key_move")), ("Enter", t("key_choose")), ("Esc", t("key_back")),
                    ("q", t("key_quit"))], style["accent"])
    term.draw(canvas)
    return offset


def confirm_screen(term, game, item, previews, velvet_available, velvet, shuffled=False):
    w, h = term.size()
    style = GAME_STYLES[game]
    canvas = Canvas(w, h, style["bg"])
    header(canvas, game, t("ready"))
    pw = min(w - 6, int((h - 13) * 2 * 16 / 9), previews.width or 80)
    ph = (pw * 9 // 16) // 2 * 2
    y = 5
    pixels = previews.scaled(item["key"], pw, ph) if pw >= 8 and ph >= 4 else None
    if pixels:
        x = (w - pw) // 2
        canvas.box(x - 1, y - 1, pw + 2, ph // 2 + 2, item["color"], heavy=True)
        canvas.image(x, y, pixels)
        y += ph // 2 + 2
    name = item["name"].upper()
    if ransom_width(name) <= w - 4 and name.isascii():
        canvas.ransom((w - ransom_width(name)) // 2, y, name, seed=len(name))
        y += 3
    else:
        canvas.center(y, name, WHITE, None, "b")
        y += 2
    if item.get("arcana"):
        canvas.center(y, f"✦ {t('arcana')} : {install_i18n.arcana(item['arcana'])} ✦", (230, 200, 120))
        y += 2
    if velvet_available:
        mark = "■" if velvet else " "
        canvas.center(y, f"[{mark}] {t('velvet_option')}", (200, 200, 230))
    hints = [("Enter", t("key_install")), ("Esc", t("key_back")), ("q", t("key_quit"))]
    if velvet_available:
        hints.insert(1, ("Space", "Velvet Room"))
    if shuffled:
        hints.insert(1, ("S", t("key_reshuffle")))
    footer(canvas, hints, style["accent"])
    term.draw(canvas)


# --- PARCOURS ---
def png_size(path):
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        return struct.unpack(">II", head[16:24])
    except (OSError, struct.error):
        return 0, 0


def theme_color(path):
    """Couleur du personnage : celle de la barre de progression du thème"""
    try:
        with open(os.path.join(path, "theme.txt")) as f:
            for line in f:
                if line.strip().startswith("fg_color"):
                    value = line.split("=", 1)[1].strip().strip('"').lstrip("#")
                    if len(value) == 3:
                        value = "".join(c * 2 for c in value)
                    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except (OSError, ValueError):
        pass
    return RED


def theme_item(path, name, label, extra, quotes, arcana=None):
    game = os.path.basename(os.path.dirname(path))
    folder = os.path.basename(path)
    w, h = png_size(os.path.join(path, "background.png"))
    return {
        "label": label, "extra": extra, "name": name, "path": path,
        "key": f"{game}/{folder}", "color": theme_color(path), "quote": quotes.get(folder),
        "arcana": (arcana or {}).get(folder),
        "hd": w >= 1920 and h >= 1080 and abs(w / h - 16 / 9) < 0.02,
    }


def run(data, quotes, velvet_available, arcana=None, shuffle=False):
    """Parcours complet. Retourne (chemin, nom, variante, velvet_room) ou None si l'utilisateur quitte."""
    previews = Previews()
    games = [g for g in GAME_STYLES if g in data]
    counts = {g: sum(len(v) for v in data[g].values()) for g in games}
    try:
        with Terminal() as term:
            return menus(term, data, games, counts, previews, quotes, velvet_available, arcana or {}, shuffle)
    except KeyboardInterrupt:  # Ctrl+C : on quitte proprement, le terminal est déjà restauré
        return None


def next_language():
    codes = install_i18n.available()
    install_i18n.set_language(codes[(codes.index(install_i18n.current) + 1) % len(codes)])


def menus(term, data, games, counts, previews, quotes, velvet_available, arcana, shuffle):
    """Écrans jeu -> personnage -> tenue -> confirmation, ou Shuffle Time -> confirmation"""
    intro(term)
    wipe(term, RED)
    game_index = 0
    pending_shuffle = shuffle
    while True:
        if pending_shuffle:
            pending_shuffle = False
            result = shuffle_time(term, data, previews, quotes, arcana)
            if result == "quit":
                return None
            if result is None:
                wipe(term, RED)
                continue
            game, char, variant, chosen = result
            shuffled = True
        else:
            # 1. Jeu
            while True:
                game_screen(term, games, counts, previews, game_index)
                key = term.read_key()
                if key in ("left", "up"):
                    game_index = (game_index - 1) % len(games)
                elif key in ("right", "down"):
                    game_index = (game_index + 1) % len(games)
                elif key.isdigit() and 1 <= int(key) <= len(games):
                    game_index = int(key) - 1
                    break
                elif key == "enter":
                    break
                elif key == "l":
                    next_language()
                elif key == "s":
                    pending_shuffle = True
                    break
                elif key in ("q", "esc"):
                    return None
            if pending_shuffle:
                continue
            game = games[game_index]
            wipe(term, GAME_STYLES[game]["accent"])

            # 2. Personnage
            hero = GAME_STYLES[game]["hero"].capitalize()
            characters = sorted(data[game], key=lambda name: (name != hero, name))  # le héros en premier
            items = []
            for name in characters:
                variants = data[game][name]
                default = variants.get("Default") or list(variants.values())[0]
                extra = f"+{len(variants) - 1}" if len(variants) > 1 else ""
                label = install_i18n.character(name)
                items.append(theme_item(default, label, label, extra, quotes, arcana))
            char_index, offset = 0, 0
            while True:
                offset = list_screen(term, game, t("choose_character", n=len(items)),
                                     items, char_index, previews, offset)
                key = term.read_key()
                if key == "up":
                    char_index = (char_index - 1) % len(items)
                elif key == "down":
                    char_index = (char_index + 1) % len(items)
                elif key == "pageup":
                    char_index = max(0, char_index - 10)
                elif key == "pagedown":
                    char_index = min(len(items) - 1, char_index + 10)
                elif key in ("esc", "back", "left"):
                    char_index = None
                    break
                elif key == "q":
                    return None
                elif key in ("enter", "right"):
                    break
            if char_index is None:
                wipe(term, RED)
                continue
            char = characters[char_index]
            variants = data[game][char]

            # 3. Tenue
            variant_names = list(variants)
            if len(variant_names) > 1:
                label = install_i18n.character(char)
                variant_items = [theme_item(variants[v], f"{label} ({v})" if v != "Default" else label, v, "",
                                            quotes, arcana) for v in variant_names]
                variant_index, voffset = 0, 0
                while True:
                    voffset = list_screen(term, game, t("choose_outfit", name=label), variant_items,
                                          variant_index, previews, voffset)
                    key = term.read_key()
                    if key == "up":
                        variant_index = (variant_index - 1) % len(variant_items)
                    elif key == "down":
                        variant_index = (variant_index + 1) % len(variant_items)
                    elif key in ("esc", "back", "left"):
                        variant_index = None
                        break
                    elif key == "q":
                        return None
                    elif key in ("enter", "right"):
                        break
                if variant_index is None:
                    continue
                variant = variant_names[variant_index]
                chosen = variant_items[variant_index]
            else:
                variant = None
                chosen = items[char_index]
            shuffled = False

        # 4. Confirmation
        velvet = False
        while True:
            confirm_screen(term, game, chosen, previews, velvet_available, velvet, shuffled)
            key = term.read_key()
            if key == "space" and velvet_available:
                velvet = not velvet
            elif key == "enter":
                wipe(term, GAME_STYLES[game]["accent"])
                return chosen["path"], char, variant, velvet
            elif key == "s" and shuffled:
                pending_shuffle = True
                break
            elif key in ("esc", "back", "left"):
                break
            elif key == "q":
                return None


# --- SHUFFLE TIME ---
SHUFFLE_BG = (8, 10, 30)
CARD_BACK = (16, 28, 92)
GOLD = (230, 200, 120)


def draw_card_back(canvas, x, y, w, h, width=None, highlight=False):
    """Dos de carte de tarot : losanges bleus, étoile au centre"""
    width = w if width is None else width
    if width <= 0:
        return
    x += (w - width) // 2
    canvas.fill(x, y, width, h, CARD_BACK)
    if width >= 3:
        for yy in range(1, h - 1):
            for xx in range(1, width - 1):
                if (xx + yy) % 2 == 0:
                    canvas.put(x + xx, y + yy, "◆" if (xx + yy) % 4 == 0 else "◇", (60, 90, 190), CARD_BACK)
        canvas.box(x, y, width, h, GOLD if highlight else P3_BLUE, heavy=highlight)
        if width >= 5:
            canvas.text(x + width // 2, y + h // 2, "✦", GOLD if highlight else P3_CYAN, CARD_BACK, "b")


def draw_card_face(canvas, x, y, w, h, item, previews, width=None):
    """Face de la carte : Arcane, aperçu du thème, nom du personnage"""
    width = w if width is None else width
    if width <= 0:
        return
    x += (w - width) // 2
    paper = (244, 238, 224)
    canvas.fill(x, y, width, h, paper)
    canvas.box(x, y, width, h, item["color"], heavy=True)
    if width < 6:
        return
    top = install_i18n.arcana(item["arcana"]).upper() if item.get("arcana") else "✦"
    canvas.center(y + 1, top[:width - 2], (120, 90, 30), None, "b", x, width)
    pw = width - 2
    ph = min((pw * 9 // 16) // 2 * 2, (h - 5) * 2)
    pixels = previews.scaled(item["key"], pw, ph) if ph >= 4 else None
    if pixels:
        canvas.image(x + 1, y + 2, pixels)
    name = item["name"]
    canvas.center(y + h - 2, name[:width - 2], BLACK, None, "b", x, width)


def shuffle_screen(canvas, subtitle):
    w = canvas.w
    for x in range(w):  # bandeau bleu façon P3
        canvas.fill(x, 0, 1, 3, mix(P3_NAVY, P3_BLUE, x / max(1, w - 1)))
    canvas.center(1, "S H U F F L E   T I M E", GOLD, None, "b")
    canvas.center(4, subtitle, (190, 200, 230), None, "i")


def shuffle_time(term, data, previews, quotes, arcana):
    """Cartes de tarot battues, une se retourne : un thème au hasard.
    Retourne (jeu, perso, tenue, élément), None (retour) ou « quit »."""
    while True:
        pool = [(game, char, variant, path)
                for game in GAME_STYLES if game in data
                for char, variants in data[game].items()
                for variant, path in variants.items()]
        game, char, variant, path = random.choice(pool)
        label = install_i18n.character(char)
        name = label if variant in (None, "Default") else f"{label} ({variant})"
        item = theme_item(path, name, name, "", quotes, arcana)

        w, h = term.size()
        n = 5 if w >= 5 * 16 + 8 else 3
        cw = max(8, min(18, (w - 4) // n - 2))
        ch = max(7, min(13, h - 9))
        gap = 2
        x0 = (w - (n * cw + (n - 1) * gap)) // 2
        y0 = 6
        home = [x0 + i * (cw + gap) for i in range(n)]
        center = (w - cw) // 2
        pick = random.randrange(n)

        def frame(xs, ys, subtitle, highlight=None, face_width=None, back_width=None):
            canvas = Canvas(w, h, SHUFFLE_BG)
            shuffle_screen(canvas, subtitle)
            for i in range(n):
                if i == pick and face_width is not None:
                    draw_card_face(canvas, xs[i], ys[i], cw, ch, item, previews, face_width)
                else:
                    draw_card_back(canvas, xs[i], ys[i], cw, ch,
                                   back_width if i == pick and back_width is not None else None, i == highlight)
            return canvas

        skipped = not term.animations
        ys = [h] * n
        # 1. Distribution : les cartes arrivent une à une
        for i in range(n):
            for step in range(1, 5):
                if skipped:
                    break
                ys[i] = int(h + (y0 - h) * step / 4)
                term.draw(frame(home, ys, t("shuffle_pick")))
                skipped = term.pause(0.02)
        ys = [y0] * n
        # 2. On bat les cartes : elles se resserrent au centre puis se rouvrent
        for _ in range(2):
            for step in list(range(1, 7)) + list(range(5, -1, -1)):
                if skipped:
                    break
                xs = [int(x + (center - x) * step / 6) for x in home]
                jiggle = [y0 + (1 if (i + step) % 2 else 0) for i in range(n)]
                term.draw(frame(xs, jiggle, t("shuffle_pick")))
                skipped = term.pause(0.03)
        # 3. La roulette : la sélection ralentit et s'arrête sur une carte
        total = 2 * n + pick
        for step in range(total + 1):
            if skipped:
                break
            term.draw(frame(home, ys, t("shuffle_pick"), highlight=step % n))
            skipped = term.pause(0.04 + 0.16 * step / total)
        # 4. La carte se soulève et se retourne
        lifted = [y0 - 1 if i == pick else y0 for i in range(n)]
        if not skipped:
            for width in list(range(cw, 0, -3)):
                term.draw(frame(home, lifted, t("shuffle_pick"), highlight=pick, back_width=width))
                if term.pause(0.03):
                    break
            for width in list(range(1, cw, 3)):
                term.draw(frame(home, lifted, t("shuffle_result"), face_width=width))
                if term.pause(0.03):
                    break

        # 5. Résultat
        while True:
            canvas = frame(home, lifted, f"{t('shuffle_result')} : {name}", face_width=cw)
            if item.get("quote"):
                canvas.center(y0 + ch + 1, f"“{item['quote']}”"[:w - 4], WHITE, None, "bi")
            footer(canvas, [("Enter", t("key_choose")), ("S", t("key_reshuffle")), ("Esc", t("key_back")),
                            ("q", t("key_quit"))], P3_BLUE)
            term.draw(canvas)
            key = term.read_key()
            if key == "enter":
                return game, char, None if variant == "Default" else variant, item
            if key == "s":
                break
            if key in ("esc", "back"):
                return None
            if key == "q":
                return "quit"


# --- EASTER EGGS ---
def egg_all_out_attack(term):
    """Code Konami : ALL-OUT ATTACK!"""
    w, h = term.size()
    text = "ALL-OUT ATTACK!"
    frames = 16
    for f in range(frames):
        canvas = Canvas(w, h, RED)
        for y in range(h):  # bandes noires qui défilent en diagonale
            for x in range(w):
                if ((x + y * 2 + f * 4) // 5) % 3 == 0:
                    canvas.put(x, y, " ", None, BLACK, "")
        shown = text[:min(len(text), f + 1)]
        canvas.ransom((w - ransom_width(text)) // 2, h // 2 - 1, shown, seed=11, styles=RANSOM_ON_RED)
        term.draw(canvas)
        if term.pause(0.05):
            break
    canvas = Canvas(w, h, WHITE)
    for y in range(h):  # éclaboussure
        canvas.fill(max(0, w // 2 - 2 * h + y * 3), y, 9, 1, RED)
    finale = "THE SHOW'S OVER"
    canvas.ransom((w - ransom_width(finale)) // 2, h // 2 - 1, finale, seed=5,
                  styles=[(BLACK, WHITE), (RED, WHITE), (BLACK, RED)])
    term.draw(canvas)
    term.pause(1.6)


BUTTERFLY = [
    ["(\\ /)", " )●( ", "(/ \\)"],
    [" \\ / ", "  ●  ", " / \\ "],
]


def egg_velvet_room(term):
    """« igor » : un papillon bleu traverse la Velvet Room"""
    w, h = term.size()
    velvet = (10, 16, 70)
    line = "Welcome to the Velvet Room."
    steps = 40
    for step in range(steps + 1):
        canvas = Canvas(w, h, velvet)
        for x in range(0, w, 6):  # rideaux
            canvas.fill(x, 0, 1, h, (16, 26, 100))
        bx = int(2 + (w - 8) * step / steps)
        by = int(h // 2 - 4 + 3 * math.sin(step / 3))
        for row, part in enumerate(BUTTERFLY[step % 2]):
            canvas.text(bx, by + row, part, P3_CYAN, None, "b")
        typed = line[:int(len(line) * step / steps)]
        canvas.center(h - 4, typed, (220, 225, 255), None, "i")
        term.draw(canvas)
        if term.pause(0.06):
            break
    term.pause(1.2)


MORGANA = [
    r"    /\       /\    ",
    r"   /  \_____/  \   ",
    r"  |   (O) (O)   |  ",
    r"  |      ^      |  ",
    r"   \   \___/   /   ",
    r"    '-._____.-'    ",
    r"     [=======]     ",
]


def egg_morgana(term):
    """« mona » : Morgana a quelque chose à dire"""
    w, h = term.size()
    line = "Looking cool, Joker!"
    x0, y0 = max(2, w // 2 - 24), max(2, h // 2 - 4)
    for i in range(len(line) + 1):
        canvas = Canvas(w, h, BLACK)
        for row, part in enumerate(MORGANA):
            color = (255, 210, 60) if row == len(MORGANA) - 1 else WHITE
            canvas.text(x0, y0 + row, part, color, None, "b")
        bx, by = x0 + 22, y0
        canvas.fill(bx, by, len(line) + 4, 3, WHITE)
        canvas.text(bx - 1, by + 2, "◀", WHITE)
        canvas.text(bx + 2, by + 1, line[:i], BLACK, None, "bi")
        term.draw(canvas)
        if term.pause(0.05):
            break
    term.pause(1.4)


EASTER_EGGS = [
    (["up", "up", "down", "down", "left", "right", "left", "right", "b", "a"], egg_all_out_attack),
    (list("igor"), egg_velvet_room),
    (list("mona"), egg_morgana),
]


def outro(quote, name, game):
    """Message final, dans le terminal normal"""
    accent = GAME_STYLES.get(game, {}).get("accent", RED)
    color256 = not truecolor()

    def bg(rgb):
        return f"\x1b[48;5;{rgb_to_256(rgb)}m" if color256 else f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m"

    def fg(rgb):
        return f"\x1b[38;5;{rgb_to_256(rgb)}m" if color256 else f"\x1b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"

    width = min(shutil.get_terminal_size((80, 24)).columns, 90)
    slash = "".join(f"{bg(accent if i % 6 < 4 else BLACK)} " for i in range(width - 4))
    print(f"\n  {slash}\x1b[0m")
    if quote:
        print(f"\n  {fg(WHITE)}\x1b[1;3m“{quote}”\x1b[0m {fg(accent)}— {name}\x1b[0m")
    print(f"\n  {slash}\x1b[0m")
