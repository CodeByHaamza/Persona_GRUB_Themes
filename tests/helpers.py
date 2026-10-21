"""
Faux système pour tester l'installeur sans toucher au vrai GRUB :
/etc/default/grub, /boot/grub, /sys/class/drm et /etc/grub.d temporaires.
"""
import builtins
import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, ROOT)

import install  # noqa: E402
import install_i18n  # noqa: E402


class FakeSystemTest(unittest.TestCase):
    GRUB_CONFIG = "GRUB_DEFAULT=0\nGRUB_TIMEOUT=5\n"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.grub_dir = os.path.join(self.tmp, "boot", "grub")
        os.makedirs(self.grub_dir)
        self.cfg = os.path.join(self.tmp, "grub")
        with open(self.cfg, "w") as f:
            f.write(self.GRUB_CONFIG)
        self.drm = os.path.join(self.tmp, "drm")
        self.efi = os.path.join(self.tmp, "efi")
        self.grub_d = os.path.join(self.tmp, "grub.d")
        os.makedirs(self.grub_d)
        self.calls = []

        patches = [
            mock.patch.object(install, "GRUB_CONFIG_FILE", self.cfg),
            mock.patch.object(install, "GRUB_CONFIG_ORIGINAL", self.cfg + ".persona.orig"),
            mock.patch.object(install, "DRM_DIR", self.drm),
            mock.patch.object(install, "EFI_DIR", self.efi),
            mock.patch.object(install, "VELVET_ROOM_SCRIPT", os.path.join(self.grub_d, "42_persona_velvet_room")),
            mock.patch.object(install, "detect_grub", lambda: (self.grub_dir, ["fake-mkconfig"])),
            mock.patch.object(install, "check_root", lambda: None),
            mock.patch.object(install, "clear_screen", lambda: None),
            mock.patch.object(install.subprocess, "run", lambda cmd, check=False: self.calls.append(cmd)),
            # Le faux système n'a aucun binaire : sans ça, la question
            # os-prober apparaît ou non selon la machine qui lance les tests,
            # et les réponses scriptées ne tombent plus en face.
            mock.patch.object(install.shutil, "which", lambda name: None),
            # Interface stylée désactivée : les tests passent par les menus numérotés
            mock.patch.object(install, "install_ui", None),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        install_i18n.set_language("en")
        self.addCleanup(install_i18n.set_language, "en")

    def run_installer(self, *argv, answers=()):
        """Lance install.py avec ces arguments ; renvoie ce qui a été affiché"""
        answers = iter(answers)
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["install.py", *argv]), \
                mock.patch.object(builtins, "input", lambda prompt="": next(answers)), \
                redirect_stdout(output):
            install.DRY_RUN = False
            install.main()
        return output.getvalue()

    def config(self):
        with open(self.cfg) as f:
            return f.read()

    def installed(self, theme):
        return os.path.isfile(os.path.join(self.grub_dir, "themes", theme, "theme.txt"))

    def add_screen(self, status, modes):
        connector = os.path.join(self.drm, "card1-HDMI-A-1")
        os.makedirs(connector, exist_ok=True)
        with open(os.path.join(connector, "status"), "w") as f:
            f.write(status + "\n")
        with open(os.path.join(connector, "modes"), "w") as f:
            f.write(modes)
