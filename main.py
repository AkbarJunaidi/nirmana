"""
main.py
========
PYTHON NIRMANA GENERATOR -- Sistem DKV Otentik
------------------------------------------------
Titik masuk (entry point) CLI. Menggabungkan seluruh mesin nirmana:

  1. Nirmana Garis        -> distorsi vortex pada garis paralel (op-art flow)
  2. Nirmana Organik      -> hatching burst / concentric cells / DLA branching
  3. Nirmana Geometrik    -> isometric cubes / spiral checkerboard / distorted grid
  4. Depth Illusion       -> perspective tunnel / shatter web / spiral hatch burst
  5. Kombinasi Multi-Layer -> papan studi berlabel / mosaik voronoi

Setiap teknik adalah simulasi/algoritma matematis asli (bukan penempatan
bentuk acak), sehingga hasilnya punya struktur & logika visual yang benar
secara kaidah nirmana DKV. Warna bisa hitam-putih (default otentik), palet
kurasi manual, atau ACAK harmonis (dibangun dari teori warna, bukan RGB
comot mentah) -- satu warna untuk seluruh batch, atau berbeda tiap karya.
"""

import os
import random
import sys
import time

from generators.line_nirmana import LineNirmanaGenerator
from generators.organic_patterns import OrganicNirmanaGenerator
from generators.geometric_patterns import GeometricNirmanaGenerator
from generators.composition import StudyBoard, VoronoiMosaic
from generators.depth_illusion import DepthIllusionGenerator
from generators.advanced_depth import AdvancedDepthGenerator
from generators.palette import (
    recolor_duotone, random_palette_name, PALETTES,
    generate_random_palette,
)

ASPECT_RATIOS = {
    "1": ("1:1 (Instagram Post)", (1600, 1600)),
    "2": ("4:5 (Feed Sosmed)", (1350, 1687)),
    "3": ("9:16 (Story/Reels)", (1080, 1920)),
    "4": ("16:9 (Landscape/Banner)", (1920, 1080)),
    "5": ("A4 Potrait (Cetak 300 DPI)", (2480, 3508)),
    "6": ("4K Ultra HD", (3840, 2160)),
}

TECHNIQUES = {
    "1": "garis",
    "2": "organik_burst",
    "3": "organik_cells",
    "4": "organik_branching",
    "5": "geometrik_kubus",
    "6": "geometrik_spiral",
    "7": "geometrik_grid",
    "8": "depth_tunnel",
    "9": "depth_shatter",
    "10": "depth_spiral",
    "11": "moire",
    "12": "wireframe",
    "13": "droste",
    "14": "papan_studi",
    "15": "mosaik_voronoi",
    "16": "acak",
}

TECHNIQUE_LABELS = {
    "garis": "Nirmana Garis (Op-Art Flow Distortion)",
    "organik_burst": "Nirmana Organik - Hatching Burst",
    "organik_cells": "Nirmana Organik - Concentric Cells",
    "organik_branching": "Nirmana Organik - DLA Branching (Karang)",
    "geometrik_kubus": "Nirmana Geometrik - Isometric Cubes",
    "geometrik_spiral": "Nirmana Geometrik - Spiral Checkerboard",
    "geometrik_grid": "Nirmana Geometrik - Distorted Grid",
    "depth_tunnel": "Depth Illusion - Perspective Tunnel",
    "depth_shatter": "Depth Illusion - Shatter Web (Closure)",
    "depth_spiral": "Depth Illusion - Spiral Hatch Burst",
    "moire": "Advanced Depth - Moire Interference",
    "wireframe": "Advanced Depth - Wireframe Mesh 3D",
    "droste": "Advanced Depth - Droste Zoom (Rekursi Tak Berhingga)",
    "papan_studi": "Papan Studi (grid perbandingan multi-teknik berlabel)",
    "mosaik_voronoi": "Mosaik Voronoi (multi-teknik menyatu, satu komposisi)",
}


def render_technique(technique: str, w: int, h: int, seed: int):
    """Merender satu teknik nirmana pada resolusi & seed tertentu.
    Mengembalikan (PIL.Image, label_teknik)."""
    if technique == "garis":
        gen = LineNirmanaGenerator(w, h, seed=seed)
        band_count = random.Random(seed).randint(16, 30)
        img = gen.generate(band_count=band_count)

    elif technique == "organik_burst":
        gen = OrganicNirmanaGenerator(w, h, seed=seed)
        img = gen.generate_hatching_burst()

    elif technique == "organik_cells":
        gen = OrganicNirmanaGenerator(w, h, seed=seed)
        img = gen.generate_concentric_cells()

    elif technique == "organik_branching":
        gen = OrganicNirmanaGenerator(w, h, seed=seed)
        img = gen.generate_reaction_diffusion_blob()

    elif technique == "geometrik_kubus":
        gen = GeometricNirmanaGenerator(w, h, seed=seed)
        img = gen.generate_isometric_cubes()

    elif technique == "geometrik_spiral":
        gen = GeometricNirmanaGenerator(w, h, seed=seed)
        img = gen.generate_spiral_checkerboard()

    elif technique == "geometrik_grid":
        gen = GeometricNirmanaGenerator(w, h, seed=seed)
        img = gen.generate_distorted_grid()

    elif technique == "depth_tunnel":
        gen = DepthIllusionGenerator(w, h, seed=seed)
        img = gen.generate_perspective_tunnel()

    elif technique == "depth_shatter":
        gen = DepthIllusionGenerator(w, h, seed=seed)
        img = gen.generate_shatter_web()

    elif technique == "depth_spiral":
        gen = DepthIllusionGenerator(w, h, seed=seed)
        img = gen.generate_spiral_hatch_burst()

    elif technique == "moire":
        gen = AdvancedDepthGenerator(w, h, seed=seed)
        img = gen.generate_moire_interference()

    elif technique == "wireframe":
        gen = AdvancedDepthGenerator(w, h, seed=seed)
        img = gen.generate_wireframe_mesh()

    elif technique == "droste":
        rng = random.Random(seed)
        base_choice = rng.choice(["garis", "geometrik_kubus", "geometrik_spiral",
                                   "geometrik_grid", "organik_cells"])
        base_img, _ = render_technique(base_choice, w, h, seed + 999)
        gen = AdvancedDepthGenerator(w, h, seed=seed)
        img = gen.generate_droste_zoom(base_image=base_img, levels=rng.randint(4, 6))

    elif technique == "papan_studi":
        board = StudyBoard(w, h, seed=seed)
        rng = random.Random(seed)
        rows = rng.choice([2, 3])
        cols = 2
        img = board.generate(rows=rows, cols=cols, column_headers=("ORGANIK", "GEOMETRIK"))

    elif technique == "mosaik_voronoi":
        mosaic = VoronoiMosaic(w, h, seed=seed)
        img = mosaic.generate()

    else:
        raise ValueError(f"Teknik tidak dikenali: {technique}")

    return img, TECHNIQUE_LABELS[technique]


def pilih(prompt: str, mapping: dict, default_key: str) -> str:
    print(prompt)
    for k, v in mapping.items():
        label = v[0] if isinstance(v, tuple) else v
        print(f"  {k}. {label}")
    pilihan = input(f"Masukkan pilihan [Default: {default_key}]: ").strip()
    return pilihan if pilihan in mapping else default_key


def main():
    print("=" * 60)
    print("   PYTHON NIRMANA GENERATOR -- SISTEM DKV OTENTIK")
    print("=" * 60)

    # 1. Rasio & Resolusi
    rasio_key = pilih("\nPilih Rasio & Resolusi:", ASPECT_RATIOS, "1")
    label_rasio, (W, H) = ASPECT_RATIOS[rasio_key]

    # 2. Teknik Nirmana
    print()
    teknik_key = pilih("Pilih Teknik Nirmana:", TECHNIQUES, "8")
    teknik_terpilih = TECHNIQUES[teknik_key]

    # 3. Palet Warna
    print("\nPilih Palet Warna:")
    print("  0. Hitam-Putih (default, paling otentik nirmana)")
    palette_keys = list(PALETTES.keys())
    for i, k in enumerate(palette_keys, start=1):
        print(f"  {i}. {k}")
    idx_acak_satu = len(palette_keys) + 1
    idx_acak_tiap = len(palette_keys) + 2
    print(f"  {idx_acak_satu}. ACAK -- satu kombinasi warna acak (harmonis) dipakai untuk semua karya")
    print(f"  {idx_acak_tiap}. ACAK -- kombinasi warna acak BERBEDA setiap karya")
    palet_input = input("Masukkan pilihan [Default: 0]: ").strip()

    mode_warna = "palette"       # "palette" | "hitam_putih" | "acak_satu" | "acak_tiap"
    palet_terpilih = "hitam_putih"
    warna_acak_tetap = None

    if palet_input.isdigit():
        n = int(palet_input)
        if 1 <= n <= len(palette_keys):
            palet_terpilih = palette_keys[n - 1]
        elif n == idx_acak_satu:
            mode_warna = "acak_satu"
            warna_acak_tetap = generate_random_palette(seed=random.randint(0, 10 ** 9))
            print(f"    -> Warna acak terpilih: dark={warna_acak_tetap[0]}  light={warna_acak_tetap[1]}")
        elif n == idx_acak_tiap:
            mode_warna = "acak_tiap"

    if mode_warna == "palette" and palet_terpilih == "hitam_putih":
        mode_warna = "hitam_putih"

    # 4. Jumlah karya
    try:
        jumlah = int(input("\nJumlah karya unik yang ingin di-generate [Default: 3]: ").strip())
    except ValueError:
        jumlah = 3

    print(f"\n[Info] Memulai generative pipeline: {jumlah} karya | {label_rasio} | "
          f"{TECHNIQUE_LABELS.get(teknik_terpilih, 'Acak per karya')} | "
          f"Warna: {mode_warna if mode_warna != 'palette' else palet_terpilih}\n")

    os.makedirs("outputs", exist_ok=True)
    base_seed = random.randint(1, 999999)

    for i in range(1, jumlah + 1):
        seed = base_seed + i * 7919

        if teknik_terpilih == "acak":
            technique_choices = ["garis"] + [t for t in TECHNIQUE_LABELS.keys()
                                              if t not in ("garis", "papan_studi", "mosaik_voronoi")]
            technique = random.Random(seed).choice(technique_choices)
        else:
            technique = teknik_terpilih

        t0 = time.time()
        print(f"--- Karya {i}/{jumlah} | Teknik: {TECHNIQUE_LABELS[technique]} | Seed: {seed} ---")

        img, label = render_technique(technique, W, H, seed)

        if mode_warna == "hitam_putih":
            pass
        elif mode_warna == "palette":
            img = recolor_duotone(img, palet_terpilih)
        elif mode_warna == "acak_satu":
            img = recolor_duotone(img, custom_colors=warna_acak_tetap)
        elif mode_warna == "acak_tiap":
            warna_i = generate_random_palette(seed=seed)
            img = recolor_duotone(img, custom_colors=warna_i)
            print(f"    Warna karya ini: dark={warna_i[0]}  light={warna_i[1]}")

        nama_file = f"nirmana_{technique}_{rasio_key}_{i}_seed{seed}.png"
        path = os.path.join("outputs", nama_file)
        img.save(path, quality=95)

        dt = time.time() - t0
        print(f"    -> Tersimpan: {path} ({dt:.2f}s)\n")

    print(f"=== Selesai! {jumlah} karya nirmana tersimpan di folder 'outputs/' ===")


if __name__ == "__main__":
    main()
