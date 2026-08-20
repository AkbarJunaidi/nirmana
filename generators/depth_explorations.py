"""
depth_explorations.py
=======================
Jelajah lebih dalam lagi -- tiga teknik yang mendekati "kedalaman" dari
sudut yang sepenuhnya berbeda dari semua modul sebelumnya:

1. anaglyph_relief   -> stereoskopi sungguhan: sebuah height-field (relief)
                         dirender jadi dua sudut pandang (kiri/kanan) yang
                         digeser secara horizontal proporsional terhadap
                         ketinggian, lalu digabung jadi citra merah-cyan.
                         Dipakai kacamata 3D, kedalamannya BENAR-BENAR
                         terlihat -- bukan cuma ilusi di atas kertas.
2. lsystem_branching -> L-System (Lindenmayer System): tata bahasa string
                         rewriting yang sama persis dipakai untuk memodelkan
                         pertumbuhan tanaman secara matematis (bukan random
                         walk seperti DLA) -- percabangan presisi & self-
                         similar, lebar cabang menipis tiap generasi
                         sehingga kedalaman rekursif terasa kuat.
3. parallax_silhouette -> beberapa lapis siluet organik ditumpuk dengan
                         gradasi value & skala (aerial/atmospheric
                         perspective) -- prinsip Gestalt "common fate" +
                         oklusi, cara termudah otak manusia membaca
                         kedalaman: elemen dekat gelap & besar di depan,
                         elemen jauh terang & kecil di belakang.
"""

import math
import random
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


class DepthExplorationGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.nprng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # 1. ANAGLYPH RELIEF (stereoskopi merah-cyan sungguhan)
    # ------------------------------------------------------------------
    def generate_anaglyph_relief(self, max_shift_px: int = None,
                                  pattern: str = None) -> Image.Image:
        """Merender relief 3D sebagai anaglyph merah-cyan. Alih-alih
        menggeser grid piksel penuh (rentan artefak resampling saat shift
        besar), tiap 'bukit' digambar langsung sebagai kontur cincin
        konsentris pada dua kanvas mata kiri/kanan dengan pusat digeser
        proporsional terhadap tinggi lokalnya -- pendekatan yang jauh lebih
        stabil dan justru lebih 'nirmana' (garis kontur, bukan noise titik)."""
        W, H = self.w, self.h
        max_shift_px = max_shift_px or max(10, int(min(W, H) * 0.028))

        left = Image.new("L", (W, H), 255)
        right = Image.new("L", (W, H), 255)
        dl, dr = ImageDraw.Draw(left), ImageDraw.Draw(right)

        # --- Grid referensi halus (statis, sama di kedua mata) supaya mata
        #     punya "lantai" tetap untuk membandingkan pergeseran bukit ---
        spacing = max(18, int(min(W, H) * 0.045))
        for gx in range(0, W, spacing):
            dl.line([(gx, 0), (gx, H)], fill=225, width=1)
            dr.line([(gx, 0), (gx, H)], fill=225, width=1)
        for gy in range(0, H, spacing):
            dl.line([(0, gy), (W, gy)], fill=225, width=1)
            dr.line([(0, gy), (W, gy)], fill=225, width=1)

        n_bumps = self.rng.randint(4, 6)
        line_w = max(1, int(min(W, H) * 0.0028))

        # Penempatan bukit: sebelumnya dibatasi ke zona tengah 60% kanvas
        # (0.2-0.8) dengan hanya 4-6 bukit -- menyisakan bingkai kosong
        # lebar di sekeliling & celah besar antar-bukit. Sekarang dipakai
        # grid+jitter (pola yang sama dipakai di teknik organik) supaya
        # bukit tersebar merata hingga ke tepi kanvas, dan jumlahnya
        # diskalakan terhadap luas kanvas supaya kepadatan tetap konsisten.
        area_factor = (W * H) / (1000 * 1000)
        n_bumps = max(6, int(self.rng.uniform(7, 10) * math.sqrt(max(area_factor, 0.3))))
        grid_cols = max(2, math.ceil(math.sqrt(n_bumps * (W / H))))
        grid_rows = max(2, math.ceil(n_bumps / grid_cols))
        cell_w, cell_h = W / grid_cols, H / grid_rows

        for row in range(grid_rows):
            for col in range(grid_cols):
                bx = (col + self.rng.uniform(0.18, 0.82)) * cell_w
                by = (row + self.rng.uniform(0.18, 0.82)) * cell_h
                br = min(cell_w, cell_h) * self.rng.uniform(0.55, 0.82)
                sign = self.rng.choice([1, 1, -1])  # dominan "menonjol keluar"
                peak_shift = sign * self.rng.uniform(0.55, 1.0) * max_shift_px

                n_rings = self.rng.randint(6, 9)
                for ring_i in range(n_rings, 0, -1):
                    frac = ring_i / n_rings
                    radius = br * frac
                    # tinggi lokal makin besar mendekati puncak (pusat) -> makin
                    # ke tepi cincin, ketinggian & pergeseran makin kecil
                    local_h = math.exp(-((1 - frac) ** 2) / 0.18)
                    shift = peak_shift * local_h
                    shade = int(40 + 170 * (1 - local_h))  # pusat lebih gelap (menonjol)

                    cx_l, cx_r = bx - shift / 2, bx + shift / 2
                    dl.ellipse([cx_l - radius, by - radius, cx_l + radius, by + radius],
                               outline=shade, width=line_w)
                    dr.ellipse([cx_r - radius, by - radius, cx_r + radius, by + radius],
                               outline=shade, width=line_w)

        left_arr = np.asarray(left, dtype=np.float64)
        right_arr = np.asarray(right, dtype=np.float64)

        rgb = np.zeros((H, W, 3), dtype=np.uint8)
        rgb[..., 0] = left_arr.astype(np.uint8)                       # merah = mata kiri
        rgb[..., 1] = right_arr.astype(np.uint8)                      # hijau = mata kanan
        rgb[..., 2] = right_arr.astype(np.uint8)                      # biru  = mata kanan (cyan)

        return Image.fromarray(rgb, mode="RGB")

    # ------------------------------------------------------------------
    # 2. L-SYSTEM BRANCHING (percabangan presisi matematis)
    # ------------------------------------------------------------------
    _LSYSTEM_PRESETS = [
        # (axiom, rules, angle_deg)
        ("F", {"F": "FF-[-F+F+F]+[+F-F-F]"}, 22),
        ("X", {"X": "F-[[X]+X]+F[+FX]-X", "F": "FF"}, 25),
        ("F", {"F": "F[+F]F[-F]F"}, 20),
        ("F", {"F": "F[+F][-F]F"}, 27),
        ("X", {"X": "F[+X][-X]FX", "F": "FF"}, 17),
    ]

    def generate_lsystem_branching(self, iterations: int = None,
                                    supersample: int = 2, n_plants: int = None) -> Image.Image:
        """Serumpun tanaman (bukan cuma satu tangkai kesepian) -- 1 tanaman
        utama lebih besar + beberapa 'anakan' lebih kecil di sekelilingnya,
        semua berpijak di garis dasar yang sama, seperti rumpun semak asli."""
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        # Jumlah rumpun diskalakan terhadap lebar kanvas & proporsi tinggi
        # tanaman dibesarkan signifikan -- sebelumnya tanaman utama cuma
        # mencapai 62-78% tinggi kanvas dan anakan cuma 30-48%, menyisakan
        # bidang langit kosong raksasa di atas (dan pada rasio tertentu
        # rumpun malah numpuk di satu sisi). Sekarang tanaman jauh lebih
        # tinggi & jumlah rumpun mengikuti lebar kanvas supaya benar-benar
        # merentang penuh dari kiri ke kanan, hampir menyentuh tepi atas.
        n_plants = n_plants or max(4, round((W / H) * self.rng.uniform(4.5, 6.0)))

        # Slot horizontal untuk tiap tanaman, sedikit jitter biar tidak kaku
        margin = W * 0.04
        slot_w = (W - margin * 2) / n_plants
        slot_centers = [margin + slot_w * (i + 0.5) + self.rng.uniform(-slot_w * 0.15, slot_w * 0.15)
                        for i in range(n_plants)]
        self.rng.shuffle(slot_centers)

        main_idx = self.rng.randrange(n_plants)

        for p_idx in range(n_plants):
            is_main = (p_idx == main_idx)
            axiom, rules, angle_deg = self.rng.choice(self._LSYSTEM_PRESETS)
            # Iterasi minimum dinaikkan (dari 3 ke 4) supaya tak ada rumpun
            # yang kebetulan jadi nyaris satu garis lurus polos (degenerate).
            iters = (iterations or self.rng.randint(5, 6)) if is_main else self.rng.randint(5, 6)
            angle = math.radians(angle_deg * self.rng.uniform(0.9, 1.1))

            s = axiom
            for _ in range(iters):
                s = "".join(rules.get(c, c) for c in s)
                if len(s) > 150000:
                    break

            max_depth_seen, cur_depth = 1, 0
            for c in s:
                if c == "[":
                    cur_depth += 1
                    max_depth_seen = max(max_depth_seen, cur_depth)
                elif c == "]":
                    cur_depth -= 1

            heading0 = -math.pi / 2
            x, y = 0.0, 0.0
            stack = []
            depth = 0
            segments = []
            minx = maxx = miny = maxy = 0.0
            heading = heading0
            for c in s:
                if c == "F":
                    nx = x + math.cos(heading)
                    ny = y + math.sin(heading)
                    segments.append((x, y, nx, ny, depth))
                    x, y = nx, ny
                    minx, maxx = min(minx, x), max(maxx, x)
                    miny, maxy = min(miny, y), max(maxy, y)
                elif c == "+":
                    heading += angle
                elif c == "-":
                    heading -= angle
                elif c == "[":
                    stack.append((x, y, heading, depth))
                    depth += 1
                elif c == "]":
                    if stack:
                        x, y, heading, depth = stack.pop()

            span_x = max(1e-6, maxx - minx)
            span_y = max(1e-6, maxy - miny)

            target_h = H * (self.rng.uniform(0.84, 0.94) if is_main else self.rng.uniform(0.55, 0.78))
            scale = target_h / span_y
            # Batasi lebar juga supaya tidak menyerbu slot tetangga
            max_w_allowed = slot_w * 1.9
            scale = min(scale, max_w_allowed / span_x)

            offset_x = slot_centers[p_idx] - (minx + maxx) / 2 * scale
            offset_y = H * 0.97 - maxy * scale

            for (x0, y0, x1, y1, d) in segments:
                w_line = max(1, int(ss * (max_depth_seen - d + 1) * (0.6 if is_main else 0.42)))
                draw.line([(x0 * scale + offset_x, y0 * scale + offset_y),
                           (x1 * scale + offset_x, y1 * scale + offset_y)],
                          fill=0, width=w_line)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ------------------------------------------------------------------
    # 3. PARALLAX SILHOUETTE (kedalaman lewat oklusi & aerial perspective)
    # ------------------------------------------------------------------
    def generate_parallax_silhouette(self, n_layers: int = None,
                                      dark_first: bool = True) -> Image.Image:
        W, H = self.w, self.h
        n_layers = n_layers or self.rng.randint(5, 8)
        img = Image.new("RGB", (W, H), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        xs = np.linspace(0, 1, W)

        for layer in range(n_layers):
            t = layer / (n_layers - 1)  # 0 = terjauh, 1 = terdekat
            if not dark_first:
                t = 1 - t

            # Aerial perspective: makin dekat (t besar) makin gelap & besar
            shade = int(235 - t * 215)
            color = (shade, shade, shade)

            n_harm = self.rng.randint(3, 5)
            y_base = H * (0.32 + 0.5 * (layer / n_layers))
            amp = H * (0.05 + 0.16 * (1 - t * 0.5)) * self.rng.uniform(0.7, 1.15)

            ridge = np.zeros(W)
            for k in range(n_harm):
                freq = self.rng.uniform(1.0, 3.5) * (k + 1)
                phase = self.rng.uniform(0, math.tau)
                ridge += (amp / (k + 1)) * np.sin(freq * xs * math.tau + phase)

            y_line = y_base + ridge
            pts = [(float(x), float(y)) for x, y in zip(np.linspace(0, W, W), y_line)]
            polygon = [(0, H)] + pts + [(W, H)]
            draw.polygon(polygon, fill=color)

        return img
