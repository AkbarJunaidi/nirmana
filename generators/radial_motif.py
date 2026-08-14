"""
radial_motif.py
=================
Teknik "Motif Simetri Radial" -- prinsip nirmana paling klasik: repetisi +
simetri dari satu motif dasar di sekeliling pusat, mengisi seluruh bidang
kanvas. Terinspirasi studi motif hitam-putih (panah radiasi + target
konsentris, gradasi lingkaran diagonal, bentuk geometris berselang-seling
menyilang, garis diagonal beranyam).

Empat varian:
1. arrow_burst    -> panah-panah memanjang dari pusat ke penjuru kanvas,
                      dengan lingkaran target konsentris di titik pusat.
2. dot_gradient_x -> dua garis diagonal (membentuk X) berisi lingkaran
                      bergradasi ukuran, dari besar di ujung ke kecil di
                      tengah (atau sebaliknya) -- efek "halftone" klasik.
3. shape_cross    -> 4 lengan menyilang, tiap lengan berisi barisan
                      bentuk geometris berselang-seling (segitiga,
                      lingkaran, kotak) yang mengecil menuju pusat.
4. weave_stripes  -> garis-garis diagonal yang beranyam/menjalin,
                      menciptakan ilusi tenun optik.
"""

import math
import random
from typing import List, Tuple

from PIL import Image, ImageDraw


class RadialMotifGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # 1. ARROW BURST (panah radiasi + target konsentris)
    # ------------------------------------------------------------------
    def generate_arrow_burst(self, n_arms: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        cx, cy = W / 2, H / 2
        n_arms = n_arms or self.rng.choice([4, 6, 8])
        max_r = min(W, H) * 0.47
        start_r = min(W, H) * 0.09

        base_angle = self.rng.uniform(0, math.tau / n_arms)
        for i in range(n_arms):
            angle = base_angle + i * (math.tau / n_arms)
            self._draw_arrow_segmented(draw, cx, cy, angle, start_r, max_r, ss)

        # Target konsentris di pusat
        n_rings = self.rng.randint(4, 6)
        for k in range(n_rings, 0, -1):
            r = start_r * 0.85 * (k / n_rings)
            fill = 0 if k % 2 == 1 else 255
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
                         outline=0, width=max(1, ss))

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    def _draw_arrow_segmented(self, draw, cx, cy, angle, r0, r1, ss):
        """Satu 'panah' tersusun dari beberapa segmen trapesium yang
        mengecil menjauhi pusat, diakhiri kepala panah (segitiga)."""
        n_seg = self.rng.randint(4, 6)
        ca, sa = math.cos(angle), math.sin(angle)
        perp = (-sa, ca)
        seg_len = (r1 - r0) / (n_seg + 1)

        for s in range(n_seg):
            inner_r = r0 + s * seg_len
            outer_r = r0 + (s + 1) * seg_len * 0.82  # sedikit gap antar-segmen
            half_w = seg_len * 0.34 * (1 - s / (n_seg * 1.6))
            p1 = (cx + inner_r * ca - half_w * perp[0], cy + inner_r * sa - half_w * perp[1])
            p2 = (cx + inner_r * ca + half_w * perp[0], cy + inner_r * sa + half_w * perp[1])
            half_w2 = half_w * 0.7
            p3 = (cx + outer_r * ca + half_w2 * perp[0], cy + outer_r * sa + half_w2 * perp[1])
            p4 = (cx + outer_r * ca - half_w2 * perp[0], cy + outer_r * sa - half_w2 * perp[1])
            draw.polygon([p1, p2, p3, p4], fill=0)

        # Kepala panah di ujung terluar
        tip_r = r1
        base_r = r1 - seg_len * 1.3
        half_w = seg_len * 0.5
        tip = (cx + tip_r * ca, cy + tip_r * sa)
        b1 = (cx + base_r * ca - half_w * perp[0], cy + base_r * sa - half_w * perp[1])
        b2 = (cx + base_r * ca + half_w * perp[0], cy + base_r * sa + half_w * perp[1])
        draw.polygon([tip, b1, b2], fill=0)

    # ------------------------------------------------------------------
    # 2. DOT GRADIENT X (lingkaran bergradasi ukuran membentuk X)
    # ------------------------------------------------------------------
    def generate_dot_gradient_x(self, n_per_arm: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        cx, cy = W / 2, H / 2
        max_r = min(W, H) * 0.46
        n_per_arm = n_per_arm or self.rng.randint(9, 13)
        n_diag = self.rng.choice([2, 4])  # 2 = satu garis X penuh, 4 = X + tambahan tegak/datar

        max_dot_r = min(W, H) * self.rng.uniform(0.028, 0.042)
        min_dot_r = max_dot_r * 0.12
        grow_outward = self.rng.choice([True, False])

        # Latar dot-field halus (opsional, memberi kesan "ramai" seperti referensi)
        self._sprinkle_background_dots(draw, W, H, max_dot_r * 0.35, density=0.10)

        for a in range(n_diag):
            angle = a * (math.pi / max(2, n_diag)) if n_diag > 2 else (math.pi / 4 if a == 0 else -math.pi / 4)
            ca, sa = math.cos(angle), math.sin(angle)
            for side in (-1, 1):
                for i in range(1, n_per_arm + 1):
                    t = i / n_per_arm
                    r = t * max_r
                    size_t = t if grow_outward else (1 - t)
                    radius = min_dot_r + (max_dot_r - min_dot_r) * size_t
                    jitter = radius * self.rng.uniform(-0.15, 0.15)
                    px = cx + side * r * ca + jitter
                    py = cy + side * r * sa + jitter
                    draw.ellipse([px - radius, py - radius, px + radius, py + radius], fill=0)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    def _sprinkle_background_dots(self, draw, W, H, r, density=0.08):
        n = int(W * H * density / (r * r * 400))
        for _ in range(max(0, n)):
            x = self.rng.uniform(0, W)
            y = self.rng.uniform(0, H)
            rr = r * self.rng.uniform(0.3, 1.0)
            draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=0)

    # ------------------------------------------------------------------
    # 3. SHAPE CROSS (bentuk geometris berselang-seling menyilang)
    # ------------------------------------------------------------------
    def generate_shape_cross(self, n_arms: int = 4, n_per_arm: int = None,
                              supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        cx, cy = W / 2, H / 2
        max_r = min(W, H) * 0.46
        n_per_arm = n_per_arm or self.rng.randint(4, 6)
        shapes = ["triangle", "square", "circle"]
        self.rng.shuffle(shapes)

        base_angle = self.rng.uniform(0, math.pi / n_arms)
        for i in range(n_arms):
            angle = base_angle + i * (math.tau / n_arms)
            self._draw_shape_arm(draw, cx, cy, angle, max_r, n_per_arm, shapes, ss)

        # Elemen kecil di pusat agar tidak kosong (titik fokus komposisi)
        core_r = max_r * 0.05
        draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=0)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    def _draw_shape_arm(self, draw, cx, cy, angle, max_r, n_shapes, shapes, ss):
        ca, sa = math.cos(angle), math.sin(angle)
        min_r = max_r * 0.22
        for i in range(n_shapes):
            t = i / max(1, n_shapes - 1)
            r = min_r + (max_r - min_r) * t
            size = max_r * (0.045 + 0.11 * t)  # kecil dekat pusat, besar ke ujung
            px, py = cx + r * ca, cy + r * sa
            shape = shapes[i % len(shapes)]
            if shape == "triangle":
                tip = (px + size * ca, py + size * sa)
                base_cx, base_cy = px - size * 0.5 * ca, py - size * 0.5 * sa
                perp_x, perp_y = -sa, ca
                b1 = (base_cx + perp_x * size * 0.55, base_cy + perp_y * size * 0.55)
                b2 = (base_cx - perp_x * size * 0.55, base_cy - perp_y * size * 0.55)
                draw.polygon([tip, b1, b2], fill=0)
            elif shape == "square":
                half = size * 0.62
                draw.polygon([
                    (px - half, py - half), (px + half, py - half),
                    (px + half, py + half), (px - half, py + half)], fill=0)
            else:  # circle
                r2 = size * 0.62
                draw.ellipse([px - r2, py - r2, px + r2, py + r2], fill=0)

    # ------------------------------------------------------------------
    # 4. WEAVE STRIPES (garis diagonal beranyam)
    # ------------------------------------------------------------------
    def generate_weave_stripes(self, n_bands: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        n_bands = n_bands or self.rng.randint(14, 20)
        band_w = W / n_bands
        weave_period = self.rng.randint(3, 5)  # tiap N band, arah miring berselang-seling

        for b in range(n_bands):
            x0 = b * band_w
            phase = (b // weave_period) % 2
            tilt = self.rng.uniform(0.35, 0.55) * H * (1 if phase == 0 else -1)
            n_stripes = self.rng.randint(3, 5)
            stripe_w = band_w / (n_stripes * 2)
            for s in range(n_stripes):
                sx = x0 + s * stripe_w * 2
                draw.polygon([
                    (sx, 0), (sx + stripe_w, 0),
                    (sx + stripe_w + tilt, H), (sx + tilt, H),
                ], fill=0)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")
