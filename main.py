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

import argparse
import os
import random
import sys
import time

from generators.composition import VoronoiMosaic
from generators.registry import (
    render_base_technique, BASE_TECHNIQUE_LABELS, ALL_BASE_KEYS, SPARSE_BY_DESIGN,
    render_svg_technique, SVG_CAPABLE_KEYS,
)
from generators.quality import generate_best_of, generate_critique
from generators.gallery import build_html_gallery
from generators.presets import CURATED_PRESETS
from generators.palette import (
    recolor_duotone, random_palette_name, PALETTES,
    generate_random_palette, is_valid_hex,
)


# Setiap preset resolusi juga membawa metadata DPI yang PRESISI secara
# fisik (bukan cuma jumlah piksel) -- supaya file yang sama, saat dibuka di
# software cetak (InDesign, Illustrator, print shop) maupun media digital
# (Instagram, web, presentasi), selalu terbaca ukuran fisik yang benar.
# dpi=None berarti "murni digital" (tidak ada ukuran fisik yang relevan,
# software akan default 72/96 dpi -- itu sudah benar untuk layar).
ASPECT_RATIOS = {
    "1": ("1:1 (Instagram Post)", (1600, 1600), None),
    "2": ("4:5 (Feed Sosmed)", (1350, 1687), None),
    "3": ("9:16 (Story/Reels)", (1080, 1920), None),
    "4": ("16:9 (Landscape/Banner)", (1920, 1080), None),
    "5": ("A4 Potrait (Cetak 300 DPI, 21x29.7cm)", (2480, 3508), (300, 300)),
    "6": ("A3 Potrait (Cetak 300 DPI, 29.7x42cm)", (3508, 4961), (300, 300)),
    "7": ("Kartu Nama (Cetak 300 DPI + bleed, 9.4x5.5cm)", (1110, 650), (300, 300)),
    "8": ("Poster Besar (150 DPI, 60x90cm)", (3543, 5315), (150, 150)),
    "9": ("Kanvas Persegi Cetak (300 DPI, 40x40cm)", (4724, 4724), (300, 300)),
    "10": ("4K Ultra HD (Layar/Wallpaper)", (3840, 2160), None),
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
    "27": "hierarki_paralel",
    "28": "hierarki_konsentris",
    "29": "hierarki_radial",
    "30": "bidang",
    "31": "value_grid",
    "32": "irama_repetisi",
    "33": "irama_progresi",
    "34": "irama_oposisi",
    "35": "keseimbangan_asimetris",
    "36": "mosaik_voronoi",
    "37": "acak",
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


def run_pipeline(rasio_key: str, W: int, H: int, dpi_meta, label_rasio: str,
                  teknik_terpilih: str, mode_warna: str, palet_terpilih: str,
                  warna_acak_tetap, jumlah: int, n_candidates: int,
                  export_svg: bool, output_dir: str = "outputs") -> list:
    """Loop generatif inti -- dipakai baik oleh mode interaktif maupun mode
    CLI non-interaktif (--technique dkk), supaya logikanya satu sumber
    kebenaran (tidak disalin dua kali dan berisiko drift). Mengembalikan
    daftar path file yang dihasilkan."""
    print(f"\n[Info] Memulai generative pipeline: {jumlah} karya | {label_rasio} | "
          f"{TECHNIQUE_LABELS.get(teknik_terpilih, 'Acak per karya')} | "
          f"Warna: {mode_warna if mode_warna != 'palette' else palet_terpilih} | "
          f"Kandidat/karya: {n_candidates}\n")

    os.makedirs(output_dir, exist_ok=True)
    base_seed = random.randint(1, 999999)
    gallery_entries = []
    saved_paths = []

    # Sistem "acak" pakai SHUFFLE BAG (sampling tanpa pengembalian), bukan
    # random.choice() independen tiap karya -- random.choice() independen
    # rawan memilih teknik yang SAMA berkali-kali dalam satu batch pendek
    # (soal probabilitas murni: dengan ~30 teknik & batch 5 karya, peluang
    # ada duplikat > 25%). Shuffle bag menjamin semua teknik terpakai
    # merata dulu satu-satu (urutan diacak) sebelum ada yang terulang --
    # itulah "benar-benar acak" yang terasa adil buat mata, bukan acak
    # matematis independen yang secara persepsi terasa "kok itu-itu lagi".
    acak_rng = random.Random(base_seed)
    acak_bag: list = []

    def ambil_teknik_acak() -> str:
        nonlocal acak_bag
        if not acak_bag:
            acak_bag = list(ALL_BASE_KEYS)
            acak_rng.shuffle(acak_bag)
        return acak_bag.pop()

    for i in range(1, jumlah + 1):
        seed = acak_rng.randint(1, 10 ** 9) if teknik_terpilih == "acak" else base_seed + i * 7919

        if teknik_terpilih == "acak":
            technique = ambil_teknik_acak()
        else:
            technique = teknik_terpilih

        t0 = time.time()
        print(f"--- Karya {i}/{jumlah} | Teknik: {TECHNIQUE_LABELS[technique]} | Seed dasar: {seed} ---")
        sparse_ok = technique in SPARSE_BY_DESIGN

        if n_candidates > 1:
            render_fn = lambda s, _t=technique: render_technique(_t, W, H, s)[0]
            img, chosen_seed, score_info = generate_best_of(
                render_fn, n_candidates=n_candidates, seed_base=seed, verbose=True,
                sparse_ok=sparse_ok)
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
        path = os.path.join(output_dir, nama_file)
        # dpi_meta ditanam sebagai metadata fisik PNG (pHYs chunk) -- kalau
        # None (preset digital murni), tidak usah dipaksa, biarkan default.
        if dpi_meta:
            img.save(path, dpi=dpi_meta)
        else:
            img.save(path)
        saved_paths.append(path)

        dt = time.time() - t0
        print(f"    -> Tersimpan: {path} ({dt:.2f}s)")

        # Ekspor SVG (opsional, kalau diaktifkan & teknik mendukung) --
        # pakai `seed` yang SAMA (kalau mode kualitas aktif, ini sudah jadi
        # seed pemenang best-of) supaya komposisi SVG sepadan dengan PNG
        # yang baru disimpan. SVG saat ini selalu monokrom (palet warna
        # PNG tidak diterapkan ke SVG) -- dinyatakan eksplisit di pesan
        # supaya tidak membingungkan kalau warnanya beda dari PNG.
        if export_svg:
            if technique in SVG_CAPABLE_KEYS:
                svg_str = render_svg_technique(technique, W, H, seed)
                svg_name = f"nirmana_{technique}_{rasio_key}_{i}_seed{seed}.svg"
                svg_path = os.path.join(output_dir, svg_name)
                with open(svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_str)
                saved_paths.append(svg_path)
                print(f"    -> SVG vektor: {svg_path} (monokrom -- presisi tak terbatas, siap Illustrator)")
            else:
                print(f"    [Info] '{TECHNIQUE_LABELS[technique]}' berbasis tekstur/noise raster -- "
                      f"ekspor SVG dilewati untuk karya ini.")

        # Kritik otomatis singkat ala art director -- dianalisis dari
        # citra FINAL (setelah recolor), supaya relevan dengan yang
        # benar-benar dilihat pengguna. sparse_ok dicek dari SPARSE_BY_DESIGN
        # supaya teknik yang memang sengaja jarang (mis. Keseimbangan
        # Asimetris) tidak salah dikritik "belum penuh".
        for poin in generate_critique(img, sparse_ok=sparse_ok):
            print(f"    [Kritik] {poin}")
        print()

        warna_meta = mode_warna if mode_warna != "palette" else palet_terpilih
        gallery_entries.append((path, TECHNIQUE_LABELS[technique],
                                 f"{label_rasio} | Warna: {warna_meta} | Seed: {seed}"))

    print(f"=== Selesai! {jumlah} karya nirmana tersimpan di folder '{output_dir}/' ===")

    if gallery_entries:
        gallery_path = os.path.join(output_dir, "galeri.html")
        build_html_gallery(gallery_entries, gallery_path,
                            title="Python Nirmana Generator -- Hasil Batch")
        print(f"[Info] Galeri HTML dibuat: {gallery_path} (buka di browser untuk lihat semua sekaligus)")
        saved_paths.append(gallery_path)

    return saved_paths


def build_arg_parser() -> argparse.ArgumentParser:
    """Mode CLI non-interaktif -- untuk automasi/skrip/batch job (mis. CI,
    cron, dipanggil dari tool lain) tanpa perlu menjawab prompt satu-satu.
    Kalau tidak ada flag teknik/preset yang diberikan, program otomatis
    jatuh ke mode interaktif seperti biasa (kompatibel penuh ke belakang)."""
    valid_techniques = list(TECHNIQUE_LABELS.keys()) + ["acak"]
    p = argparse.ArgumentParser(
        prog="nirmana",
        description="Python Nirmana Generator -- Sistem DKV Otentik. "
                     "Jalankan tanpa argumen untuk mode interaktif (tanya-jawab), "
                     "atau pakai --technique/--preset untuk mode skrip/automasi.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Contoh:\n"
               "  python main.py                                  # mode interaktif\n"
               "  python main.py --technique hierarki_konsentris --count 5 --svg\n"
               "  python main.py --preset 3 --count 10 --ratio 5\n"
               "  python main.py --technique acak --count 8 --quality 3\n"
               "  python main.py --list-techniques\n",
    )
    p.add_argument("--technique", choices=valid_techniques, metavar="TEKNIK",
                    help="Kunci teknik (lihat --list-techniques). 'acak' = shuffle-bag semua teknik.")
    p.add_argument("--preset", metavar="KEY",
                    help="Kunci preset kurasi (lihat --list-presets), dipakai sebagai ganti --technique.")
    p.add_argument("--ratio", default="1", metavar="KEY",
                    help="Kunci rasio/resolusi (lihat --list-ratios). Default: 1 (1:1 Instagram).")
    p.add_argument("--count", type=int, default=3, metavar="N",
                    help="Jumlah karya unik yang di-generate. Default: 3.")
    p.add_argument("--palette", default=None, metavar="NAMA",
                    help="Nama palet kurasi (lihat --list-palettes). Default: hitam-putih.")
    p.add_argument("--random-color", action="store_true",
                    help="Satu kombinasi warna acak (harmonis) dipakai untuk semua karya dalam batch.")
    p.add_argument("--random-color-each", action="store_true",
                    help="Kombinasi warna acak BERBEDA untuk tiap karya.")
    p.add_argument("--quality", type=int, default=1, metavar="N",
                    help="Mode kualitas: render N kandidat per karya, pilih otomatis skor terbaik. Default: 1 (nonaktif).")
    p.add_argument("--svg", action="store_true",
                    help="Ekspor juga sebagai SVG vektor (untuk teknik yang mendukung, lihat --list-techniques).")
    p.add_argument("--output-dir", default="outputs", metavar="DIR",
                    help="Folder tujuan hasil render. Default: outputs/")
    p.add_argument("--list-techniques", action="store_true", help="Tampilkan semua kunci teknik lalu keluar.")
    p.add_argument("--list-ratios", action="store_true", help="Tampilkan semua kunci rasio/resolusi lalu keluar.")
    p.add_argument("--list-palettes", action="store_true", help="Tampilkan semua kunci palet warna lalu keluar.")
    p.add_argument("--list-presets", action="store_true", help="Tampilkan semua kunci preset kurasi lalu keluar.")
    return p


def run_cli(args: argparse.Namespace) -> None:
    """Jalur non-interaktif: semua parameter datang dari argparse, tidak
    ada input() sama sekali -- aman dipanggil dari skrip/CI/cron."""
    if args.ratio not in ASPECT_RATIOS:
        print(f"[Error] Kunci rasio '{args.ratio}' tidak dikenali. Lihat --list-ratios.")
        sys.exit(1)
    label_rasio, (W, H), dpi_meta = ASPECT_RATIOS[args.ratio]

    mode_warna = "hitam_putih"
    palet_terpilih = "hitam_putih"
    warna_acak_tetap = None

    if args.preset:
        if args.preset not in CURATED_PRESETS:
            print(f"[Error] Kunci preset '{args.preset}' tidak dikenali. Lihat --list-presets.")
            sys.exit(1)
        preset = CURATED_PRESETS[args.preset]
        teknik_terpilih = preset.technique
        if preset.palette_mode == "hitam_putih":
            mode_warna = "hitam_putih"
        elif preset.palette_mode == "palette":
            mode_warna, palet_terpilih = "palette", preset.palette_name
        elif preset.palette_mode == "acak_harmonis":
            mode_warna = "acak_tiap"
    elif args.technique:
        teknik_terpilih = args.technique
        if args.random_color_each:
            mode_warna = "acak_tiap"
        elif args.random_color:
            mode_warna = "acak_satu"
            warna_acak_tetap = generate_random_palette(seed=random.randint(0, 10 ** 9))
            print(f"[Info] Warna acak terpilih: dark={warna_acak_tetap[0]}  light={warna_acak_tetap[1]}")
        elif args.palette:
            if args.palette not in PALETTES:
                print(f"[Error] Nama palet '{args.palette}' tidak dikenali. Lihat --list-palettes.")
                sys.exit(1)
            mode_warna, palet_terpilih = "palette", args.palette
    else:
        print("[Error] Mode CLI butuh --technique atau --preset. Lihat --help, "
              "atau jalankan tanpa argumen untuk mode interaktif.")
        sys.exit(1)

    run_pipeline(args.ratio, W, H, dpi_meta, label_rasio, teknik_terpilih,
                 mode_warna, palet_terpilih, warna_acak_tetap,
                 max(1, args.count), max(1, args.quality), args.svg,
                 output_dir=args.output_dir)


def pilih(prompt: str, mapping: dict, default_key: str) -> str:
    print(prompt)
    for k, v in mapping.items():
        label = v[0] if isinstance(v, tuple) else v
        print(f"  {k}. {label}")
    pilihan = input(f"Masukkan pilihan [Default: {default_key}]: ").strip()
    return pilihan if pilihan in mapping else default_key


def main():
    args = build_arg_parser().parse_args()

    if args.list_techniques:
        print("Kunci teknik yang tersedia (--technique):")
        for k, v in TECHNIQUE_LABELS.items():
            print(f"  {k:<24} {v}")
        print(f"  {'acak':<24} Shuffle-bag semua teknik dasar (tidak berulang sampai semua terpakai)")
        return
    if args.list_ratios:
        print("Kunci rasio/resolusi yang tersedia (--ratio):")
        for k, (label, (w, h), dpi) in ASPECT_RATIOS.items():
            dpi_info = f", {dpi[0]} DPI" if dpi else ""
            print(f"  {k:<4} {label} ({w}x{h}px{dpi_info})")
        return
    if args.list_palettes:
        print("Nama palet yang tersedia (--palette):")
        for k in PALETTES:
            print(f"  {k}")
        return
    if args.list_presets:
        print("Kunci preset kurasi yang tersedia (--preset):")
        for k, p in CURATED_PRESETS.items():
            print(f"  {k:<4} {p.label} -- {p.description}")
        return

    if args.technique or args.preset:
        run_cli(args)
        return

    # --- Tidak ada flag teknik/preset -> mode interaktif (tanya-jawab) ---
    print("=" * 60)
    print("   PYTHON NIRMANA GENERATOR -- SISTEM DKV OTENTIK")
    print("=" * 60)

    # 1. Rasio & Resolusi
    rasio_key = pilih("\nPilih Rasio & Resolusi:", ASPECT_RATIOS, "1")
    label_rasio, (W, H), dpi_meta = ASPECT_RATIOS[rasio_key]

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

    # 3. Jumlah karya
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
        n_candidates = 1

    # 5. Ekspor SVG (opsional) -- hanya relevan untuk teknik berbasis
    #    garis/bentuk geometris murni (lihat SVG_CAPABLE_KEYS di registry.py).
    #    Ditanya sekali di awal; kalau teknik yang di-render suatu karya
    #    tidak mendukung SVG (mis. teknik acak jatuh ke teknik tekstur
    #    raster), file .svg untuk karya itu otomatis dilewati dengan info.
    export_svg = False
    svg_relevant = (teknik_terpilih == "acak" or teknik_terpilih in SVG_CAPABLE_KEYS)
    if svg_relevant:
        svg_input = input(
            "\nEkspor juga sebagai SVG (vektor, presisi tak terbatas, siap "
            "Illustrator/cutting plotter)? [y/N]: "
        ).strip().lower()
        export_svg = svg_input in ("y", "yes", "ya")

    run_pipeline(rasio_key, W, H, dpi_meta, label_rasio, teknik_terpilih,
                 mode_warna, palet_terpilih, warna_acak_tetap, jumlah,
                 n_candidates, export_svg)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Terjadi wajar kalau output dipipe ke `head`/`less` lalu ditutup
        # duluan (mis. `python main.py --list-techniques | head`) -- bukan
        # error sungguhan, jangan tampilkan traceback yang menakutkan.
        sys.stderr.close()
    except KeyboardInterrupt:
        print("\n[Dibatalkan]")
        sys.exit(130)
