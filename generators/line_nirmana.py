"""
line_nirmana.py
================
Nirmana Garis bergaya Op-Art / liquid distortion, sesuai referensi
"Putri Marcella Azzizah - Nirmana Garis": garis-garis paralel tebal yang
dibengkokkan mengelilingi beberapa titik fokus sehingga membentuk pola
mengalir mirip sidik jari / marmer cair.

Teknik: warp koordinat kanvas dengan WarpField (vortex chain), lalu gambar
pita (band) hitam-putih berdasarkan posisi X yang sudah terdistorsi.
Supersampling 2x dipakai untuk anti-aliasing tepi garis yang bersih.
"""

import numpy as np
from PIL import Image
import random

from .flowfield import WarpField


class LineNirmanaGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    def generate(
        self,
        band_count: int = 26,          # jumlah pita hitam+putih melintasi kanvas
        duty_cycle: float = None,       # proporsi hitam per pita (None = acak halus)
        supersample: int = 2,
        anchor_count: tuple = (2, 4),
        invert: bool = False,
    ) -> Image.Image:
        ss = max(1, supersample)
        W, H = self.w * ss, self.h * ss

        # 1. Bangun medan distorsi (beberapa pusaran acak, terkontrol)
        field = WarpField(W, H, seed=self.seed)
        field.randomize_anchors(n_min=anchor_count[0], n_max=anchor_count[1])

        # 2. Grid koordinat dasar
        xs = np.arange(W, dtype=np.float64)
        ys = np.arange(H, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys)

        Xw, Yw = field.apply(X, Y)

        # 3. Pola pita dasar: gradient linear pada Xw dengan sedikit kontribusi Yw
        #    supaya band tidak melulu vertikal tapi punya kemiringan alami.
        tilt = self.rng.uniform(-0.15, 0.15)
        phase = Xw + Yw * tilt

        period = W / band_count
        duty = duty_cycle if duty_cycle is not None else self.rng.uniform(0.42, 0.58)

        t = (phase % period) / period  # 0..1 posisi dalam satu pita

        # Anti-alias tepi pita: smoothstep tipis di sekitar batas duty cycle
        edge = 0.015
        black_mask = np.clip((duty - t) / edge + 0.5, 0.0, 1.0)
        # tepi satunya (wrap-around dekat t=1 -> t=0 juga harus mulus)
        wrap_mask = np.clip((t - (1 - edge * 2)) / edge, 0.0, 1.0)
        black_mask = np.clip(black_mask + wrap_mask * 0, 0.0, 1.0)

        if invert:
            black_mask = 1.0 - black_mask

        gray = ((1.0 - black_mask) * 255).astype(np.uint8)  # 0 = hitam, 255 = putih
        img = Image.fromarray(gray, mode="L").convert("RGB")

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)

        return img
