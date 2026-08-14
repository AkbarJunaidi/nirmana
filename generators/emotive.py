"""
emotive.py
===========
"Nirmana adalah jeritan sunyi yang terperangkap di antara persimpangan
garis dan lengkung; ia tidak merekam rupa, melainkan mengendapkan denyut
emosi yang terlalu telanjang untuk dijelaskan oleh kata-kata."

Semua teknik lain di sistem ini bekerja dari KEPASTIAN matematis: simetri,
distorsi terkontrol, tessellasi presisi. Modul ini justru bekerja dari
KETIDAKPASTIAN yang disengaja -- goresan yang lahir dari random-walk
bermomentum (bukan kurva matematis rapi), lebar garis yang naik-turun
mengikuti fungsi "denyut" (bukan gradasi linear), dan simpul-simpul kusut
di titik-titik tekanan yang tidak bisa diprediksi sebelumnya sekalipun
oleh seed yang sama dijalankan dua kali dengan parameter berbeda.

Tidak ada objek yang direpresentasikan. Tidak ada makna yang disandikan.
Yang ada hanya: tegangan antara garis lurus (tajam, keras, menyayat) dan
lengkung (lembut, mengalir, menyerah) -- dan jejak tekanan yang menumpuk
di titik-titik tertentu seperti luka yang ditekan berulang kali.

Tiga elemen dikomposisikan bersama dalam SATU karya:
1. gesture_strokes -> goresan sapuan panjang, lebar berdenyut (pulse),
   lahir dari random-walk bermomentum -- gestur mentah, bukan kurva
   yang dihitung untuk "terlihat bagus".
2. severing_lines   -> garis lurus tajam yang menyayat/memotong gestur,
   representasi ketegangan/persimpangan yang disebut dalam kalimat.
3. tension_knots    -> simpul kusut di titik-titik tekanan -- tempat
   "jeritan" mengendap dan tidak bisa lagi mengalir keluar.
"""

import math
import random
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


class EmotiveGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.nprng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # KOMPOSISI UTAMA
    # ------------------------------------------------------------------
    def generate(self, intensity: float = None, supersample: int = 2) -> Image.Image:
        """intensity (0..1, None=acak): seberapa 'tegang' komposisinya --
        makin tinggi, makin banyak garis penyayat & simpul kusut, makin
        sedikit ruang kosong untuk 'bernapas'."""
        ss = supersample
        W, H = self.w * ss, self.h * ss
        intensity = intensity if intensity is not None else self.rng.uniform(0.35, 0.85)

        # Kanvas dasar: wash tonal sangat halus (napas latar, bukan objek)
        base = self._tonal_wash(W, H)

        # Lapisan gestur (ink build-up via alpha compositing)
        ink = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        n_gestures = max(2, round(3 + intensity * 4))
        for _ in range(n_gestures):
            self._draw_gesture_stroke(ink, W, H, ss)

        n_lines = max(2, round(3 + intensity * 9))
        for _ in range(n_lines):
            self._draw_severing_line(ink, W, H, ss)

        n_knots = max(1, round(1 + intensity * 4))
        for _ in range(n_knots):
            self._draw_tension_knot(ink, W, H, ss)

        composed = Image.alpha_composite(base.convert("RGBA"), ink).convert("RGB")

        if ss > 1:
            composed = composed.resize((self.w, self.h), Image.LANCZOS)
        return composed

    # ------------------------------------------------------------------
    # LATAR: wash tonal sangat halus -- napas, bukan bentuk
    # ------------------------------------------------------------------
    def _tonal_wash(self, W: int, H: int) -> Image.Image:
        n = 220  # kerja di resolusi rendah lalu upscale, cukup untuk wash halus
        field = self.nprng.normal(0, 1, (n, n)).astype(np.float32)
        # blur bertingkat (approx multi-octave) supaya berawan, bukan noise kasar
        img_small = Image.fromarray(((field - field.min()) / (field.max() - field.min()) * 255).astype(np.uint8))
        img_small = img_small.filter(ImageFilter.GaussianBlur(radius=n * 0.06))
        arr = np.asarray(img_small, dtype=np.float32) / 255.0
        # kompres kontras jadi sangat halus (hampir putih, cuma jejak awan tipis)
        arr = 250 - arr * self.rng.uniform(6, 16)
        arr = np.clip(arr, 235, 255).astype(np.uint8)
        wash = Image.fromarray(arr, mode="L").resize((W, H), Image.LANCZOS).convert("RGB")
        return wash

    # ------------------------------------------------------------------
    # ELEMEN 1: GESTURE STROKE (sapuan bermomentum, lebar berdenyut)
    # ------------------------------------------------------------------
    def _draw_gesture_stroke(self, ink: Image.Image, W: int, H: int, ss: int):
        draw = ImageDraw.Draw(ink, "RGBA")

        x = self.rng.uniform(W * 0.15, W * 0.85)
        y = self.rng.uniform(H * 0.15, H * 0.85)
        heading = self.rng.uniform(0, math.tau)

        n_steps = self.rng.randint(90, 160)
        step_len = min(W, H) * self.rng.uniform(0.006, 0.011)

        # momentum: arah baru = campuran arah lama + dorongan acak, jadi
        # gestur mengalir (bukan lompat-lompat kacau seperti noise murni)
        momentum = self.rng.uniform(0.82, 0.93)
        turbulence = self.rng.uniform(0.35, 0.75)

        # fungsi "denyut": amplop lebar sepanjang goresan -- tipis di awal,
        # membengkak di titik tertekan, menipis lagi -- BUKAN gradasi rapi
        n_pulses = self.rng.randint(2, 4)
        pulse_centers = sorted(self.rng.uniform(0.1, 0.9) for _ in range(n_pulses))
        pulse_widths = [self.rng.uniform(0.06, 0.16) for _ in range(n_pulses)]

        base_w = min(W, H) * self.rng.uniform(0.006, 0.011)
        max_w = base_w * self.rng.uniform(3.5, 6.5)

        gray = self.rng.randint(15, 45)
        alpha = self.rng.randint(130, 190)

        prev = (x, y)
        for i in range(n_steps):
            t = i / n_steps
            heading += self.rng.uniform(-turbulence, turbulence) * (1 - momentum)
            nx = x + step_len * math.cos(heading)
            ny = y + step_len * math.sin(heading)

            # tekanan (width) di titik ini: dasar + jumlah kontribusi tiap pulse
            pulse = 0.0
            for pc, pw in zip(pulse_centers, pulse_widths):
                pulse += math.exp(-((t - pc) ** 2) / (2 * pw * pw))
            width = base_w + (max_w - base_w) * min(1.0, pulse)
            width *= self.rng.uniform(0.85, 1.15)  # jitter tangan gemetar

            draw.line([prev, (nx, ny)], fill=(gray, gray, gray, alpha), width=max(1, int(width)))
            # dab bulat di ujung supaya sambungan mulus (seperti kuas asli)
            r = width / 2
            draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=(gray, gray, gray, alpha))

            prev = (nx, ny)
            x, y = nx, ny
            if not (0 <= x <= W and 0 <= y <= H):
                break  # goresan keluar kanvas -- biarkan terpotong, jangan dipaksa balik

    # ------------------------------------------------------------------
    # ELEMEN 2: SEVERING LINE (garis lurus tajam yang menyayat)
    # ------------------------------------------------------------------
    def _draw_severing_line(self, ink: Image.Image, W: int, H: int, ss: int):
        draw = ImageDraw.Draw(ink, "RGBA")

        angle = self.rng.uniform(0, math.pi)
        length = min(W, H) * self.rng.uniform(0.35, 1.15)
        cx = self.rng.uniform(W * 0.1, W * 0.9)
        cy = self.rng.uniform(H * 0.1, H * 0.9)
        ca, sa = math.cos(angle), math.sin(angle)

        x0, y0 = cx - length / 2 * ca, cy - length / 2 * sa
        x1, y1 = cx + length / 2 * ca, cy + length / 2 * sa

        width = max(1, int(ss * self.rng.uniform(0.6, 1.6)))
        alpha = self.rng.randint(150, 235)

        # kadang garis putus di tengah (jeda, bukan menyayat tuntas) --
        # ketidaktuntasan yang disengaja
        if self.rng.random() < 0.3:
            gap_t0 = self.rng.uniform(0.35, 0.55)
            gap_t1 = gap_t0 + self.rng.uniform(0.05, 0.15)
            draw.line([(x0, y0), (x0 + (x1 - x0) * gap_t0, y0 + (y1 - y0) * gap_t0)],
                      fill=(10, 10, 10, alpha), width=width)
            draw.line([(x0 + (x1 - x0) * gap_t1, y0 + (y1 - y0) * gap_t1), (x1, y1)],
                      fill=(10, 10, 10, alpha), width=width)
        else:
            draw.line([(x0, y0), (x1, y1)], fill=(10, 10, 10, alpha), width=width)

    # ------------------------------------------------------------------
    # ELEMEN 3: TENSION KNOT (simpul kusut di titik tekanan)
    # ------------------------------------------------------------------
    def _draw_tension_knot(self, ink: Image.Image, W: int, H: int, ss: int):
        draw = ImageDraw.Draw(ink, "RGBA")

        cx = self.rng.uniform(W * 0.2, W * 0.8)
        cy = self.rng.uniform(H * 0.2, H * 0.8)
        radius = min(W, H) * self.rng.uniform(0.035, 0.09)

        n_loops = self.rng.randint(14, 26)
        x, y = cx, cy
        angle = self.rng.uniform(0, math.tau)
        gray = self.rng.randint(5, 25)
        alpha = self.rng.randint(150, 210)
        width = max(1, int(ss * self.rng.uniform(0.9, 1.8)))

        for i in range(n_loops):
            angle += self.rng.uniform(1.4, 2.9) * self.rng.choice([-1, 1])
            r = radius * self.rng.uniform(0.15, 1.0)
            nx = cx + r * math.cos(angle) + self.rng.uniform(-radius * 0.1, radius * 0.1)
            ny = cy + r * math.sin(angle) + self.rng.uniform(-radius * 0.1, radius * 0.1)
            draw.line([(x, y), (nx, ny)], fill=(gray, gray, gray, alpha), width=width)
            x, y = nx, ny
