"""
stratum.py
===========
Tiga teknik kedalaman yang bukan trik optik (bukan vanishing point, bukan
moire, bukan proyeksi 3D matematis) -- melainkan kedalaman yang lahir dari
cara paling purba manusia memahami "dalam": lapisan yang menumpuk dan
terkikis, kekosongan yang menegaskan kepenuhan di sekelilingnya, dan
patahan yang menyingkap apa yang tadinya tersembunyi.

Tidak ada objek. Tidak ada makna yang disandikan. Yang ada hanya struktur
formal: penumpukan (occlusion), ketiadaan (negative space), dan diskontinuitas
(displacement) -- tiga mekanisme dasar yang membuat mata membaca "kedalaman"
bahkan tanpa satupun elemen representasional.

1. sedimen   -> lapisan-lapisan translusen menumpuk dengan batas tak rata
                (endapan), sebagian tererosi/tersobek hingga menyingkap
                lapisan di bawahnya -- kedalaman lewat sejarah penumpukan.
2. kekosongan -> medan tekstur padat (guratan liar memenuhi bidang) yang
                dilubangi oleh rongga-rongga kosong berbentuk organik --
                kedalaman lewat tegangan antara penuh dan tiada.
3. patahan   -> pita-pita berlapis yang disesar/digeser sepanjang garis
                patahan vertikal acak, seperti penampang geologis yang
                retak -- kedalaman lewat diskontinuitas & pergeseran.
"""

import math
import random
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .precision import draw_precise_polyline


class StratumGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.nprng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # 1. SEDIMEN -- lapisan menumpuk, sebagian tererosi/tersobek
    # ------------------------------------------------------------------
    def generate_sedimen(self, n_layers: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        n_layers = n_layers or self.rng.randint(6, 10)

        canvas = Image.new("RGB", (W, H), (250, 248, 244))

        # Urutan dari lapisan TERTUA (paling bawah, digambar duluan, warna
        # paling gelap -- endapan lama) ke TERMUDA (paling atas, paling terang)
        boundaries = self._layer_boundaries(W, H, n_layers)

        for i in range(n_layers):
            t = i / max(1, n_layers - 1)
            shade = int(35 + t * 190)  # gelap (tua) -> terang (muda)
            layer_color = (shade, shade - self.rng.randint(0, 6), shade - self.rng.randint(0, 10))

            top = boundaries[i]
            bottom = boundaries[i + 1] if i + 1 < len(boundaries) else np.full(W, H, dtype=np.float64)

            snapshot = canvas.copy()  # kondisi kanvas SEBELUM lapisan ini ditumpuk

            layer_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer_img)
            poly = list(zip(range(W), top.tolist())) + list(zip(range(W - 1, -1, -1), bottom[::-1].tolist()))
            ld.polygon(poly, fill=(*layer_color, 235))

            # Butiran halus di dalam lapisan (grain) via noise ringan
            grain = self.nprng.integers(-10, 10, (H, W)).astype(np.int16)
            base_arr = np.asarray(layer_img.convert("RGBA")).astype(np.int16)
            for c in range(3):
                base_arr[..., c] = np.clip(base_arr[..., c] + grain, 0, 255)
            layer_img = Image.fromarray(base_arr.astype(np.uint8), mode="RGBA")

            canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), layer_img).convert("RGB"), (0, 0))

            # Erosi: sobekan acak yang menyingkap lapisan di bawahnya --
            # cukup dilakukan dengan mengembalikan sebagian area ini ke
            # kondisi SEBELUM lapisan ditumpuk (snapshot)
            if i > 0 and self.rng.random() < 0.75:
                self._apply_erosion_tear(canvas, snapshot, top, bottom, W, H)

        # Retakan halus vertikal menembus beberapa lapisan sekaligus
        n_cracks = self.rng.randint(2, 5)
        draw = ImageDraw.Draw(canvas)
        for _ in range(n_cracks):
            self._draw_settling_crack(draw, W, H)

        if ss > 1:
            canvas = canvas.resize((self.w, self.h), Image.LANCZOS)
        return canvas

    def _layer_boundaries(self, W: int, H: int, n_layers: int) -> List[np.ndarray]:
        """n_layers+1 garis batas horizontal tak rata (endapan tidak pernah
        rata sempurna), dari atas kanvas ke bawah, tersusun menaik."""
        xs = np.arange(W)
        boundaries = [np.zeros(W)]
        cur_base = H * self.rng.uniform(0.04, 0.10)
        step = (H * 0.94) / n_layers
        for i in range(n_layers):
            cur_base += step * self.rng.uniform(0.75, 1.25)
            n_harm = self.rng.randint(2, 4)
            wave = np.zeros(W)
            for k in range(n_harm):
                freq = self.rng.uniform(1, 4) * (k + 1)
                phase = self.rng.uniform(0, math.tau)
                amp = step * self.rng.uniform(0.08, 0.22) / (k + 1)
                wave += amp * np.sin(freq * xs / W * math.tau + phase)
            boundaries.append(np.clip(cur_base + wave, 0, H))
        return boundaries

    def _apply_erosion_tear(self, canvas: Image.Image, snapshot: Image.Image,
                             top: np.ndarray, bottom: np.ndarray, W: int, H: int):
        """Menghapus sepotong area lapisan teratas (dengan tepi tak rata)
        supaya lapisan di bawahnya (snapshot sebelum lapisan ini ditumpuk)
        tersingkap -- 'luka' pada endapan."""
        tear_w = self.rng.uniform(W * 0.08, W * 0.28)
        tx0 = self.rng.uniform(0, W - tear_w)
        tx1 = tx0 + tear_w

        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        xs_local = np.linspace(tx0, tx1, 24)
        top_local = np.interp(xs_local, np.arange(W), top)
        bot_local = np.interp(xs_local, np.arange(W), bottom)
        jitter = (bot_local - top_local) * 0.15
        top_j = top_local + self.nprng.uniform(-1, 1, len(xs_local)) * jitter
        bot_j = bot_local - self.nprng.uniform(-1, 1, len(xs_local)) * jitter
        poly = list(zip(xs_local, top_j)) + list(zip(xs_local[::-1], bot_j[::-1]))
        md.polygon(poly, fill=255)

        canvas.paste(snapshot, (0, 0), mask)

    def _draw_settling_crack(self, draw, W: int, H: int):
        x = self.rng.uniform(W * 0.1, W * 0.9)
        y = 0.0
        col = self.rng.randint(15, 40)
        pts = [(x, y)]
        while y < H:
            y += H * self.rng.uniform(0.02, 0.05)
            x += self.rng.uniform(-W * 0.02, W * 0.02)
            pts.append((x, y))
        draw_precise_polyline(draw, pts, (col, col, col), max(1, int(min(W, H) * 0.0015)))

    # ------------------------------------------------------------------
    # 2. KEKOSONGAN -- tekstur padat dilubangi rongga organik
    # ------------------------------------------------------------------
    def generate_kekosongan(self, n_voids: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img, "L")

        # --- Medan tekstur padat: ribuan guratan pendek acak memenuhi bidang ---
        density = self.rng.uniform(0.55, 0.85)
        n_strokes = int(W * H * density / (min(W, H) ** 2) * 3200)
        stroke_len = min(W, H) * 0.02

        for _ in range(n_strokes):
            x = self.rng.uniform(0, W)
            y = self.rng.uniform(0, H)
            a = self.rng.uniform(0, math.pi)
            l = stroke_len * self.rng.uniform(0.4, 1.6)
            x0, y0 = x - l / 2 * math.cos(a), y - l / 2 * math.sin(a)
            x1, y1 = x + l / 2 * math.cos(a), y + l / 2 * math.sin(a)
            gray = self.rng.randint(0, 60)
            draw.line([(x0, y0), (x1, y1)], fill=gray, width=max(1, int(ss)))

        # --- Rongga kosong: bentuk organik (blob amoeba) yang menghapus tekstur ---
        n_voids = n_voids or self.rng.randint(3, 5)
        mask_full = Image.new("L", (W, H), 0)
        centers: List[Tuple[float, float]] = []
        min_sep = min(W, H) * 0.22
        for _ in range(n_voids):
            for _try in range(20):
                cx = self.rng.uniform(W * 0.15, W * 0.85)
                cy = self.rng.uniform(H * 0.15, H * 0.85)
                if all(math.hypot(cx - px, cy - py) > min_sep for px, py in centers):
                    break
            centers.append((cx, cy))
            self._carve_void(mask_full, W, H, cx, cy)

        void_arr = np.asarray(mask_full)
        img_arr = np.asarray(img).copy()
        # Di dalam rongga: gradasi sangat halus (kesan 'melihat ke dalam
        # lubang', bukan sekadar putih polos)
        gradient_boost = (void_arr.astype(np.float32) / 255.0)
        img_arr = np.where(void_arr > 10,
                            np.clip(255 - (255 - img_arr) * (1 - gradient_boost) * 0.15, 0, 255),
                            img_arr)
        img = Image.fromarray(img_arr.astype(np.uint8), mode="L")

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    def _carve_void(self, mask_full: Image.Image, W: int, H: int, cx: float, cy: float):
        base_r = min(W, H) * self.rng.uniform(0.07, 0.13)
        n_harm = self.rng.randint(3, 5)
        phases = [self.rng.uniform(0, math.tau) for _ in range(n_harm)]
        amps = [self.rng.uniform(0.06, 0.18) / (i + 1) for i in range(n_harm)]

        n_pts = 90
        pts = []
        for k in range(n_pts + 1):
            theta = (k / n_pts) * math.tau
            r = base_r
            for h in range(n_harm):
                r += base_r * amps[h] * math.sin((h + 2) * theta + phases[h])
            pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))

        # Gradasi tepi lembut: gambar beberapa polygon menyusut dgn alpha naik
        layer = Image.new("L", (W, H), 0)
        ld = ImageDraw.Draw(layer)
        n_rings = 10
        for ring in range(n_rings, 0, -1):
            scale = ring / n_rings
            shrink_pts = [(cx + (px - cx) * scale, cy + (py - cy) * scale) for px, py in pts]
            val = int(255 * (1 - (ring / n_rings) * 0.0 + (n_rings - ring) / n_rings))
            ld.polygon(shrink_pts, fill=min(255, int(255 * (ring / n_rings) ** 0.4)))

        merged = np.maximum(np.asarray(mask_full), np.asarray(layer))
        mask_full.paste(Image.fromarray(merged, mode="L"), (0, 0))

    # ------------------------------------------------------------------
    # 3. PATAHAN -- pita berlapis disesar sepanjang garis patahan
    # ------------------------------------------------------------------
    def generate_patahan(self, n_bands: int = None, n_faults: int = None,
                          supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        n_bands = n_bands or self.rng.randint(7, 11)
        n_faults = n_faults or self.rng.randint(2, 4)

        band_h = H / n_bands
        fault_xs = sorted(self.rng.uniform(W * 0.15, W * 0.85) for _ in range(n_faults))

        # Tiap band: daftar segmen (x0,x1) dengan offset vertikal berbeda
        canvas = Image.new("RGB", (W, H), (245, 245, 242))
        draw = ImageDraw.Draw(canvas)

        for b in range(n_bands):
            y0 = b * band_h
            shade = self.rng.randint(30, 210)
            tint = self.rng.choice([0, 0, self.rng.randint(-15, 15)])

            segment_bounds = [0] + fault_xs + [W]
            base_offset = self.rng.uniform(-band_h * 0.5, band_h * 0.5)
            offsets = [base_offset]
            for _ in range(n_faults):
                base_offset += self.rng.uniform(-band_h * 0.9, band_h * 0.9)
                offsets.append(base_offset)

            for s in range(len(segment_bounds) - 1):
                x0, x1 = segment_bounds[s], segment_bounds[s + 1]
                dy = offsets[s]
                yy0 = np.clip(y0 + dy, -band_h, H)
                yy1 = np.clip(y0 + band_h + dy, -band_h, H + band_h)
                col = (shade + tint, shade, max(0, shade - tint))
                draw.rectangle([x0, yy0, x1, yy1], fill=col)

        # Garis patahan tegas di posisi tiap fault
        for fx in fault_xs:
            width = max(1, int(ss * self.rng.uniform(1.0, 2.2)))
            jitter_pts = [(fx + self.rng.uniform(-W * 0.004, W * 0.004), y)
                          for y in np.linspace(0, H, 20)]
            draw_precise_polyline(draw, jitter_pts, (15, 15, 15), width)

        if ss > 1:
            canvas = canvas.resize((self.w, self.h), Image.LANCZOS)
        return canvas
