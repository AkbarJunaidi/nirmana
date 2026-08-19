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
}

# Pengelompokan dipakai oleh composition.py (Mosaik Voronoi butuh kumpulan
# teknik yang aman & cepat untuk dirender berkali-kali pada resolusi kerja
# yang dibatasi).
ORGANIC_KEYS = ["organik_burst", "organik_cells", "organik_branching", "lsystem", "parallax"]
GEOMETRIC_KEYS = ["geometrik_kubus", "geometrik_spiral", "geometrik_grid", "depth_tunnel", "moire", "wireframe"]
MOTIF_KEYS = ["motif_arrow", "motif_dotx", "motif_shapecross", "motif_weave"]
MISC_KEYS = ["garis", "depth_shatter", "depth_spiral", "droste", "emosi",
             "sedimen", "kekosongan", "patahan", "kontur_alir", "titik",
             "hierarki_paralel", "hierarki_konsentris", "hierarki_radial"]
# anaglyph sengaja TIDAK dimasukkan ke pool otomatis composition -- warna
# merah-cyannya adalah konten inti teknik itu sendiri, akan terlihat aneh
# kalau dipaksa berdampingan acak dengan teknik hitam-putih lain atau
# ikut ter-recolor oleh sistem palet.
ALL_BASE_KEYS = ORGANIC_KEYS + GEOMETRIC_KEYS + MOTIF_KEYS + MISC_KEYS


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

    raise ValueError(f"Teknik tidak dikenali: {technique}")
