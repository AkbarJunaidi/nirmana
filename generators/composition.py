"""
composition.py
================
Menggabungkan beberapa teknik nirmana jadi SATU karya komposit, dua mode:

1. StudyBoard (grid_board)
   Papan studi perbandingan teknik -- persis pola tugas nirmana asli
   (lihat referensi foto 3: grid berlabel "ORGANIK" vs "GEOMETRIK" berisi
   beberapa swatch teknik berdampingan). Berguna untuk tugas kuliah yang
   memang meminta perbandingan/eksplorasi beberapa teknik sekaligus.

2. VoronoiMosaic (organic_mosaic)
   Kanvas dipartisi jadi beberapa region organik (Voronoi cells dari
   titik-titik acak), tiap region diisi teknik nirmana berbeda, lalu
   disatukan jadi satu komposisi tunggal yang koheren -- mendekati
   kompleksitas nirmana tekstur kaya (banyak motif berdampingan dalam
   satu bidang, seperti pada referensi batik/motif kaya).
"""

import math
import random
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .line_nirmana import LineNirmanaGenerator
from .organic_patterns import OrganicNirmanaGenerator
from .geometric_patterns import GeometricNirmanaGenerator

TECHNIQUE_LABELS = {
    "garis": "Nirmana Garis",
    "organik_burst": "Organik - Hatching Burst",
    "organik_cells": "Organik - Concentric Cells",
    "organik_branching": "Organik - DLA Branching",
    "geometrik_kubus": "Geometrik - Isometric Cubes",
    "geometrik_spiral": "Geometrik - Spiral Checkerboard",
    "geometrik_grid": "Geometrik - Distorted Grid",
}

ORGANIC_SET = ["organik_burst", "organik_cells", "organik_branching"]
GEOMETRIC_SET = ["geometrik_kubus", "geometrik_spiral", "geometrik_grid"]
ALL_TECHNIQUES = ["garis"] + ORGANIC_SET + GEOMETRIC_SET


def render_technique_swatch(technique: str, w: int, h: int, seed: int) -> Image.Image:
    """Fungsi bersama untuk merender satu teknik pada ukuran & seed tertentu.
    Dipakai baik oleh StudyBoard maupun VoronoiMosaic agar konsisten."""
    if technique == "garis":
        gen = LineNirmanaGenerator(w, h, seed=seed)
        band_count = random.Random(seed).randint(14, 26)
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

    raise ValueError(f"Teknik tidak dikenali: {technique}")


# ==============================================================
# MODE A: STUDY BOARD (grid perbandingan berlabel)
# ==============================================================
class StudyBoard:
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    def generate(self, rows: int = 3, cols: int = 2,
                 techniques: Optional[List[str]] = None,
                 show_labels: bool = True,
                 column_headers: Optional[Tuple[str, str]] = None) -> Image.Image:
        """Membuat papan grid rows x cols, tiap sel = satu teknik.
        Default: kolom kiri = organik, kolom kanan = geometrik (meniru
        struktur referensi foto 3 persis)."""
        board = Image.new("RGB", (self.w, self.h), (18, 18, 18))
        draw = ImageDraw.Draw(board)

        margin = int(min(self.w, self.h) * 0.035)
        header_h = int(self.h * 0.05) if column_headers else 0
        gutter = int(min(self.w, self.h) * 0.018)

        grid_top = margin + header_h
        grid_w = self.w - margin * 2
        grid_h = self.h - grid_top - margin

        cell_w = (grid_w - gutter * (cols - 1)) // cols
        cell_h = (grid_h - gutter * (rows - 1)) // rows

        if techniques is None:
            # Default persis referensi: kolom 0 = organik, kolom 1 = geometrik
            techniques = []
            for r in range(rows):
                row_pair = []
                for c in range(cols):
                    pool = ORGANIC_SET if c % 2 == 0 else GEOMETRIC_SET
                    row_pair.append(self.rng.choice(pool))
                techniques.append(row_pair)

        try:
            font = ImageFont.load_default(size=int(self.h * 0.022))
        except TypeError:
            font = ImageFont.load_default()

        if column_headers:
            for c in range(cols):
                x0 = margin + c * (cell_w + gutter)
                text = column_headers[c % len(column_headers)]
                draw.text((x0 + cell_w / 2, margin / 2), text, fill=(255, 255, 255),
                          font=font, anchor="mm")

        for r in range(rows):
            for c in range(cols):
                technique = techniques[r][c]
                x0 = margin + c * (cell_w + gutter)
                y0 = grid_top + r * (cell_h + gutter)

                sub_seed = self.seed + (r * cols + c) * 5417
                swatch = render_technique_swatch(technique, cell_w, cell_h, sub_seed)
                board.paste(swatch, (x0, y0))

                draw.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1],
                                outline=(255, 255, 255), width=max(1, int(self.h * 0.0015)))

                if show_labels:
                    label = TECHNIQUE_LABELS[technique]
                    pad = int(cell_h * 0.02)
                    text_box_h = int(cell_h * 0.07)
                    draw.rectangle([x0, y0 + cell_h - text_box_h, x0 + cell_w, y0 + cell_h],
                                    fill=(0, 0, 0))
                    draw.text((x0 + pad, y0 + cell_h - text_box_h / 2), label,
                               fill=(255, 255, 255), font=font, anchor="lm")

        return board


# ==============================================================
# MODE B: VORONOI MOSAIC (satu komposisi menyatu, region organik)
# ==============================================================
class VoronoiMosaic:
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    def generate(self, n_cells: int = None, techniques_pool: Optional[List[str]] = None,
                 border_width: int = None, max_work_dim: int = 1400) -> Image.Image:
        n_cells = n_cells or self.rng.randint(4, 7)
        pool = techniques_pool or ALL_TECHNIQUES

        # Untuk kanvas besar (mis. cetak A4/4K), render tiap layer di resolusi
        # kerja yang dibatasi lalu di-upscale -- supersample per teknik sudah
        # menambah detail, jadi hasil tetap tajam tanpa membengkakkan memori
        # (7 layer full-res A4 sekaligus bisa >2GB dan mematikan proses).
        scale = min(1.0, max_work_dim / max(self.w, self.h))
        ww, wh = max(1, int(self.w * scale)), max(1, int(self.h * scale))

        # 1. Titik-titik pusat region Voronoi (dihitung di resolusi kerja)
        points = self._poisson_like_points_wh(n_cells, ww, wh)

        # 2. Assignment region per pixel via jarak terdekat (Voronoi murni)
        xs = np.arange(ww, dtype=np.float64)
        ys = np.arange(wh, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys)

        dists = np.stack([
            (X - px) ** 2 + (Y - py) ** 2 for px, py in points
        ], axis=0)
        region_id = np.argmin(dists, axis=0)  # (H, W) index array 0..n_cells-1

        # 3. Assign teknik per region, hindari teknik yang sama berturutan
        assigned = []
        last = None
        for i in range(len(points)):
            choices = [t for t in pool if t != last] or pool
            technique = self.rng.choice(choices)
            assigned.append(technique)
            last = technique

        # 4. Render tiap teknik di resolusi kerja, komposit sesuai region_id
        canvas = np.zeros((wh, ww, 3), dtype=np.uint8)
        for i, technique in enumerate(assigned):
            sub_seed = self.seed + i * 6221
            layer = render_technique_swatch(technique, ww, wh, sub_seed)
            layer_arr = np.asarray(layer.convert("RGB"))
            mask = region_id == i
            canvas[mask] = layer_arr[mask]

        img = Image.fromarray(canvas, mode="RGB")

        # 5. Garis pembatas tipis antar-region (biar terasa "dipotong" rapi,
        #    bukan seolah bertabrakan mentah)
        bw = border_width or max(1, int(min(ww, wh) * 0.0025))
        if bw > 0:
            edge = self._region_edge_mask(region_id)
            arr = np.asarray(img).copy()
            arr[edge] = (250, 250, 250)
            img = Image.fromarray(arr, mode="RGB")

        if scale < 1.0:
            img = img.resize((self.w, self.h), Image.LANCZOS)

        return img

    def _poisson_like_points_wh(self, n: int, ww: int, wh: int) -> List[Tuple[float, float]]:
        pts = []
        attempts = 0
        min_dist = min(ww, wh) * (0.65 / math.sqrt(max(n, 1)))
        while len(pts) < n and attempts < n * 60:
            attempts += 1
            x = self.rng.uniform(ww * 0.08, ww * 0.92)
            y = self.rng.uniform(wh * 0.08, wh * 0.92)
            if all(math.hypot(x - px, y - py) > min_dist for px, py in pts):
                pts.append((x, y))
        while len(pts) < n:
            pts.append((self.rng.uniform(0, ww), self.rng.uniform(0, wh)))
        return pts

    @staticmethod
    def _region_edge_mask(region_id: np.ndarray) -> np.ndarray:
        """Deteksi tepi antar-region (pixel yang tetangganya beda region_id)."""
        edge = np.zeros_like(region_id, dtype=bool)
        edge[:, 1:] |= region_id[:, 1:] != region_id[:, :-1]
        edge[:, :-1] |= region_id[:, 1:] != region_id[:, :-1]
        edge[1:, :] |= region_id[1:, :] != region_id[:-1, :]
        edge[:-1, :] |= region_id[1:, :] != region_id[:-1, :]
        return edge
