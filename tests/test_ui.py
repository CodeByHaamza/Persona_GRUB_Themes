"""Interface terminal : rendu, aperçus, Dark Hour, et un vrai lancement dans un pseudo-terminal"""
import os
import pty
import select
import sys
import time
import unittest

from helpers import ROOT, install_i18n

import install_ui  # noqa: E402


class CanvasTest(unittest.TestCase):
    def test_render_truecolor_and_256(self):
        canvas = install_ui.Canvas(10, 2)
        canvas.text(0, 0, "Joker", install_ui.WHITE, install_ui.RED, "b")
        self.assertIn("38;2;255;255;255", canvas.render(False))
        self.assertIn("48;5;", canvas.render(True))
        self.assertIn("Joker", canvas.render(False))

    def test_wide_characters_take_two_columns(self):
        canvas = install_ui.Canvas(10, 1)
        end = canvas.text(0, 0, "恭喜")
        self.assertEqual(end, 4)

    def test_dark_hour_tint_is_green(self):
        r, g, b = install_ui.dark_hour_tint((200, 200, 200))
        self.assertGreater(g, r)
        self.assertGreater(g, b)


class PreviewsTest(unittest.TestCase):
    def test_scaled_preview(self):
        previews = install_ui.Previews()
        pixels = previews.scaled("persona5_royal/joker", 32, 18)
        self.assertEqual(len(pixels), 18)
        self.assertEqual(len(pixels[0]), 32)


class LanguageTest(unittest.TestCase):
    def tearDown(self):
        install_i18n.set_language("en")

    def test_switch_language(self):
        install_i18n.set_language("fr")
        self.assertEqual(install_i18n.t("choose_game"), "Choisis ton jeu")
        self.assertEqual(install_i18n.arcana("Fool"), "Fou")
        self.assertTrue(install_i18n.is_yes("oui"))
        install_i18n.set_language("xx")  # langue inconnue : anglais
        self.assertEqual(install_i18n.current, "en")


@unittest.skipUnless(hasattr(os, "fork"), "needs a POSIX terminal")
class RealTerminalTest(unittest.TestCase):
    """Lance l'installeur dans un pseudo-terminal, ouvre un jeu, puis quitte"""

    def run_keys(self, keys, env=None):
        script = (
            "import sys, tempfile, os; sys.path.insert(0, %r); import install as I; "
            "d = tempfile.mkdtemp(); open(d + '/grub', 'w').write('GRUB_TIMEOUT=5\\n'); "
            "I.GRUB_CONFIG_FILE = d + '/grub'; I.check_root = lambda: None; "
            "I.detect_grub = lambda: (d, ['true']); I.main()"
        ) % ROOT
        pid, fd = pty.fork()
        if pid == 0:
            os.environ.update({"TERM": "xterm-256color", "COLORTERM": "truecolor", "PERSONA_NO_ANIM": "1",
                               "LANG": "en_US.UTF-8", **(env or {})})
            os.execvp(sys.executable, [sys.executable, "-c", script, "--dry-run"])
        output = b""

        def pump(seconds):
            nonlocal output
            end = time.time() + seconds
            while time.time() < end:
                if select.select([fd], [], [], 0.05)[0]:
                    try:
                        output += os.read(fd, 65536)
                    except OSError:
                        return

        pump(2.0)
        for key in keys:
            os.write(fd, key)
            pump(0.6)
        pump(1.5)
        _, status = os.waitpid(pid, 0)
        return os.WEXITSTATUS(status), output.decode("utf-8", "ignore")

    def test_open_a_game_and_quit(self):
        code, output = self.run_keys([b"\r", b"q"])
        self.assertEqual(code, 0)
        self.assertIn("Take your time.", output)
        self.assertIn("THE SHOW", output)  # phrase de Joker dans la liste des persos

    def test_dark_hour_and_language(self):
        code, output = self.run_keys([b"l", b"q"], {"PERSONA_DARK_HOUR": "1"})
        self.assertEqual(code, 0)
        self.assertIn("Choisis ton jeu", output)


if __name__ == "__main__":
    unittest.main()
