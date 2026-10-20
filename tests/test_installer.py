"""Installeur : installation, sauvegardes, restauration, désinstallation, anciens noms"""
import glob
import os
import unittest

from helpers import FakeSystemTest, install


class InstallTest(FakeSystemTest):
    GRUB_CONFIG = (
        'GRUB_DEFAULT=0\n'
        'GRUB_TIMEOUT=5\n'
        'GRUB_TERMINAL=console\n'
        'GRUB_TERMINAL_OUTPUT="console"\n'
        '#GRUB_GFXMODE=640x480'  # pas de retour à la ligne final, exprès
    )

    def test_install_sets_theme_terminal_and_resolution(self):
        self.add_screen("connected", "2560x1440\n1920x1080\n")
        self.run_installer("--theme", "persona5_royal/joker", "-y")
        config = self.config()
        self.assertIn(f'GRUB_THEME="{self.grub_dir}/themes/joker/theme.txt"', config)
        self.assertIn("#GRUB_TERMINAL=console", config)
        self.assertIn('#GRUB_TERMINAL_OUTPUT="console"', config)
        self.assertIn('GRUB_GFXMODE="2560x1440,auto"', config)
        self.assertTrue(self.installed("joker"))
        self.assertEqual(self.calls[-1], ["fake-mkconfig"])

    def test_original_config_is_kept_once(self):
        self.run_installer("--theme", "joker", "-y")
        self.run_installer("--theme", "makoto", "-y")
        with open(install.GRUB_CONFIG_ORIGINAL) as f:
            self.assertEqual(f.read(), self.GRUB_CONFIG)
        config = self.config()
        self.assertEqual(config.count("GRUB_THEME="), 1)
        self.assertIn("themes/makoto/theme.txt", config)
        self.assertTrue(glob.glob(self.cfg + ".bak.*"))

    def test_restore(self):
        self.run_installer("--theme", "joker", "-y")
        self.run_installer("--restore")
        self.assertEqual(self.config(), self.GRUB_CONFIG)

    def test_uninstall(self):
        self.run_installer("--theme", "joker", "-y")
        self.run_installer("--uninstall")
        self.assertNotIn("\nGRUB_THEME=", "\n" + self.config())
        self.assertFalse(self.installed("joker"))

    def test_dry_run_changes_nothing(self):
        self.run_installer("--theme", "wonder", "-y", "--dry-run")
        self.assertEqual(self.config(), self.GRUB_CONFIG)
        self.assertFalse(self.installed("wonder"))
        self.assertEqual(self.calls, [])

    def test_unknown_theme(self):
        with self.assertRaises(SystemExit) as error:
            self.run_installer("--theme", "nobody", "-y")
        self.assertEqual(error.exception.code, 1)


class UserSettingsTest(FakeSystemTest):
    GRUB_CONFIG = 'GRUB_GFXMODE=1366x768\nGRUB_TERMINAL_OUTPUT="gfxterm"\n'

    def test_user_settings_are_kept(self):
        self.add_screen("connected", "2560x1440\n")
        self.run_installer("--theme", "skull", "-y")
        config = self.config()
        self.assertIn("GRUB_GFXMODE=1366x768\n", config)
        self.assertEqual(config.count("GRUB_GFXMODE"), 1)
        self.assertIn('GRUB_TERMINAL_OUTPUT="gfxterm"', config)


class RenamedThemesTest(FakeSystemTest):
    def test_old_names_still_work(self):
        data = install.scan_themes()
        self.assertTrue(install.find_theme(data, "wonder_beach")[0].endswith("persona5_phantom_x/wonder_summer"))
        self.assertTrue(install.find_theme(data, "persona5_phantom_x/bui_stellar")[0].endswith("/bui_cosmic"))
        for old, new in install.RENAMED_THEMES.items():
            self.assertEqual(len(install.find_theme(data, old)), 1, old)

    def test_uninstall_removes_old_names(self):
        os.makedirs(os.path.join(self.grub_dir, "themes", "wonder_beach"))
        self.run_installer("--theme", "wonder_beach", "-y")
        self.assertTrue(self.installed("wonder_summer"))
        self.run_installer("--uninstall")
        self.assertFalse(os.path.exists(os.path.join(self.grub_dir, "themes", "wonder_beach")))
        self.assertFalse(self.installed("wonder_summer"))


class InteractiveTest(FakeSystemTest):
    def test_numbered_menus(self):
        # Jeu 1 (P3R), perso 1 (Aigis), tenue 2 (FES), confirmer, pas de redémarrage
        self.run_installer(answers=["1", "1", "2", "", "n"])
        self.assertTrue(self.installed("aigis_fes"))

    def test_abort(self):
        output = self.run_installer("--theme", "joker", answers=["n"])
        self.assertIn("Take your time.", output)
        self.assertFalse(self.installed("joker"))

    def test_shuffle_time_without_interface(self):
        output = self.run_installer("--shuffle-time", "-y")
        self.assertIn("SHUFFLE TIME", output)
        self.assertEqual(len(glob.glob(os.path.join(self.grub_dir, "themes", "*", "theme.txt"))), 1)

    def test_french(self):
        output = self.run_installer("--lang", "fr", "--theme", "joker", answers=["o", "n"])
        self.assertIn("Installation terminée !", output)
        self.assertTrue(self.installed("joker"))


if __name__ == "__main__":
    unittest.main()
