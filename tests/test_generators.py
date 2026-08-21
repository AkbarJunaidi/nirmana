"""
test_generators.py
====================
Test suite pytest. Fokus: smoke test (semua teknik harus render tanpa
error pada ukuran kecil, cepat) + beberapa unit test untuk komponen
kritis (anti-patahan, evaluator kualitas, sistem warna).

Jalankan: pytest tests/ -v
"""

import math
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generators.registry import (
    render_base_technique, ALL_BASE_KEYS, SVG_CAPABLE_KEYS,
    render_svg_technique, SPARSE_BY_DESIGN,
)
from generators.composition import VoronoiMosaic
from generators.precision import draw_precise_polyline, circle_points
from generators.quality import generate_critique, _score_image
from generators.palette import (
    recolor_duotone, generate_random_palette, is_valid_hex, PALETTES,
)

SMOKE_SIZE = 220  # kecil & cepat -- smoke test cuma perlu pastikan tidak crash


# ----------------------------------------------------------------------
# Smoke test: semua teknik dasar harus render tanpa error
# ----------------------------------------------------------------------
@pytest.mark.parametrize("technique", ALL_BASE_KEYS)
def test_base_technique_renders(technique):
    img = render_base_technique(technique, SMOKE_SIZE, SMOKE_SIZE, seed=42)
    assert isinstance(img, Image.Image)
    assert img.size == (SMOKE_SIZE, SMOKE_SIZE)


@pytest.mark.parametrize("technique", ALL_BASE_KEYS)
def test_base_technique_deterministic(technique):
    """Seed yang sama HARUS menghasilkan citra identik -- properti penting
    untuk reproduksibilitas (mis. mode kualitas best-of-N mengandalkan ini
    untuk menyimpan ulang kandidat pemenang)."""
    img1 = render_base_technique(technique, 120, 120, seed=7)
    img2 = render_base_technique(technique, 120, 120, seed=7)
    assert img1.tobytes() == img2.tobytes()


def test_voronoi_mosaic_renders():
    img = VoronoiMosaic(SMOKE_SIZE, SMOKE_SIZE, seed=1).generate()
    assert isinstance(img, Image.Image)


def test_voronoi_mosaic_non_square():
    """Rasio non-persegi (mis. story 9:16) sempat jadi sumber bug -- pastikan
    tidak crash & tidak distorsi ekstrem."""
    img = VoronoiMosaic(180, 320, seed=1).generate()
    assert img.size == (180, 320)


# ----------------------------------------------------------------------
# SVG: semua teknik SVG-capable harus menghasilkan markup valid
# ----------------------------------------------------------------------
@pytest.mark.parametrize("technique", sorted(SVG_CAPABLE_KEYS))
def test_svg_technique_renders(technique):
    svg = render_svg_technique(technique, 400, 400, seed=11)
    assert svg.startswith("<?xml")
    assert "<svg" in svg and "</svg>" in svg


def test_svg_rejects_unsupported_technique():
    with pytest.raises(ValueError):
        render_svg_technique("organik_branching", 200, 200, seed=1)  # teknik raster, bukan vektor


# ----------------------------------------------------------------------
# precision.py -- jaminan anti-patahan
# ----------------------------------------------------------------------
def test_circle_points_closes_exactly():
    pts = circle_points(50, 50, 30)
    assert pts[0] == pts[-1], "Loop lingkaran harus menutup persis (tanpa jahitan)"


def test_circle_points_adaptive_density():
    pts_small = circle_points(0, 0, 5)
    pts_large = circle_points(0, 0, 500)
    assert len(pts_large) > len(pts_small), "Lingkaran besar butuh lebih banyak sampel"


def test_draw_precise_polyline_no_crash_on_sharp_angle():
    img = Image.new("RGB", (100, 100), (255, 255, 255))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    # Sudut sangat tajam (lipat balik) -- kasus paling rawan bercelah
    pts = [(10, 10), (90, 50), (10, 90)]
    draw_precise_polyline(draw, pts, (0, 0, 0), width=12)  # tidak boleh raise


# ----------------------------------------------------------------------
# quality.py -- evaluator kualitas & kritik otomatis
# ----------------------------------------------------------------------
def test_critique_returns_nonempty_list():
    img = render_base_technique("value_grid", 200, 200, seed=5)
    critique = generate_critique(img)
    assert isinstance(critique, list) and len(critique) > 0
    assert all(isinstance(p, str) for p in critique)


def test_critique_sparse_ok_softens_blank_warning():
    """Teknik SPARSE_BY_DESIGN tidak boleh dikritik 'belum penuh' terlalu
    agresif dibanding kalau dianalisis tanpa sparse_ok."""
    img = render_base_technique("keseimbangan_asimetris", 300, 300, seed=9)
    info_strict = _score_image(img, sparse_ok=False)
    info_relaxed = _score_image(img, sparse_ok=True)
    assert info_relaxed["blank_threshold"] >= info_strict["blank_threshold"]


def test_score_image_handles_blank_canvas():
    """Kanvas kosong total tidak boleh membuat evaluator crash (division
    by zero dkk)."""
    img = Image.new("RGB", (100, 100), (255, 255, 255))
    info = _score_image(img)
    assert 0 <= info["total"] <= 100


def test_score_image_handles_dark_background():
    """Evaluator harus generik untuk latar GELAP juga (mis. organik_branching
    berlatar hitam) -- bukan mengasumsikan latar selalu putih."""
    img = render_base_technique("organik_branching", 200, 200, seed=3)
    info = _score_image(img)
    assert info["bg_value"] < 0.3, "Latar dominan organik_branching seharusnya gelap"


# ----------------------------------------------------------------------
# palette.py -- sistem warna
# ----------------------------------------------------------------------
def test_recolor_duotone_preserves_size():
    img = render_base_technique("garis", 150, 150, seed=1)
    recolored = recolor_duotone(img, list(PALETTES.keys())[0])
    assert recolored.size == img.size


def test_generate_random_palette_valid_hex():
    dark, light = generate_random_palette(seed=123)
    assert is_valid_hex(dark) and is_valid_hex(light)


def test_is_valid_hex():
    assert is_valid_hex("#1A1A2E")
    assert is_valid_hex("1A1A2E")
    assert not is_valid_hex("bukan-hex")
    assert not is_valid_hex("#GGG")


# ----------------------------------------------------------------------
# Registry -- konsistensi metadata
# ----------------------------------------------------------------------
def test_all_base_keys_unique():
    assert len(ALL_BASE_KEYS) == len(set(ALL_BASE_KEYS)), "Ada kunci teknik duplikat di registry"


def test_sparse_by_design_is_subset_of_all_keys():
    assert SPARSE_BY_DESIGN.issubset(set(ALL_BASE_KEYS))


def test_svg_capable_is_subset_of_all_keys():
    assert SVG_CAPABLE_KEYS.issubset(set(ALL_BASE_KEYS))
