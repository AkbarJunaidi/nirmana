"""
palette.py
==========
Utility ringan untuk me-recolor hasil nirmana (yang secara default
hitam-putih -- sesuai kaidah nirmana garis/tekstur klasik) menjadi duotone
memakai palet warna bermakna (semantic palette), untuk yang ingin variasi
warna tanpa mengubah struktur komposisinya sama sekali.
"""

import random
from typing import Tuple
from PIL import Image
import numpy as np

PALETTES = {
    "hitam_putih":      ("#0A0A0A", "#FAFAFA"),
    "swiss_editorial":  ("#1A1A1A", "#EAEAEA"),
    "bauhaus_modern":   ("#121212", "#F3F3F3"),
    "terracotta_earth": ("#3A2A20", "#F4EBD0"),
    "monochrome_slate": ("#0F172A", "#F8FAFC"),
    "cyber_neon":       ("#050510", "#00F5D4"),
    "acid_chromatic":   ("#0B0C10", "#CCFF00"),
    "navy_paper":       ("#101A2E", "#F6F1E6"),
}


def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def recolor_duotone(img: Image.Image, palette_name: str = "hitam_putih") -> Image.Image:
    """Memetakan citra grayscale/hitam-putih ke dua warna (dark, light)
    berdasarkan intensitas piksel, mempertahankan anti-aliasing (blend halus)."""
    dark_hex, light_hex = PALETTES.get(palette_name, PALETTES["hitam_putih"])
    dark = np.array(_hex_to_rgb(dark_hex), dtype=np.float32)
    light = np.array(_hex_to_rgb(light_hex), dtype=np.float32)

    gray = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    gray = gray[..., None]  # (H,W,1) untuk broadcasting

    out = dark * (1 - gray) + light * gray
    return Image.fromarray(out.astype(np.uint8), mode="RGB")


def random_palette_name(seed: int = None, exclude_bw: bool = False) -> str:
    rng = random.Random(seed)
    keys = [k for k in PALETTES if not (exclude_bw and k == "hitam_putih")]
    return rng.choice(keys)
