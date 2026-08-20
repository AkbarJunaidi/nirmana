"""
composition.py
================
Menggabungkan beberapa teknik nirmana jadi SATU karya komposit lewat
VoronoiMosaic: kanvas dipartisi jadi beberapa region organik (Voronoi
cells dari titik-titik acak), tiap region diisi teknik nirmana berbeda,
lalu disatukan jadi satu komposisi tunggal yang koheren -- mendekati
kompleksitas nirmana tekstur kaya (banyak motif berdampingan dalam satu
bidang, seperti pada referensi batik/motif kaya).
"""

import math
import random
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw

from .registry import (
    render_base_technique as render_technique_swatch,
    ALL_BASE_KEYS as ALL_TECHNIQUES,
)


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

        # 4. Render tiap teknik PAS DI UKURAN SEL-NYA SENDIRI (bounding box
        #    region tersebut), baru dikomposit -- bukan me-render teknik di
        #    ukuran KANVAS PENUH lalu dipotong sesuai sel. Cara lama itu
        #    salah: banyak teknik nirmana punya komposisi yang sengaja
        #    dipusatkan (bola, ledakan radial, motif tengah) -- kalau
        #    dirender penuh-kanvas lalu dipotong ke sel yang jauh dari
        #    tengah, yang muncul cuma POTONGAN ACAK (mis. separuh bola,
        #    sepotong motif) yang terlihat berantakan & tidak proporsional.
        #    Dengan merender pas di bounding box sel, tiap teknik tetap
        #    utuh & terpusat proporsional di dalam sel masing-masing --
        #    hasilnya jauh lebih rapi dan "sengaja", bukan tabrakan acak.
        canvas = np.zeros((wh, ww, 3), dtype=np.uint8)
        min_cell_dim = max(24, int(min(ww, wh) * 0.05))
        for i, technique in enumerate(assigned):
            mask_full = region_id == i
            rows = np.any(mask_full, axis=1)
            cols = np.any(mask_full, axis=0)
            if not rows.any():
                continue
            r0, r1 = np.where(rows)[0][[0, -1]]
            c0, c1 = np.where(cols)[0][[0, -1]]
            cell_h = max(min_cell_dim, int(r1 - r0 + 1))
            cell_w = max(min_cell_dim, int(c1 - c0 + 1))

            sub_seed = self.seed + i * 6221
            layer = render_technique_swatch(technique, cell_w, cell_h, sub_seed)
            layer_arr = np.asarray(layer.convert("RGB"))
            # Tempel tepat di bounding box sel (bisa sedikit melebihi kalau
            # cell_h/cell_w dinaikkan ke minimum -- diklip supaya tetap pas)
            ph, pw = layer_arr.shape[0], layer_arr.shape[1]
            r_end = min(wh, r0 + ph)
            c_end = min(ww, c0 + pw)
            sub_mask = mask_full[r0:r_end, c0:c_end]
            canvas[r0:r_end, c0:c_end][sub_mask] = layer_arr[:r_end - r0, :c_end - c0][sub_mask]

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
