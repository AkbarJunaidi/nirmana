"""
depth_illusion.py
===================
Tiga teknik nirmana "berkesan spektakuler" yang mengeksploitasi prinsip
Gestalt untuk membangun ILUSI KEDALAMAN (depth) di bidang datar -- terinspirasi
studi "Gestalt principles - depth" (proximity, closure, continuity, common
fate, pragnanz): garis-garis yang menciut ke satu titik menipu mata jadi
melihat ruang 3D, retakan yang membentuk bidang tertutup menipu mata jadi
melihat pecahan kaca, dsb.

1. perspective_tunnel  -> grid memusat ke vanishing point (Gestalt: common
                           fate & continuity) -- efek lorong/terowongan.
2. shatter_web          -> retakan radial + cincin dari titik tumbukan,
                           sebagian sel di-flood-fill hitam (Gestalt:
                           closure -- otak "menutup" bidang jadi solid).
3. spiral_hatch_burst   -> guratan tinta pendek mengikuti medan spiral,
                           rapat di pusat, renggang di tepi (Gestalt:
                           similarity & pragnanz -- pengulangan elemen
                           serupa terbaca sebagai satu bentuk pusaran).
"""

import math
import random
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw

from .precision import draw_precise_polyline, draw_precise_polygon_outline, circle_points


class DepthIllusionGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # 1. PERSPECTIVE TUNNEL (vanishing point grid)
    # ------------------------------------------------------------------
    def generate_perspective_tunnel(self, n_frames: int = 26, n_spokes: int = None,
                                     vp: Tuple[float, float] = None,
                                     supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        vpx, vpy = vp or (W * self.rng.uniform(0.42, 0.58), H * self.rng.uniform(0.38, 0.55))
        n_spokes = n_spokes or self.rng.choice([16, 20, 24])

        # Frame terluar: persegi penuh kanvas (dengan sedikit margin)
        half_w0, half_h0 = W * 0.62, H * 0.62

        # --- Radiating spokes (garis dari VP ke tepi frame terluar) ---
        corners_outer = [
            (vpx - half_w0, vpy - half_h0), (vpx + half_w0, vpy - half_h0),
            (vpx + half_w0, vpy + half_h0), (vpx - half_w0, vpy + half_h0),
        ]
        for i in range(n_spokes):
            t = i / n_spokes
            # titik di sekeliling frame terluar (interpolasi antar sudut)
            edge_pt = self._point_on_rect_perimeter(corners_outer, t)
            draw.line([(vpx, vpy), edge_pt], fill=0, width=max(1, ss))

        # --- Concentric frames (nonlinear spacing agar terasa menciut cepat
        #     mendekati VP, khas ilusi perspektif) ---
        growth = self.rng.uniform(0.78, 0.85)
        scale = 1.0
        frame_pts = []
        for f in range(n_frames):
            hw, hh = half_w0 * scale, half_h0 * scale
            rect = [(vpx - hw, vpy - hh), (vpx + hw, vpy - hh),
                    (vpx + hw, vpy + hh), (vpx - hw, vpy + hh)]
            frame_pts.append(rect)
            scale *= growth

        for rect in frame_pts:
            draw_precise_polygon_outline(draw, rect, 0, max(1, ss))

        # --- Isi band antar-frame berselang-seling dengan pola berbeda
        #     supaya terasa gradasi cahaya seperti lorong (dekat VP lebih
        #     gelap/padat, jauh dari VP lebih terang/jarang) ---
        for idx in range(len(frame_pts) - 1):
            outer = frame_pts[idx]
            inner = frame_pts[idx + 1]
            depth_t = idx / len(frame_pts)  # 0 = terluar, 1 = dekat VP

            mode = self.rng.choice(["dot", "hatch", "solid", "none"]) if idx % 3 == 0 else "none"
            if mode == "dot":
                self._fill_band_dots(draw, outer, inner, density=0.15 + depth_t * 0.5, ss=ss)
            elif mode == "hatch":
                self._fill_band_hatch(draw, outer, inner, vpx, vpy, spacing=max(4, int(14 * ss * (1 - depth_t))))
            elif mode == "solid" and self.rng.random() < 0.3:
                draw.polygon(outer, fill=0)
                draw.polygon(inner, fill=255)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    @staticmethod
    def _point_on_rect_perimeter(corners, t):
        """t in [0,1) -> titik di sekeliling persegi (4 sisi) secara merata."""
        n = len(corners)
        seg = t * n
        i = int(seg) % n
        frac = seg - int(seg)
        x0, y0 = corners[i]
        x1, y1 = corners[(i + 1) % n]
        return (x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac)

    def _fill_band_dots(self, draw, outer, inner, density, ss):
        (ox0, oy0), (ox1, _), (_, oy2), _ = outer
        n_dots = int(60 * density)
        r = max(1, int(1.3 * ss))
        for _ in range(n_dots):
            px = self.rng.uniform(ox0, ox1)
            py = self.rng.uniform(oy0, oy2)
            if self._point_in_quad((px, py), outer) and not self._point_in_quad((px, py), inner):
                draw.ellipse([px - r, py - r, px + r, py + r], fill=0)

    def _fill_band_hatch(self, draw, outer, inner, vpx, vpy, spacing):
        (ox0, oy0), (ox1, _), (_, oy2), _ = outer
        y = oy0
        while y < oy2:
            pts = [(x, y) for x in range(int(ox0), int(ox1), spacing)]
            for (px, py) in pts:
                if self._point_in_quad((px, py), outer) and not self._point_in_quad((px, py), inner):
                    draw.line([(px, py), (px + spacing * 0.6, py)], fill=0, width=max(1, spacing // 6))
            y += spacing

    @staticmethod
    def _point_in_quad(pt, quad):
        x, y = pt
        xs = [p[0] for p in quad]
        ys = [p[1] for p in quad]
        return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)

    # ------------------------------------------------------------------
    # 2. SHATTER WEB (fracture / closure illusion)
    # ------------------------------------------------------------------
    def generate_shatter_web(self, n_impacts: int = None, cracks_per_impact: int = None,
                              fill_ratio: float = 0.42, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("RGB", (W, H), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        n_impacts = n_impacts or self.rng.randint(1, 3)
        impacts = [(self.rng.uniform(W * 0.2, W * 0.8), self.rng.uniform(H * 0.2, H * 0.8))
                   for _ in range(n_impacts)]

        line_w = max(1, int(1.8 * ss))

        for (icx, icy) in impacts:
            n_cracks = cracks_per_impact or self.rng.randint(9, 16)
            base_angle = self.rng.uniform(0, math.tau)
            crack_angles = sorted(
                (base_angle + (i / n_cracks) * math.tau + self.rng.uniform(-0.18, 0.18)) % math.tau
                for i in range(n_cracks)
            )
            max_reach = math.hypot(W, H)
            crack_endpoints = []
            for ang in crack_angles:
                reach = max_reach * self.rng.uniform(0.55, 1.05)
                # crack jalur piecewise (sedikit jitter) biar tidak lurus sempurna
                n_seg = self.rng.randint(3, 5)
                pts = [(icx, icy)]
                for s in range(1, n_seg + 1):
                    t = s / n_seg
                    jitter_ang = ang + self.rng.uniform(-0.05, 0.05) * (1 - t)
                    r = reach * t
                    pts.append((icx + r * math.cos(jitter_ang), icy + r * math.sin(jitter_ang)))
                draw_precise_polyline(draw, pts, (15, 15, 15), line_w)
                crack_endpoints.append(pts[-1])

            # cincin retak konsentris (patah-patah, tidak menutup penuh)
            n_rings = self.rng.randint(2, 4)
            for ridx in range(1, n_rings + 1):
                ring_r = (max_reach * 0.5) * (ridx / (n_rings + 1)) * self.rng.uniform(0.5, 0.85)
                n_pts = 26
                gap_start = self.rng.uniform(0, math.tau)
                gap_size = self.rng.uniform(0.3, 0.7)
                pts = []
                for k in range(n_pts + 1):
                    a = (k / n_pts) * math.tau
                    rel = (a - gap_start) % math.tau
                    if rel < math.tau - gap_size:
                        wob = ring_r * (1 + self.rng.uniform(-0.04, 0.04))
                        pts.append((icx + wob * math.cos(a), icy + wob * math.sin(a)))
                    else:
                        if len(pts) > 1:
                            draw_precise_polyline(draw, pts, (15, 15, 15), max(1, line_w - ss // 2))
                        pts = []
                if len(pts) > 1:
                    draw_precise_polyline(draw, pts, (15, 15, 15), max(1, line_w - ss // 2))

        # Flood-fill sebagian sel yang terbentuk jadi hitam pekat (efek
        # "closure" -- mata membaca bidang tertutup sebagai solid)
        n_seeds = int(40 * fill_ratio)
        for _ in range(n_seeds):
            sx, sy = self.rng.randint(0, W - 1), self.rng.randint(0, H - 1)
            if img.getpixel((sx, sy)) == (255, 255, 255):
                try:
                    ImageDraw.floodfill(img, (sx, sy), (15, 15, 15), thresh=10)
                except Exception:
                    pass

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ------------------------------------------------------------------
    # 3. SPIRAL HATCH BURST (similarity / pragnanz)
    # ------------------------------------------------------------------
    def generate_spiral_hatch_burst(self, n_arms: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        cx, cy = W * self.rng.uniform(0.4, 0.6), H * self.rng.uniform(0.4, 0.6)
        max_r = math.hypot(W, H) * 0.56
        n_arms = n_arms or self.rng.randint(3, 5)
        swirl = self.rng.uniform(2.6, 5.0)  # total putaran (radian) dari pusat ke tepi

        n_rings = 130
        for ring in range(3, n_rings):
            t = ring / n_rings  # 0 dekat pusat, 1 di tepi
            r = max_r * (t ** 1.25)
            angle_offset = swirl * (t ** 0.8)
            tick_len = max(1.6 * ss, r * 0.085 * (1 - t * 0.35))

            # Kepadatan guratan mengikuti keliling lingkaran di radius ini,
            # supaya jarak antar-guratan konsisten (bukan makin renggang ke tepi).
            circumference = 2 * math.pi * max(r, 1.0)
            spacing = max(2.5 * ss, tick_len * 0.85)
            n_ticks = max(8, int(circumference / spacing))

            for k in range(n_ticks):
                a = (k / n_ticks) * math.tau + angle_offset
                # modulasi kepadatan per-lengan: puncak di dekat tiap "arm",
                # menciut di antaranya -- membentuk pola pusaran kipas (pinwheel)
                weight = (math.cos(n_arms * (a - angle_offset)) + 1) / 2  # 0..1
                if weight < 0.12 and self.rng.random() > 0.15:
                    continue  # celah antar-lengan, sedikit noise biar tidak steril

                a_j = a + self.rng.uniform(-0.02, 0.02)
                px, py = cx + r * math.cos(a_j), cy + r * math.sin(a_j)
                tang = a_j + math.pi / 2
                local_len = tick_len * (0.55 + 0.45 * weight)
                x0 = px - local_len / 2 * math.cos(tang)
                y0 = py - local_len / 2 * math.sin(tang)
                x1 = px + local_len / 2 * math.cos(tang)
                y1 = py + local_len / 2 * math.sin(tang)
                draw.line([(x0, y0), (x1, y1)], fill=0, width=max(1, int(ss * (1.1 if t < 0.5 else 0.8))))

        # titik pusat padat (fokus komposisi)
        core_r = max_r * 0.045
        draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=0)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")
