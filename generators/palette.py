"""
palette.py
==========
Utility untuk me-recolor hasil nirmana (yang secara default hitam-putih --
sesuai kaidah nirmana garis/tekstur klasik) jadi duotone.

Dua sumber warna:
1. PALETTES kurasi manual (tetap, hasilnya konsisten & teruji enak dilihat).
2. generate_random_palette() -- warna ACAK tapi tetap harmonis, dibangun
   lewat teori warna dasar (complementary / analogous / triadic / split-
   complementary / monochrome-tint) di ruang HSL, bukan RGB asal comot
   (RGB acak murni sering menghasilkan kombinasi kotor/kontras jelek).
"""

import colorsys
import random
from typing import Tuple
from PIL import Image
import numpy as np

PALETTES = {
    "hitam_putih":       ("#0A0A0A", "#FAFAFA"),
    "swiss_editorial":   ("#1A1A1A", "#EAEAEA"),
    "bauhaus_modern":    ("#121212", "#F3F3F3"),
    "terracotta_earth":  ("#3A2A20", "#F4EBD0"),
    "monochrome_slate":  ("#0F172A", "#F8FAFC"),
    "cyber_neon":        ("#050510", "#00F5D4"),
    "acid_chromatic":    ("#0B0C10", "#CCFF00"),
    "navy_paper":        ("#101A2E", "#F6F1E6"),
    "royal_gold":        ("#151022", "#E8C874"),
    "coral_reef":        ("#0D2B2E", "#FF6F59"),
    "forest_moss":       ("#10210F", "#C9E4A5"),
    "plum_blossom":      ("#1F0F26", "#F2B6D2"),
    "ink_indigo":        ("#0B0F2B", "#A6C8FF"),
    "sunset_ember":      ("#210A08", "#FF9E5E"),
    "mint_charcoal":     ("#111815", "#9FE6C6"),
    "crimson_paper":     ("#160607", "#F5E6D3"),
    "peach_blush":       ("#2B1410", "#FFD8C2"),
    "olive_khaki":       ("#1D1C0C", "#D9CB9E"),
    "steel_blue":        ("#0C1A24", "#8FB8D6"),
    "wine_burgundy":     ("#1C0509", "#E8AAB0"),
    "arctic_teal":       ("#04191B", "#B8F0E6"),
    "amber_glow":        ("#1E1204", "#FFC24B"),
    "lavender_grey":     ("#161522", "#D8D3EE"),
    "copper_rust":       ("#211008", "#D97B4A"),
    "seafoam_dusk":      ("#0A1F1C", "#A9E4C6"),
    "graphite_ivory":    ("#161616", "#F2EFE6"),
    "electric_violet":   ("#0D0620", "#B388FF"),
    "desert_sand":       ("#241A0D", "#EAC98F"),
    "midnight_rose":     ("#170A15", "#F2A6C9"),
    "chartreuse_ink":    ("#0E1204", "#D6F24B"),
    "slate_lilac":       ("#141220", "#C9BFE8"),
    "tangerine_smoke":   ("#1D0F06", "#FF9F5B"),
}


def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def is_valid_hex(h: str) -> bool:
    h = h.strip().lstrip("#")
    if len(h) != 6:
        return False
    try:
        int(h, 16)
        return True
    except ValueError:
        return False


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """h dalam derajat 0-360, s & l dalam 0-1."""
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
    return (round(r * 255), round(g * 255), round(b * 255))


def recolor_duotone(img: Image.Image, palette_name: str = "hitam_putih",
                     custom_colors: Tuple[str, str] = None) -> Image.Image:
    """Memetakan citra grayscale/hitam-putih ke dua warna (dark, light)
    berdasarkan intensitas piksel, mempertahankan anti-aliasing (blend halus).
    Jika custom_colors diberikan (dark_hex, light_hex), dipakai langsung --
    dipakai oleh mode warna acak."""
    if custom_colors is not None:
        dark_hex, light_hex = custom_colors
    else:
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


# ----------------------------------------------------------------------
# GENERATOR WARNA ACAK HARMONIS (teori warna, bukan RGB comot mentah)
# ----------------------------------------------------------------------
_SCHEMES = ["complementary", "analogous", "triadic", "split_complementary", "monochrome_tint"]


def generate_random_palette(seed: int = None, scheme: str = None) -> Tuple[str, str]:
    """Menghasilkan sepasang warna (dark_hex, light_hex) yang acak namun
    harmonis, dibangun di ruang HSL:
    - dark: selalu gelap & cukup jenuh (jadi tetap terbaca sebagai "garis/
      struktur" pada komposisi, seperti warna hitam pada nirmana asli).
    - light: dipilih dari salah satu skema teori warna relatif ke hue dark,
      dengan lightness tinggi & saturasi rendah-sedang (jadi tetap nyaman
      dipakai sebagai "kertas/latar").
    Kontras lightness antara dark & light selalu dijaga besar supaya motif
    nirmana tetap terbaca jelas, bukan cuma sekadar dua warna acak berdekatan.
    """
    rng = random.Random(seed)
    scheme = scheme or rng.choice(_SCHEMES)

    base_hue = rng.uniform(0, 360)
    dark_sat = rng.uniform(0.45, 0.85)
    dark_light = rng.uniform(0.07, 0.16)
    dark_rgb = _hsl_to_rgb(base_hue, dark_sat, dark_light)

    if scheme == "complementary":
        light_hue = base_hue + 180
    elif scheme == "analogous":
        light_hue = base_hue + rng.uniform(-35, 35)
    elif scheme == "triadic":
        light_hue = base_hue + rng.choice([120, 240])
    elif scheme == "split_complementary":
        light_hue = base_hue + rng.choice([150, 210])
    else:  # monochrome_tint
        light_hue = base_hue

    light_sat = rng.uniform(0.12, 0.45) if scheme != "monochrome_tint" else rng.uniform(0.05, 0.2)
    light_light = rng.uniform(0.90, 0.97)
    light_rgb = _hsl_to_rgb(light_hue, light_sat, light_light)

    return _rgb_to_hex(dark_rgb), _rgb_to_hex(light_rgb)


def generate_random_palette_batch(n: int, seed: int = None) -> list:
    """n pasang warna acak berbeda, berguna untuk mode 'acak per karya'
    dalam satu batch generate."""
    rng = random.Random(seed)
    return [generate_random_palette(seed=rng.randint(0, 10 ** 9)) for _ in range(n)]
