"""
advanced_depth.py
===================
Tiga teknik lanjutan yang mengeksplorasi kedalaman (depth) dari sudut yang
berbeda dari depth_illusion.py:

1. moire_interference  -> dua kisi periodik saling tumpang tindih pada
                           sudut/skala sedikit berbeda. Bukan ilusi optik
                           semu -- ini FENOMENA FISIK NYATA (interferensi
                           gelombang) yang sama persis dipakai di kain
                           tenun, layar, dan security print, menghasilkan
                           pola "beat" yang seolah bergerak/berdenyut.
2. wireframe_mesh       -> permukaan 3D matematis sungguhan (bidang
                           bergelombang / bola) diproyeksikan ke 2D lewat
                           rotasi & perspective-divide asli -- depth di
                           sini bukan ilusi, tapi hasil proyeksi geometri
                           3D->2D yang benar, dengan garis kian menipis &
                           memudar seiring menjauh dari "kamera".
3. droste_zoom          -> rekursi Droste sungguhan: kanvas ditempel ulang
                           (scaled + rotated) ke dalam dirinya sendiri
                           berkali-kali, menghasilkan efek "tak berhingga"
                           asli (bukan sekadar frame konsentris statis).
"""

import math
import random
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw


class AdvancedDepthGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # 1. MOIRE INTERFERENCE
    # ------------------------------------------------------------------
    def generate_moire_interference(self, mode: str = None) -> Image.Image:
        W, H = self.w, self.h
        xs = np.arange(W, dtype=np.float64)
        ys = np.arange(H, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys)

        mode = mode or self.rng.choice(["radial", "linear", "mixed"])
        period = min(W, H) * self.rng.uniform(0.018, 0.03)

        if mode == "radial":
            # Dua kisi lingkaran konsentris dari pusat sedikit berbeda
            c1 = (W * self.rng.uniform(0.42, 0.58), H * self.rng.uniform(0.42, 0.58))
            offset = min(W, H) * self.rng.uniform(0.02, 0.05)
            angle = self.rng.uniform(0, math.tau)
            c2 = (c1[0] + offset * math.cos(angle), c1[1] + offset * math.sin(angle))

            d1 = np.sqrt((X - c1[0]) ** 2 + (Y - c1[1]) ** 2)
            d2 = np.sqrt((X - c2[0]) ** 2 + (Y - c2[1]) ** 2)
            g1 = (np.floor(d1 / period).astype(np.int64) % 2) == 0
            g2 = (np.floor(d2 / period).astype(np.int64) % 2) == 0

        elif mode == "linear":
            # Dua kisi garis lurus, sudut sedikit berbeda (moire klasik kain tenun)
            a1 = self.rng.uniform(0, math.pi)
            a2 = a1 + math.radians(self.rng.uniform(3, 12)) * self.rng.choice([-1, 1])
            proj1 = X * math.cos(a1) + Y * math.sin(a1)
            proj2 = X * math.cos(a2) + Y * math.sin(a2)
            g1 = (np.floor(proj1 / period).astype(np.int64) % 2) == 0
            g2 = (np.floor(proj2 / period).astype(np.int64) % 2) == 0

        else:  # mixed: kisi radial vs kisi linear -> pola moire paling dramatis
            c1 = (W * self.rng.uniform(0.4, 0.6), H * self.rng.uniform(0.4, 0.6))
            d1 = np.sqrt((X - c1[0]) ** 2 + (Y - c1[1]) ** 2)
            g1 = (np.floor(d1 / period).astype(np.int64) % 2) == 0
            a2 = self.rng.uniform(0, math.pi)
            proj2 = X * math.cos(a2) + Y * math.sin(a2)
            g2 = (np.floor(proj2 / (period * 1.05)).astype(np.int64) % 2) == 0

        interference = g1 ^ g2  # XOR -> fringe pattern khas moire
        gray = np.where(interference, 0, 255).astype(np.uint8)
        return Image.fromarray(gray, mode="L").convert("RGB")

    # ------------------------------------------------------------------
    # 2. WIREFRAME MESH (proyeksi 3D->2D sungguhan)
    # ------------------------------------------------------------------
    def generate_wireframe_mesh(self, surface: str = None, grid_n: int = 34,
                                 supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("RGB", (W, H), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        surface = surface or self.rng.choice(["wave_terrain", "sphere", "saddle"])
        tilt = math.radians(self.rng.uniform(48, 68))     # rotasi sumbu-X (kemiringan pandang)
        spin = math.radians(self.rng.uniform(0, 360))      # rotasi sumbu-Z (arah hadap)
        focal = 2.6
        cam_dist = 3.2

        n = grid_n
        u = np.linspace(-1, 1, n)
        v = np.linspace(-1, 1, n)
        U, V = np.meshgrid(u, v)

        if surface == "wave_terrain":
            freq = self.rng.uniform(2.5, 4.0)
            amp = self.rng.uniform(0.28, 0.42)
            Z = amp * np.sin(freq * U * math.pi) * np.cos(freq * V * math.pi)
            X3, Y3 = U, V
        elif surface == "sphere":
            theta = (U * 0.5 + 0.5) * math.pi          # 0..pi
            phi = (V * 0.5 + 0.5) * math.tau           # 0..2pi
            X3 = np.sin(theta) * np.cos(phi)
            Y3 = np.sin(theta) * np.sin(phi)
            Z = np.cos(theta)
        else:  # saddle
            X3, Y3 = U, V
            Z = (U ** 2 - V ** 2) * self.rng.uniform(0.5, 0.9)

        # Rotasi 3D: spin (sumbu Z) lalu tilt (sumbu X)
        Xr = X3 * math.cos(spin) - Y3 * math.sin(spin)
        Yr = X3 * math.sin(spin) + Y3 * math.cos(spin)
        Yt = Yr * math.cos(tilt) - Z * math.sin(tilt)
        Zt = Yr * math.sin(tilt) + Z * math.cos(tilt)
        Xt = Xr

        # Perspective projection
        denom = (cam_dist - Zt)
        denom = np.where(np.abs(denom) < 0.1, 0.1, denom)
        scale = focal / denom
        cx, cy = W / 2, H / 2
        # size sebelumnya dipatok tunggal ke sisi TERPENDEK (0.34x) dan sama
        # untuk sumbu X & Y -- pada kanvas persegi hasilnya bola kecil di
        # tengah lautan putih; di kanvas rasio panjang (mis. 9:16) malah
        # lebih parah lagi. Sekarang skala dibuat PER-SUMBU mengikuti lebar
        # & tinggi kanvas MASING-MASING (sedikit anamorfik jika kanvas tidak
        # persegi) supaya wireframe benar-benar memenuhi bidang gambar.
        size_x = W * 0.465
        size_y = H * 0.465
        SX = cx + Xt * scale * size_x
        SY = cy - Yt * scale * size_y

        # Bidang objek (bola/pelana/medan gelombang) secara geometris tidak
        # pernah menjangkau SUDUT kanvas persegi -- ditambal aksen garis
        # radiasi tipis ala blueprint teknik dari pusat ke keempat sudut
        # & tepi kanvas, konsisten dengan tema "wireframe" (bukan elemen
        # asing), supaya sudut kanvas tidak terasa kosong melompong.
        corner_pts = [(0, 0), (W, 0), (W, H), (0, H),
                      (W / 2, 0), (W, H / 2), (W / 2, H), (0, H / 2)]
        for (tx, ty) in corner_pts:
            draw.line([(cx, cy), (tx, ty)], fill=(222, 222, 222), width=max(1, ss // 2))
        ring_r_outer = math.hypot(W, H) * 0.5
        for k in range(1, 4):
            rr = ring_r_outer * (0.7 + 0.1 * k)
            draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(222, 222, 222),
                         width=max(1, ss // 2))

        depth = Zt  # dipakai untuk shading (dekat kamera = Zt besar -> garis lebih tebal/gelap)
        d_min, d_max = depth.min(), depth.max()
        depth_norm = (depth - d_min) / max(1e-6, (d_max - d_min))  # 0..1, 1 = paling dekat

        def draw_edge(i0, j0, i1, j1):
            dn = (depth_norm[i0, j0] + depth_norm[i1, j1]) / 2
            shade = int(230 - dn * 210)
            width = max(1, int(ss * (0.6 + dn * 2.2)))
            draw.line([(SX[i0, j0], SY[i0, j0]), (SX[i1, j1], SY[i1, j1])],
                      fill=(shade, shade, shade), width=width)

        # Gambar garis dari titik terjauh ke terdekat (painter's algorithm sederhana)
        order = np.argsort(depth_norm, axis=None)
        drawn_h = np.zeros_like(depth_norm, dtype=bool)
        for idx in order:
            i, j = np.unravel_index(idx, depth_norm.shape)
            if j < n - 1:
                draw_edge(i, j, i, j + 1)
            if i < n - 1:
                draw_edge(i, j, i + 1, j)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ------------------------------------------------------------------
    # 3. DROSTE ZOOM (rekursi tak berhingga sungguhan)
    # ------------------------------------------------------------------
    def generate_droste_zoom(self, base_image: Image.Image = None, levels: int = 6,
                              scale_factor: float = None, rotate_per_level: float = None) -> Image.Image:
        W, H = self.w, self.h

        if base_image is None:
            base_image = self._default_base_pattern(W, H)
        img = base_image.convert("RGB").resize((W, H))

        scale_factor = scale_factor or self.rng.uniform(0.58, 0.68)
        rotate_per_level = rotate_per_level if rotate_per_level is not None else self.rng.uniform(-14, 14)

        target_w, target_h = int(W * scale_factor), int(H * scale_factor)
        px, py = (W - target_w) // 2, (H - target_h) // 2
        border_w = max(2, int(min(W, H) * 0.006))

        canvas = img.copy()
        for level in range(levels):
            shrunk = canvas.resize((target_w, target_h), Image.LANCZOS)
            if rotate_per_level != 0:
                shrunk = shrunk.rotate(rotate_per_level * (level + 1), resample=Image.BICUBIC,
                                        expand=False, fillcolor=(255, 255, 255))
            new_canvas = canvas.copy()
            new_canvas.paste(shrunk, (px, py))
            d = ImageDraw.Draw(new_canvas)
            d.rectangle([px, py, px + target_w - 1, py + target_h - 1],
                        outline=(10, 10, 10), width=border_w)
            canvas = new_canvas

        return canvas

    def _default_base_pattern(self, w: int, h: int) -> Image.Image:
        """Pola dasar bawaan untuk Droste bila tidak diberi base_image --
        pakai kisi radial sederhana supaya rekursinya tetap jelas terbaca."""
        img = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        cx, cy = w / 2, h / 2
        n_spokes = 24
        max_r = math.hypot(w, h) / 2
        for i in range(n_spokes):
            a = (i / n_spokes) * math.tau
            draw.line([(cx, cy), (cx + max_r * math.cos(a), cy + max_r * math.sin(a))],
                      fill=(30, 30, 30), width=2)
        for rr in range(1, 10):
            r = max_r * rr / 10
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 30, 30), width=2)
        return img
