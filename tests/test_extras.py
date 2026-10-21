"""Velvet Room, Ventoy et phrases des All-Out Attacks"""
import json
import os
import unittest

from unittest import mock

from helpers import FakeSystemTest, install


class VelvetRoomTest(FakeSystemTest):
    def test_option_adds_script_and_icon(self):
        self.run_installer("--theme", "joker", "-y", "--velvet-room")
        self.assertTrue(os.access(install.VELVET_ROOM_SCRIPT, os.X_OK))
        self.assertTrue(os.path.isfile(os.path.join(self.grub_dir, "themes", "joker", "icons", "velvet.png")))
        # Un thème installé ensuite récupère aussi l'icône
        self.run_installer("--theme", "makoto", "-y")
        self.assertTrue(os.path.isfile(os.path.join(self.grub_dir, "themes", "makoto", "icons", "velvet.png")))

    def test_uninstall_and_restore_remove_it(self):
        self.run_installer("--theme", "joker", "-y", "--velvet-room")
        self.run_installer("--uninstall")
        self.assertFalse(os.path.exists(install.VELVET_ROOM_SCRIPT))
        self.run_installer("--theme", "joker", "-y", "--velvet-room")
        self.run_installer("--restore")
        self.assertFalse(os.path.exists(install.VELVET_ROOM_SCRIPT))

    def test_question_only_on_uefi(self):
        os.makedirs(self.efi)
        self.run_installer("--theme", "wonder", answers=["y", "y", "n"])
        self.assertTrue(os.path.exists(install.VELVET_ROOM_SCRIPT))

    def test_no_question_without_uefi(self):
        self.run_installer("--theme", "skull", answers=["y", "n"])
        self.assertFalse(os.path.exists(install.VELVET_ROOM_SCRIPT))

    def test_grub_script_is_valid_shell(self):
        self.assertTrue(install.VELVET_ROOM_CONTENT.startswith("#!/bin/sh\n"))
        self.assertIn("fwsetup", install.VELVET_ROOM_CONTENT)
        self.assertIn('--class velvet', install.VELVET_ROOM_CONTENT)


class VentoyTest(FakeSystemTest):
    def setUp(self):
        super().setUp()
        self.usb = os.path.join(self.tmp, "usb")
        os.makedirs(os.path.join(self.usb, "ventoy"))
        self.json_path = os.path.join(self.usb, "ventoy", "ventoy.json")

    def test_keeps_other_settings(self):
        with open(self.json_path, "w") as f:
            json.dump({"control": [{"VTOY_DEFAULT_MENU_MODE": "1"}]}, f)
        self.run_installer("--ventoy", self.usb, "--theme", "wonder_beach")
        with open(self.json_path) as f:
            config = json.load(f)
        self.assertEqual(config["control"], [{"VTOY_DEFAULT_MENU_MODE": "1"}])
        self.assertEqual(config["theme"]["file"], "/ventoy/themes/wonder_summer/theme.txt")
        self.assertTrue(os.path.isfile(os.path.join(self.usb, "ventoy", "themes", "wonder_summer", "theme.txt")))
        self.assertTrue(any(name.startswith("ventoy.json.bak.") for name in os.listdir(os.path.join(self.usb, "ventoy"))))

    def test_invalid_json_is_left_alone(self):
        with open(self.json_path, "w") as f:
            f.write("{oops")
        with self.assertRaises(SystemExit):
            self.run_installer("--ventoy", self.usb, "--theme", "skull")
        with open(self.json_path) as f:
            self.assertEqual(f.read(), "{oops")

    def test_dry_run(self):
        self.run_installer("--ventoy", self.usb, "--theme", "joker", "--dry-run")
        self.assertFalse(os.path.exists(self.json_path))


class OsProberTest(FakeSystemTest):
    def test_flag_enables_it(self):
        self.run_installer("--theme", "joker", "-y", "--os-prober")
        self.assertIn("GRUB_DISABLE_OS_PROBER=false", self.config())

    def test_existing_line_is_replaced_not_duplicated(self):
        with open(self.cfg, "w") as f:
            f.write(self.GRUB_CONFIG + 'GRUB_DISABLE_OS_PROBER=true\n')
        self.run_installer("--theme", "joker", "-y", "--os-prober")
        config = self.config()
        self.assertIn("GRUB_DISABLE_OS_PROBER=false", config)
        self.assertNotIn("GRUB_DISABLE_OS_PROBER=true", config)
        self.assertEqual(config.count("GRUB_DISABLE_OS_PROBER"), 1)

    def test_not_touched_without_the_flag(self):
        self.run_installer("--theme", "joker", "-y")
        self.assertNotIn("GRUB_DISABLE_OS_PROBER", self.config())

    def test_only_offered_when_os_prober_is_installed(self):
        # os-prober absent : pas de question, donc une seule réponse suffit
        with mock.patch.object(install.shutil, "which", lambda name: None):
            self.assertFalse(install.os_prober_available())

    def test_already_enabled_is_not_offered_again(self):
        with open(self.cfg, "w") as f:
            f.write(self.GRUB_CONFIG + 'GRUB_DISABLE_OS_PROBER=false\n')
        with mock.patch.object(install.shutil, "which", lambda name: "/usr/bin/os-prober"):
            self.assertFalse(install.os_prober_available())

    def test_offered_when_installed_and_disabled(self):
        with mock.patch.object(install.shutil, "which", lambda name: "/usr/bin/os-prober"):
            self.assertTrue(install.os_prober_available())


class RandomTest(FakeSystemTest):
    def test_random_installs_a_real_theme(self):
        self.run_installer("--random", "-y")
        themes = os.listdir(os.path.join(self.grub_dir, "themes"))
        self.assertEqual(len(themes), 1)
        self.assertTrue(self.installed(themes[0]))

    def test_random_keeps_the_theme_in_the_config(self):
        self.run_installer("--random", "-y")
        self.assertIn("GRUB_THEME=", self.config())


class IconColorTest(FakeSystemTest):
    def icon_palette(self, theme, name="ubuntu.png"):
        path = os.path.join(self.grub_dir, "themes", theme, "icons", name)
        data = open(path, "rb").read()
        offset = 8
        while offset < len(data):
            length = int.from_bytes(data[offset:offset + 4], "big")
            if data[offset + 4:offset + 8] == b"PLTE":
                raw = data[offset + 8:offset + 8 + length]
                return [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]
            offset += 12 + length
        return []

    def test_named_colour_repaints_the_icons(self):
        self.run_installer("--theme", "makoto", "-y", "--icon-color", "green")
        palette = self.icon_palette("makoto")
        self.assertTrue(palette)
        # le blanc du logo reste, le bleu du personnage a disparu
        self.assertIn((255, 255, 255), palette)
        self.assertNotIn((50, 152, 235), palette)

    def test_hex_colour_is_accepted(self):
        self.run_installer("--theme", "makoto", "-y", "--icon-color", "#884400")
        reds = [c[0] for c in self.icon_palette("makoto")]
        self.assertTrue(max(reds) >= 136)

    def test_the_repo_copy_is_left_alone(self):
        before = open(os.path.join(
            install.THEMES_DIR, "persona3_reload", "makoto", "icons", "ubuntu.png"), "rb").read()
        self.run_installer("--theme", "makoto", "-y", "--icon-color", "red")
        after = open(os.path.join(
            install.THEMES_DIR, "persona3_reload", "makoto", "icons", "ubuntu.png"), "rb").read()
        self.assertEqual(before, after)

    def test_without_the_option_the_icons_keep_the_character_colour(self):
        self.run_installer("--theme", "makoto", "-y")
        self.assertIn((50, 152, 235), self.icon_palette("makoto"))

    def test_a_light_colour_is_darkened_so_the_logo_stays_readable(self):
        # blanc pur : un logo blanc dessus serait invisible
        self.run_installer("--theme", "makoto", "-y", "--icon-color", "#FFFFFF")
        palette = self.icon_palette("makoto")
        darkest = min(palette, key=lambda c: sum(c))
        self.assertLess(sum(darkest), 3 * 255)

    def test_an_unknown_colour_is_refused(self):
        with self.assertRaises(SystemExit):
            self.run_installer("--theme", "makoto", "-y", "--icon-color", "mauve-ish")


class QuotesTest(unittest.TestCase):
    def test_quotes_and_arcana_match_existing_themes(self):
        data = install.scan_themes()
        themes = {os.path.basename(p) for c in data.values() for v in c.values() for p in v.values()}
        self.assertLessEqual(set(install.THEME_QUOTES), themes)
        self.assertLessEqual(set(install.THEME_ARCANA), themes)


if __name__ == "__main__":
    unittest.main()
