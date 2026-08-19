"""
geometric_patterns.py
======================
Tiga teknik Nirmana Geometrik klasik DKV (lihat foto 3, kolom "GEOMETRIK"):

1. isometric_cubes     -> tessellasi kubus isometrik (ilusi 3D dari 3 belah
                           ketupat per kubus, gelap/sedang/terang).
2. spiral_checkerboard -> papan catur yang diremap ke koordinat polar
                           (radius + sudut) sehingga membentuk ilusi spiral.
3. distorted_grid       -> grid/graticule yang didistorsi memakai WarpField
                           yang sama dengan Nirmana Garis, menghasilkan
                           grid organik-geometrik seperti pada referensi.
"""

import math
import random
import numpy as np
from PIL import Image, ImageDraw

from .flowfield import WarpField
from .precision import draw_precise_polygon_outline, circle_points


class GeometricNirmanaGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # 1. ISOMETRIC CUBE TESSELLATION
    # ------------------------------------------------------------------
    def generate_isometric_cubes(self, cube_size: int = None, supersample: int = 2,
                                  tri_tone: bool = True) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("RGB", (W, H), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        s = (cube_size or self.rng.randint(60, 100)) * ss
        # Vektor arah 3 sisi belah ketupat (top, left, right) berbasis 120 derajat
        dx = s * math.sqrt(3) / 2
        dy = s / 2

        dark = (25, 25, 25)
        mid = (135, 135, 135)
        light = (235, 235, 235)
        if not tri_tone:
            dark, mid, light = (0, 0, 0), (255, 255, 255), (0, 0, 0)

        cols = int(W / (dx * 2)) + 4
        rows = int(H / (s * 1.5)) + 4
        row_height = s * 1.5
        col_width = dx * 2

        for row in range(-2, rows):
            for col in range(-2, cols):
                offset_x = dx if (row % 2) else 0
                cx = col * col_width + offset_x
                cy = row * row_height

                top = [(cx, cy - s), (cx + dx, cy - dy), (cx, cy), (cx - dx, cy - dy)]
                left = [(cx - dx, cy - dy), (cx, cy), (cx, cy + s), (cx - dx, cy + dy)]
                right = [(cx + dx, cy - dy), (cx, cy), (cx, cy + s), (cx + dx, cy + dy)]

                draw.polygon(top, fill=light)
                draw.polygon(left, fill=mid)
                draw.polygon(right, fill=dark)
                # Outline presisi: draw.polygon(outline=..) bawaan Pillow tidak
                # menutup celah di tiap simpul saat width > 1 -- di sini setiap
                # simpul rusuk kubus ditambal dab supaya sambungan selalu rapat.
                ow = max(1, ss)
                draw_precise_polygon_outline(draw, top, (0, 0, 0), ow)
                draw_precise_polygon_outline(draw, left, (0, 0, 0), ow)
                draw_precise_polygon_outline(draw, right, (0, 0, 0), ow)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ------------------------------------------------------------------
    # 2. SPIRAL CHECKERBOARD (ilusi optik polar remap)
    # ------------------------------------------------------------------
    def generate_spiral_checkerboard(self, rings: int = None, sectors: int = None,
                                      spiral_amount: float = None,
                                      supersample: int = 2) -> Image.Image:
        # Supersample + edge anti-alias: tepi ring/sektor dihitung sebagai
        # implicit function pada resolusi tinggi lalu di-downsample dengan
        # filter Lanczos, supaya batas polar tetap tajam & presisi (bukan
        # bergerigi/aliased) walau dicetak besar.
        ss = max(1, supersample)
        W, H = self.w * ss, self.h * ss
        cx, cy = W / 2, H / 2

        xs = np.arange(W, dtype=np.float64)
        ys = np.arange(H, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys)
        dx = X - cx
        dy = Y - cy
        r = np.sqrt(dx * dx + dy * dy)
        theta = np.arctan2(dy, dx)

        n_rings = rings or self.rng.randint(10, 16)
        n_sectors = sectors or self.rng.choice([20, 24, 28, 32])
        spiral = spiral_amount if spiral_amount is not None else self.rng.uniform(0.8, 1.8)

        max_r = math.hypot(W, H) / 2
        # Skala radial non-linear (sqrt) supaya lebar cincin terlihat konsisten
        # secara visual (area sama), khas papan-catur polar yang enak dipandang.
        r_norm = np.sqrt(r / max_r)

        ring_index = np.floor(r_norm * n_rings)
        sector_index = np.floor(((theta + math.pi) / (2 * math.pi) + (r_norm * spiral)) * n_sectors)

        checker = (ring_index + sector_index) % 2
        gray = np.where(checker > 0.5, 255, 0).astype(np.uint8)

        img = Image.fromarray(gray, mode="L").convert("RGB")
        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ------------------------------------------------------------------
    # 3. DISTORTED GRID (grid geometrik yang di-warp organik)
    # ------------------------------------------------------------------
    def generate_distorted_grid(self, cell_size: int = None, supersample: int = 2,
                                 line_mode: bool = None) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss

        field = WarpField(W, H, seed=self.seed)
        field.randomize_anchors(n_min=2, n_max=4,
                                 strength_range=(0.9, 2.0))

        xs = np.arange(W, dtype=np.float64)
        ys = np.arange(H, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys)
        Xw, Yw = field.apply(X, Y)

        cell = (cell_size or self.rng.randint(46, 72)) * ss

        line_mode = self.rng.choice([True, False]) if line_mode is None else line_mode

        if line_mode:
            # Mode garis grid tipis (graticule) -- pakai jarak-ke-garis-terdekat
            gx = np.abs(((Xw + cell / 2) % cell) - cell / 2)
            gy = np.abs(((Yw + cell / 2) % cell) - cell / 2)
            line_w = cell * 0.045
            mask = (gx < line_w) | (gy < line_w)
            gray = np.where(mask, 0, 255).astype(np.uint8)
        else:
            # Mode checkerboard terdistorsi (kotak hitam-putih yang di-warp)
            cxk = np.floor(Xw / cell).astype(np.int64)
            cyk = np.floor(Yw / cell).astype(np.int64)
            checker = (cxk + cyk) % 2
            gray = np.where(checker == 0, 255, 0).astype(np.uint8)

        img = Image.fromarray(gray, mode="L").convert("RGB")
        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img
