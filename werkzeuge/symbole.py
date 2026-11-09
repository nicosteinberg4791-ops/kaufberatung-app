# -*- coding: utf-8 -*-
"""Erzeugt die PNG-Symbole der App aus app/icons/*.svg (Chrome headless rendert, Pillow verkleinert).

Aufruf:  python -I werkzeuge/symbole.py
Nur vorhandene Werkzeuge: Google Chrome (oder Edge) und Pillow. Ergebnis wird versioniert, der Build braucht Chrome nicht.
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

WURZEL = Path(__file__).resolve().parent.parent
ICONS = WURZEL / "app" / "icons"
BROWSER = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
           Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]


def rendere(svg, png):
    exe = next(p for p in BROWSER if p.exists())
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([str(exe), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}",
                        "--default-background-color=00000000", "--window-size=512,512",
                        f"--force-device-scale-factor={FAKTOR}",
                        f"--screenshot={png}", svg.as_uri()], check=True, capture_output=True, timeout=60)
    with Image.open(png) as im:
        assert im.size == (512 * FAKTOR, 512 * FAKTOR), f"{png.name}: {im.size}"


# Doppelte Auflösung rendern und erst danach verkleinern: sauberere Kanten und Verläufe (Schärfe auf dem Handy)
FAKTOR = 2


def main():
    for name, svg in (("icon", ICONS / "icon.svg"), ("icon-maskable", ICONS / "icon-maskable.svg")):
        gross = ICONS / f"{name}-512.png"
        rendere(svg, gross)
        with Image.open(gross) as im:
            im = im.convert("RGBA")
            im.resize((512, 512), Image.LANCZOS).save(gross, optimize=True)
            im.resize((192, 192), Image.LANCZOS).save(ICONS / f"{name}-192.png", optimize=True)
            if name == "icon-maskable":
                im.resize((180, 180), Image.LANCZOS).convert("RGB").save(ICONS / "apple-touch-icon.png", optimize=True)
        print("geschrieben:", name, "512/192")


if __name__ == "__main__":
    main()
