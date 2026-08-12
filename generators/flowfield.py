"""
flowfield.py
================
Mesin distorsi koordinat (coordinate warp) berbasis medan vektor (vortex field).
Dipakai sebagai "otot" matematis di balik Nirmana Garis (Op-Art) dan variasi
distorsi lain (organik, geometrik) agar semua modul punya bahasa distorsi yang
konsisten dan bisa dikombinasikan.

Prinsip: alih-alih menggambar garis lurus lalu membengkokkannya secara manual,
kita mendistorsi RUANG (koordinat x,y) itu sendiri dengan beberapa "pusaran"
(vortex) di titik-titik acak, lalu menggambar pola dasar (garis, stripe,
grid) DI ATAS ruang yang sudah terdistorsi. Ini teknik standar generative-art
untuk menghasilkan efek liquid/marble/fingerprint seperti pada referensi.
"""

import numpy as np
import random
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class VortexAnchor:
    cx: float
    cy: float
    radius: float      # jangkauan pengaruh pusaran
    strength: float     # kekuatan rotasi (radian), bisa negatif (arah sebaliknya)
    push: float = 0.0   # dorongan radial tambahan (tarik/dorong dari pusat)


class WarpField:
    """
    Membangun dan menerapkan tumpukan (stack) vortex warp pada grid koordinat
    numpy (X, Y) sekaligus (vectorized -> cepat untuk kanvas resolusi besar).
    """

    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.rng = random.Random(seed)
        self.anchors: List[VortexAnchor] = []

    def randomize_anchors(self, n_min: int = 3, n_max: int = 6,
                           radius_range: Tuple[float, float] = None,
                           strength_range: Tuple[float, float] = (1.1, 2.6),
                           min_separation_factor: float = 0.9):
        """Membuat sejumlah titik pusaran acak namun terkontrol agar tidak
        saling menghilangkan (biar hasil tetap 'terbaca' bentuknya -- satu
        aliran besar yang koheren, bukan banyak spiral kecil yang bertabrakan).
        Jarak minimum antar-anchor dijaga relatif terhadap radius supaya
        pengaruh tiap pusaran tidak saling menumpuk berlebihan."""
        diag = math.hypot(self.w, self.h)
        if radius_range is None:
            radius_range = (diag * 0.22, diag * 0.42)

        n = self.rng.randint(n_min, n_max)
        anchors: List[VortexAnchor] = []
        attempts = 0
        while len(anchors) < n and attempts < n * 40:
            attempts += 1
            cx = self.rng.uniform(self.w * 0.15, self.w * 0.85)
            cy = self.rng.uniform(self.h * 0.15, self.h * 0.85)
            radius = self.rng.uniform(*radius_range)

            ok = True
            for a in anchors:
                min_dist = (radius + a.radius) * 0.5 * min_separation_factor
                if math.hypot(cx - a.cx, cy - a.cy) < min_dist:
                    ok = False
                    break
            if not ok:
                continue

            strength = self.rng.uniform(*strength_range) * self.rng.choice([-1, 1])
            push = self.rng.uniform(-0.15, 0.15) * radius
            anchors.append(VortexAnchor(cx, cy, radius, strength, push))

        # Fallback: kalau penempatan gagal (kanvas kecil), tetap pastikan minimal 2 anchor
        if len(anchors) < 2:
            for _ in range(2 - len(anchors)):
                cx = self.rng.uniform(self.w * 0.25, self.w * 0.75)
                cy = self.rng.uniform(self.h * 0.25, self.h * 0.75)
                radius = self.rng.uniform(*radius_range)
                strength = self.rng.uniform(*strength_range) * self.rng.choice([-1, 1])
                anchors.append(VortexAnchor(cx, cy, radius, strength, 0.0))

        self.anchors = anchors
        return self

    def apply(self, X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Menerapkan seluruh anchor secara berurutan (chained warp) pada
        array koordinat X, Y. Mengembalikan koordinat baru yang terdistorsi."""
        Xw, Yw = X.copy(), Y.copy()
        for a in self.anchors:
            dx = Xw - a.cx
            dy = Yw - a.cy
            dist = np.sqrt(dx * dx + dy * dy) + 1e-6

            # Falloff gaussian: pengaruh kuat di dekat pusat, melemah halus ke tepi
            falloff = np.exp(-(dist * dist) / (2.0 * a.radius * a.radius))

            theta = np.arctan2(dy, dx) + a.strength * falloff
            new_dist = dist + a.push * falloff

            Xw = a.cx + new_dist * np.cos(theta)
            Yw = a.cy + new_dist * np.sin(theta)
        return Xw, Yw
