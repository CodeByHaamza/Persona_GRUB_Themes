"""Contenu du repo : thèmes complets, previews, langues, personadle"""
import json
import os
import re
import unittest

from helpers import ROOT, install, install_i18n

THEMES_DIR = os.path.join(ROOT, "themes")
REQUIRED_FILES = ["theme.txt", "background.png", "select_c.png", "boot_menu_c.png"]


def all_themes():
    for game in sorted(os.listdir(THEMES_DIR)):
        game_dir = os.path.join(THEMES_DIR, game)
        if game.startswith("_") or not os.path.isdir(game_dir):
            continue
        for theme in sorted(os.listdir(game_dir)):
            if os.path.isdir(os.path.join(game_dir, theme)):
                yield game, theme


class ThemeFilesTest(unittest.TestCase):
    def test_every_theme_is_complete(self):
        for game, theme in all_themes():
            path = os.path.join(THEMES_DIR, game, theme)
            with self.subTest(theme=f"{game}/{theme}"):
                for name in REQUIRED_FILES:
                    self.assertTrue(os.path.isfile(os.path.join(path, name)), name)
                self.assertTrue(os.path.isdir(os.path.join(path, "icons")))

    def test_files_referenced_by_theme_txt_exist(self):
        for game, theme in all_themes():
            path = os.path.join(THEMES_DIR, game, theme)
            with open(os.path.join(path, "theme.txt")) as f:
                text = f.read()
            with self.subTest(theme=f"{game}/{theme}"):
                for name in re.findall(r'desktop-image:\s*"([^"]+)"', text):
                    self.assertTrue(os.path.isfile(os.path.join(path, name)), name)
                for pattern in re.findall(r'pixmap_style\s*=\s*"([^"]+)"', text):
                    self.assertTrue(os.path.isfile(os.path.join(path, pattern.replace("*", "c"))), pattern)

    def test_every_theme_has_a_preview(self):
        for game, theme in all_themes():
            with self.subTest(theme=f"{game}/{theme}"):
                self.assertTrue(os.path.isfile(os.path.join(ROOT, "previews", game, theme + ".png")))

    def test_folder_names_are_unique(self):
        names = [theme for _, theme in all_themes()]
        self.assertEqual(len(names), len(set(names)))

    def test_terminal_previews_cover_every_theme(self):
        with open(os.path.join(THEMES_DIR, "_shared", "terminal_previews.json")) as f:
            previews = json.load(f)["themes"]
        for game, theme in all_themes():
            self.assertIn(f"{game}/{theme}", previews)


class LanguageTest(unittest.TestCase):
    def test_all_languages_have_the_same_keys(self):
        files = {code: install_i18n._load(code) for code in install_i18n.available()}
        self.assertEqual(set(files), {"en", "fr", "de", "es", "it", "pt"})
        for code, strings in files.items():
            with self.subTest(language=code):
                self.assertEqual(set(strings), set(files["en"]))
                self.assertEqual(set(strings["arcana_names"]), set(files["en"]["arcana_names"]))

    def test_every_arcana_is_translated(self):
        english = install_i18n._load("en")["arcana_names"]
        for arcana in set(install.THEME_ARCANA.values()):
            self.assertIn(arcana, english)

    def test_placeholders_match(self):
        english = install_i18n._load("en")
        for code in install_i18n.available():
            strings = install_i18n._load(code)
            for key, value in english.items():
                if isinstance(value, str):
                    with self.subTest(language=code, key=key):
                        self.assertEqual(re.findall(r"{\w+}", strings[key]), re.findall(r"{\w+}", value))


class PersonadleSyncTest(unittest.TestCase):
    def test_parses_the_character_list(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import personadle_sync
        sample = '''export const aoaCharacters = [
  { nom: "Joker ( Ren Amamiya )", gif: "Joker", opus: ["P5"] },
  { nom: "Makoto Yuki", gif: "Yuki", opus: ["P3"] },
  { nom: "Anri ( Aran Hirano )", gif: "Anri", opus: ["P5X"] },
];'''
        characters = personadle_sync.parse(sample)
        self.assertEqual([c["folder"] for c in characters], ["joker", "makoto", "anri"])
        self.assertEqual(characters[2]["game"], "persona5_phantom_x")
        missing = [c["folder"] for c in characters if c["folder"] not in personadle_sync.existing_themes()]
        self.assertEqual(missing, ["anri"])


if __name__ == "__main__":
    unittest.main()
