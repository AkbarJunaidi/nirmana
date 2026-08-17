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
  5. Advanced Depth       -> moire / wireframe 3D / droste zoom
  6. Depth Exploration    -> anaglyph / l-system / parallax silhouette
  7. Motif Radial         -> arrow burst / dot gradient X / shape cross / weave stripes
  8. Mosaik Voronoi       -> multi-teknik menyatu jadi satu komposisi

Setiap teknik adalah simulasi/algoritma matematis asli (bukan penempatan
bentuk acak), sehingga hasilnya punya struktur & logika visual yang benar
secara kaidah nirmana DKV. Warna bisa hitam-putih (default otentik), palet
kurasi manual, atau ACAK harmonis (dibangun dari teori warna, bukan RGB
comot mentah) -- satu warna untuk seluruh batch, atau berbeda tiap karya.
"""

import os
import random
import time

from generators.composition import VoronoiMosaic
from generators.registry import (
    render_base_technique, BASE_TECHNIQUE_LABELS, ALL_BASE_KEYS,
)
from generators.quality import generate_best_of
from generators.gallery import build_html_gallery
from generators.presets import CURATED_PRESETS
from generators.palette import (
    recolor_duotone, random_palette_name, PALETTES,
    generate_random_palette, is_valid_hex,
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
    "14": "anaglyph",
    "15": "lsystem",
    "16": "parallax",
    "17": "motif_arrow",
    "18": "motif_dotx",
    "19": "motif_shapecross",
    "20": "motif_weave",
    "21": "emosi",
    "22": "sedimen",
    "23": "kekosongan",
    "24": "patahan",
    "25": "kontur_alir",
    "26": "titik",
    "27": "mosaik_voronoi",
    "28": "acak",
}

TECHNIQUE_LABELS = dict(BASE_TECHNIQUE_LABELS)
TECHNIQUE_LABELS["mosaik_voronoi"] = "Mosaik Voronoi (multi-teknik menyatu, satu komposisi)"


def render_technique(technique: str, w: int, h: int, seed: int):
    """Merender satu teknik nirmana pada resolusi & seed tertentu.
    Mengembalikan (PIL.Image, label_teknik). Teknik dasar didelegasikan ke
    registry.py (satu sumber kebenaran); hanya Mosaik Voronoi yang punya
    logika komposisi khusus di sini."""
    if technique == "mosaik_voronoi":
        mosaic = VoronoiMosaic(w, h, seed=seed)
        img = mosaic.generate()
    else:
        img = render_base_technique(technique, w, h, seed)

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

    # 2. Mode Cepat (preset kurasi) atau Mode Manual
    print("\nMode Cepat -- kombinasi teknik+warna yang sudah dikurasi (langsung bagus):")
    print("  0. Mode Manual (pilih teknik & warna sendiri)")
    for k, p in CURATED_PRESETS.items():
        print(f"  {k}. {p.label} -- {p.description}")
    preset_input = input("Masukkan pilihan [Default: 0]: ").strip()

    mode_warna = "hitam_putih"
    palet_terpilih = "hitam_putih"
    warna_acak_tetap = None

    if preset_input in CURATED_PRESETS:
        preset = CURATED_PRESETS[preset_input]
        teknik_terpilih = preset.technique
        if preset.palette_mode == "hitam_putih":
            mode_warna = "hitam_putih"
        elif preset.palette_mode == "palette":
            mode_warna = "palette"
            palet_terpilih = preset.palette_name
        elif preset.palette_mode == "acak_harmonis":
            mode_warna = "acak_tiap"
        print(f"    -> Preset '{preset.label}' dipakai: teknik={TECHNIQUE_LABELS.get(teknik_terpilih, teknik_terpilih)}, "
              f"warna={mode_warna if mode_warna != 'palette' else palet_terpilih}")
    else:
        # --- Mode Manual: teknik ---
        print()
        teknik_key = pilih("Pilih Teknik Nirmana:", TECHNIQUES, "8")
        teknik_terpilih = TECHNIQUES[teknik_key]

        # --- Mode Manual: palet warna ---
        print("\nPilih Palet Warna:")
        print("  0. Hitam-Putih (default, paling otentik nirmana)")
        palette_keys = list(PALETTES.keys())
        for i, k in enumerate(palette_keys, start=1):
            print(f"  {i}. {k}")
        idx_acak_satu = len(palette_keys) + 1
        idx_acak_tiap = len(palette_keys) + 2
        idx_custom = len(palette_keys) + 3
        print(f"  {idx_acak_satu}. ACAK -- satu kombinasi warna acak (harmonis) dipakai untuk semua karya")
        print(f"  {idx_acak_tiap}. ACAK -- kombinasi warna acak BERBEDA setiap karya")
        print(f"  {idx_custom}. CUSTOM -- masukkan kode warna HEX sendiri")
        palet_input = input("Masukkan pilihan [Default: 0]: ").strip()

        mode_warna = "palette"

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
            elif n == idx_custom:
                mode_warna = "acak_satu"
                dark_in = input("    Kode warna GELAP (hex, mis. #1A1A2E): ").strip()
                light_in = input("    Kode warna TERANG (hex, mis. #F5F0E6): ").strip()
                if not is_valid_hex(dark_in):
                    print("    Kode gelap tidak valid, pakai default #0A0A0A")
                    dark_in = "#0A0A0A"
                if not is_valid_hex(light_in):
                    print("    Kode terang tidak valid, pakai default #FAFAFA")
                    light_in = "#FAFAFA"
                warna_acak_tetap = (dark_in if dark_in.startswith("#") else f"#{dark_in}",
                                     light_in if light_in.startswith("#") else f"#{light_in}")
                print(f"    -> Warna custom: dark={warna_acak_tetap[0]}  light={warna_acak_tetap[1]}")

        if mode_warna == "palette" and palet_terpilih == "hitam_putih":
            mode_warna = "hitam_putih"

    if mode_warna == "acak_satu" and warna_acak_tetap is None:
        warna_acak_tetap = generate_random_palette(seed=random.randint(0, 10 ** 9))

    # 3. Jumlah karyaaaaa hiyah
    try:
        jumlah = int(input("\nJumlah karya unik yang ingin di-generate [Default: 3]: ").strip())
    except ValueError:
        jumlah = 3

    # 4. Mode kualitas (opsional): render beberapa kandidat per karya lalu
    #    otomatis pilih yang skornya terbaik (coverage/kontras/detail/centering)
    qa_input = input(
        "\nMode kualitas -- render beberapa kandidat & pilih otomatis yang "
        "terbaik? Masukkan jumlah kandidat per karya (1 = nonaktif) [Default: 1]: "
    ).strip()
    try:
        n_candidates = max(1, int(qa_input))
    except ValueError:
        n_candidates = 3

    print(f"\n[Info] Memulai generative pipeline: {jumlah} karya | {label_rasio} | "
          f"{TECHNIQUE_LABELS.get(teknik_terpilih, 'Acak per karya')} | "
          f"Warna: {mode_warna if mode_warna != 'palette' else palet_terpilih} | "
          f"Kandidat/karya: {n_candidates}\n")

    os.makedirs("outputs", exist_ok=True)
    base_seed = random.randint(1, 999999)
    gallery_entries = []

    for i in range(1, jumlah + 1):
        seed = base_seed + i * 7919

        if teknik_terpilih == "acak":
            technique = random.Random(seed).choice(list(BASE_TECHNIQUE_LABELS.keys()))
        else:
            technique = teknik_terpilih

        t0 = time.time()
        print(f"--- Karya {i}/{jumlah} | Teknik: {TECHNIQUE_LABELS[technique]} | Seed dasar: {seed} ---")

        if n_candidates > 1:
            render_fn = lambda s, _t=technique: render_technique(_t, W, H, s)[0]
            img, chosen_seed, score_info = generate_best_of(
                render_fn, n_candidates=n_candidates, seed_base=seed, verbose=True)
            seed = chosen_seed
        else:
            img, label = render_technique(technique, W, H, seed)

        if technique == "anaglyph":
            pass  # warna merah-cyan adalah konten inti teknik ini, jangan di-recolor
        elif mode_warna == "hitam_putih":
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

        warna_meta = mode_warna if mode_warna != "palette" else palet_terpilih
        gallery_entries.append((path, TECHNIQUE_LABELS[technique],
                                 f"{label_rasio} | Warna: {warna_meta} | Seed: {seed}"))

    print(f"=== Selesai! {jumlah} karya nirmana tersimpan di folder 'outputs/' ===")

    if gallery_entries:
        gallery_path = os.path.join("outputs", "galeri.html")
        build_html_gallery(gallery_entries, gallery_path,
                            title="Python Nirmana Generator -- Hasil Batch")
        print(f"[Info] Galeri HTML dibuat: {gallery_path} (buka di browser untuk lihat semua sekaligus)")


if __name__ == "__main__":
    main()
