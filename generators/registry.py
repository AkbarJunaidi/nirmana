"""
registry.py
============
Satu sumber kebenaran (single source of truth) untuk semua teknik DASAR
nirmana. main.py dan composition.py (Mosaik Voronoi) memanggil fungsi yang
sama persis dari sini, jadi begitu ada teknik baru ditambahkan, semua
bagian sistem otomatis ikut punya akses tanpa perlu disalin manual.
"""

import random

from .line_nirmana import LineNirmanaGenerator
from .organic_patterns import OrganicNirmanaGenerator
from .geometric_patterns import GeometricNirmanaGenerator
from .depth_illusion import DepthIllusionGenerator
from .advanced_depth import AdvancedDepthGenerator
from .depth_explorations import DepthExplorationGenerator
from .radial_motif import RadialMotifGenerator
from .emotive import EmotiveGenerator
from .stratum import StratumGenerator
from .flow_contours import FlowContourGenerator
from .dot_nirmana import DotNirmanaGenerator
from .line_hierarchy import LineHierarchyGenerator
from .classic_nirmana import ClassicNirmanaGenerator

BASE_TECHNIQUE_LABELS = {
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
    "anaglyph": "Depth Exploration - Anaglyph Relief (Stereoskopi 3D)",
    "lsystem": "Depth Exploration - L-System Branching (Rumpun)",
    "parallax": "Depth Exploration - Parallax Silhouette",
    "motif_arrow": "Motif Radial - Arrow Burst",
    "motif_dotx": "Motif Radial - Dot Gradient X",
    "motif_shapecross": "Motif Radial - Shape Cross",
    "motif_weave": "Motif Radial - Weave Stripes",
    "emosi": "Gestur Emosional - Denyut, Sayat, Simpul (Abstrak Ekspresif)",
    "sedimen": "Kedalaman - Sedimen (Lapisan Mengendap & Tererosi)",
    "kekosongan": "Kedalaman - Kekosongan (Tegangan Penuh vs Tiada)",
    "patahan": "Kedalaman - Patahan (Diskontinuitas & Pergeseran)",
    "kontur_alir": "Nirmana Garis - Kontur Alir (Paisley/Fingerprint)",
    "titik": "Nirmana Titik (Halftone Dot Grid)",
    "hierarki_paralel": "Garis Tebal-Tipis - Keluarga Paralel (Uji Skala Ketebalan)",
    "hierarki_konsentris": "Garis Tebal-Tipis - Cincin Konsentris Presisi (Meruncing)",
    "hierarki_radial": "Garis Tebal-Tipis - Jari-jari Meruncing x Busur",
    "bidang": "Nirmana Bidang - Figure-Ground (Overlap XOR)",
    "value_grid": "Nirmana Kontras Value - Grid 9 Tingkat",
    "irama_repetisi": "Nirmana Irama - Repetitif (Interval & Ukuran Tetap)",
    "irama_progresi": "Nirmana Irama - Progresif (Gradasi Ukuran/Rotasi)",
    "irama_oposisi": "Nirmana Irama - Oposisi (Pola Ketukan Berselang)",
    "keseimbangan_asimetris": "Nirmana Keseimbangan Asimetris (Torsi Visual Terkoreksi)",
}

# Pengelompokan dipakai oleh composition.py (Mosaik Voronoi butuh kumpulan
# teknik yang aman & cepat untuk dirender berkali-kali pada resolusi kerja
# yang dibatasi).
ORGANIC_KEYS = ["organik_burst", "organik_cells", "organik_branching", "lsystem", "parallax"]
GEOMETRIC_KEYS = ["geometrik_kubus", "geometrik_spiral", "geometrik_grid", "depth_tunnel", "moire", "wireframe"]
MOTIF_KEYS = ["motif_arrow", "motif_dotx", "motif_shapecross", "motif_weave"]
MISC_KEYS = ["garis", "depth_shatter", "depth_spiral", "droste", "emosi",
             "sedimen", "kekosongan", "patahan", "kontur_alir", "titik",
             "hierarki_paralel", "hierarki_konsentris", "hierarki_radial",
             "bidang", "value_grid", "irama_repetisi", "irama_progresi",
             "irama_oposisi", "keseimbangan_asimetris"]
# anaglyph sengaja TIDAK dimasukkan ke pool otomatis composition -- warna
# merah-cyannya adalah konten inti teknik itu sendiri, akan terlihat aneh
# kalau dipaksa berdampingan acak dengan teknik hitam-putih lain atau
# ikut ter-recolor oleh sistem palet.
ALL_BASE_KEYS = ORGANIC_KEYS + GEOMETRIC_KEYS + MOTIF_KEYS + MISC_KEYS

# Teknik yang secara PRINSIP DESAIN memang sengaja jarang/berongga (ruang
# negatif luas adalah bagian dari tekniknya, bukan cacat) -- dipakai
# quality.py supaya evaluator kualitas tidak salah kritik menyebut ruang
# kosong yang disengaja sebagai "komposisi belum penuh".
SPARSE_BY_DESIGN = {
    "keseimbangan_asimetris",  # ruang negatif adalah inti prinsip desainnya
    "motif_arrow", "motif_dotx", "motif_shapecross",  # motif radial diskret
    "hierarki_radial",  # jari-jari meruncing + busur tipis
    "titik",  # grid halftone dot, area antar-titik memang kosong
}


def render_base_technique(technique: str, w: int, h: int, seed: int):
    """Merender satu teknik DASAR nirmana. Mengembalikan PIL.Image saja
    (bukan tuple) supaya gampang dipakai composition.py maupun main.py."""
    if technique == "garis":
        gen = LineNirmanaGenerator(w, h, seed=seed)
        band_count = random.Random(seed).randint(16, 30)
        return gen.generate(band_count=band_count)

    if technique == "organik_burst":
        return OrganicNirmanaGenerator(w, h, seed=seed).generate_hatching_burst()
    if technique == "organik_cells":
        return OrganicNirmanaGenerator(w, h, seed=seed).generate_concentric_cells()
    if technique == "organik_branching":
        return OrganicNirmanaGenerator(w, h, seed=seed).generate_reaction_diffusion_blob()

    if technique == "geometrik_kubus":
        return GeometricNirmanaGenerator(w, h, seed=seed).generate_isometric_cubes()
    if technique == "geometrik_spiral":
        return GeometricNirmanaGenerator(w, h, seed=seed).generate_spiral_checkerboard()
    if technique == "geometrik_grid":
        return GeometricNirmanaGenerator(w, h, seed=seed).generate_distorted_grid()

    if technique == "depth_tunnel":
        return DepthIllusionGenerator(w, h, seed=seed).generate_perspective_tunnel()
    if technique == "depth_shatter":
        return DepthIllusionGenerator(w, h, seed=seed).generate_shatter_web()
    if technique == "depth_spiral":
        return DepthIllusionGenerator(w, h, seed=seed).generate_spiral_hatch_burst()

    if technique == "moire":
        return AdvancedDepthGenerator(w, h, seed=seed).generate_moire_interference()
    if technique == "wireframe":
        return AdvancedDepthGenerator(w, h, seed=seed).generate_wireframe_mesh()
    if technique == "droste":
        rng = random.Random(seed)
        base_choice = rng.choice(["garis", "geometrik_kubus", "geometrik_spiral",
                                   "geometrik_grid", "organik_cells", "motif_arrow",
                                   "motif_shapecross"])
        base_img = render_base_technique(base_choice, w, h, seed + 999)
        gen = AdvancedDepthGenerator(w, h, seed=seed)
        return gen.generate_droste_zoom(base_image=base_img, levels=rng.randint(4, 6))

    if technique == "anaglyph":
        return DepthExplorationGenerator(w, h, seed=seed).generate_anaglyph_relief()
    if technique == "lsystem":
        return DepthExplorationGenerator(w, h, seed=seed).generate_lsystem_branching()
    if technique == "parallax":
        return DepthExplorationGenerator(w, h, seed=seed).generate_parallax_silhouette()

    if technique == "motif_arrow":
        return RadialMotifGenerator(w, h, seed=seed).generate_arrow_burst()
    if technique == "motif_dotx":
        return RadialMotifGenerator(w, h, seed=seed).generate_dot_gradient_x()
    if technique == "motif_shapecross":
        return RadialMotifGenerator(w, h, seed=seed).generate_shape_cross()
    if technique == "motif_weave":
        return RadialMotifGenerator(w, h, seed=seed).generate_weave_stripes()

    if technique == "emosi":
        return EmotiveGenerator(w, h, seed=seed).generate()

    if technique == "sedimen":
        return StratumGenerator(w, h, seed=seed).generate_sedimen()
    if technique == "kekosongan":
        return StratumGenerator(w, h, seed=seed).generate_kekosongan()
    if technique == "patahan":
        return StratumGenerator(w, h, seed=seed).generate_patahan()

    if technique == "kontur_alir":
        return FlowContourGenerator(w, h, seed=seed).generate()

    if technique == "titik":
        return DotNirmanaGenerator(w, h, seed=seed).generate()

    if technique == "hierarki_paralel":
        return LineHierarchyGenerator(w, h, seed=seed).generate_parallel_families()
    if technique == "hierarki_konsentris":
        return LineHierarchyGenerator(w, h, seed=seed).generate_concentric_taper()
    if technique == "hierarki_radial":
        return LineHierarchyGenerator(w, h, seed=seed).generate_radial_taper()

    if technique == "bidang":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_figure_ground()
    if technique == "value_grid":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_value_grid()
    if technique == "irama_repetisi":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_rhythm_repetition()
    if technique == "irama_progresi":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_rhythm_progression()
    if technique == "irama_oposisi":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_rhythm_transition()
    if technique == "keseimbangan_asimetris":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_asymmetric_balance()

    raise ValueError(f"Teknik tidak dikenali: {technique}")


# ======================================================================
# EKSPOR VEKTOR (SVG) -- hanya untuk teknik yang secara fundamental
# berbasis garis/bentuk geometris murni (lihat svg_export.py untuk
# penjelasan lengkap kenapa noise/tekstur raster TIDAK diekspor SVG).
# Tiap fungsi svg di sini memakai rng lokal fresh dari `seed` yang sama
# persis dengan versi raster, jadi seed yang sama menghasilkan komposisi
# yang sepadan (bukan pixel-identik, tapi sama secara struktural/gaya)
# antara file .png dan .svg -- pengguna bisa percaya keduanya "karya yang
# sama", cuma beda format.
# ======================================================================

SVG_TECHNIQUE_LABELS = {
    "hierarki_paralel": BASE_TECHNIQUE_LABELS["hierarki_paralel"],
    "hierarki_konsentris": BASE_TECHNIQUE_LABELS["hierarki_konsentris"],
    "hierarki_radial": BASE_TECHNIQUE_LABELS["hierarki_radial"],
    "bidang": BASE_TECHNIQUE_LABELS["bidang"],
    "value_grid": BASE_TECHNIQUE_LABELS["value_grid"],
    "irama_repetisi": BASE_TECHNIQUE_LABELS["irama_repetisi"],
    "irama_progresi": BASE_TECHNIQUE_LABELS["irama_progresi"],
    "irama_oposisi": BASE_TECHNIQUE_LABELS["irama_oposisi"],
    "keseimbangan_asimetris": BASE_TECHNIQUE_LABELS["keseimbangan_asimetris"],
}

SVG_CAPABLE_KEYS = set(SVG_TECHNIQUE_LABELS.keys())


def render_svg_technique(technique: str, w: int, h: int, seed: int) -> str:
    """Mengembalikan markup SVG (string) untuk teknik yang mendukung
    ekspor vektor. Raise ValueError kalau teknik tidak ada di
    SVG_CAPABLE_KEYS (mis. teknik berbasis noise/tekstur raster)."""
    if technique not in SVG_CAPABLE_KEYS:
        raise ValueError(f"Teknik '{technique}' tidak mendukung ekspor SVG "
                          f"(fundamentalnya raster/tekstur, bukan garis/bentuk vektor).")

    if technique == "hierarki_paralel":
        return LineHierarchyGenerator(w, h, seed=seed).generate_parallel_families_svg()
    if technique == "hierarki_konsentris":
        return LineHierarchyGenerator(w, h, seed=seed).generate_concentric_taper_svg()
    if technique == "hierarki_radial":
        return LineHierarchyGenerator(w, h, seed=seed).generate_radial_taper_svg()
    if technique == "bidang":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_figure_ground_svg()
    if technique == "value_grid":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_value_grid_svg()
    if technique == "irama_repetisi":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_rhythm_repetition_svg()
    if technique == "irama_progresi":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_rhythm_progression_svg()
    if technique == "irama_oposisi":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_rhythm_transition_svg()
    if technique == "keseimbangan_asimetris":
        return ClassicNirmanaGenerator(w, h, seed=seed).generate_asymmetric_balance_svg()

    raise ValueError(f"Teknik tidak dikenali: {technique}")
