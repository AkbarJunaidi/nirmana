"""
organic_patterns.py
====================
Tiga teknik Nirmana Organik klasik DKV (lihat foto 3, kolom "ORGANIK"):

1. hatching_burst      -> kelompok bentuk spora/daun yang memancar dari satu
                           titik pangkal, tiap bentuk diisi titik-titik stipple.
2. concentric_cells     -> sel-sel lingkaran organik (wobble, tidak sempurna)
                           bersarang konsentris seperti serat kayu / pebble
                           mosaic, dipadatkan memenuhi kanvas (packing acak).
3. reaction_diffusion   -> pola percabangan organik otentik (Gray-Scott
                           reaction-diffusion, simulasi kimiawi nyata yang
                           menghasilkan motif seperti karang/kulit hewan),
                           di-mask ke bentuk blob agar sesuai referensi
                           (blob hitam berisi motif putih bercabang).
"""

import math
import random
import numpy as np
from PIL import Image, ImageDraw

from .precision import draw_precise_polyline, circle_points


class OrganicNirmanaGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.nprng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # 1. HATCHING BURST (spora / leaf radiate cluster)
    # ------------------------------------------------------------------
    def generate_hatching_burst(self, petal_count: int = None, supersample: int = 2,
                                 n_clusters: int = None) -> Image.Image:
        """Sekumpulan 'ledakan spora' tersebar MERATA memenuhi seluruh kanvas
        (full-bleed) dengan skala & rotasi bervariasi -- seperti serumpun
        tanaman/karang lebat, bukan beberapa tangkai kesepian yang
        menyisakan area kosong luas. Jumlah cluster & jangkauannya adaptif
        terhadap ukuran kanvas supaya kepadatan tetap konsisten di resolusi
        berapapun (dari thumbnail sampai cetak A3)."""
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        # Kepadatan adaptif: makin luas kanvas, makin banyak cluster --
        # supaya rasio isi:kosong tetap terjaga di semua ukuran/rasio.
        area_factor = (W * H) / (1000 * 1000)
        n_clusters = n_clusters or max(9, int(self.rng.uniform(10, 15) * math.sqrt(max(area_factor, 0.3))))
        placed: list = []

        # Grid penuh (bukan grid renggang) + jitter kuat, sehingga TIAP sel
        # grid pasti kebagian satu cluster -- menjamin tidak ada kuadran
        # kanvas yang kosong sama sekali seperti sebelumnya.
        grid_cols = max(3, math.ceil(math.sqrt(n_clusters * (W / H))))
        grid_rows = max(3, math.ceil(n_clusters / grid_cols))
        n_clusters = grid_cols * grid_rows
        cell_w, cell_h = W / grid_cols, H / grid_rows

        for row in range(grid_rows):
            for col in range(grid_cols):
                bx = (col + self.rng.uniform(0.22, 0.78)) * cell_w
                by = (row + self.rng.uniform(0.22, 0.78)) * cell_h
                scale = self.rng.uniform(0.75, 1.15)
                placed.append((bx, by, scale))

                n = petal_count or self.rng.randint(8, 14)
                spread = self.rng.uniform(math.pi * 0.7, math.pi * 1.4)
                overall_rot = self.rng.uniform(0, math.tau)
                start_angle = overall_rot - spread / 2

                # Jangkauan petal diikat ke ukuran SEL grid (bukan ke seluruh
                # kanvas) supaya tiap cluster proporsional mengisi wilayahnya
                # sendiri dan bertautan rapi dengan cluster tetangga, tanpa
                # menumpuk berantakan maupun menyisakan celah antar-cluster.
                max_len = min(cell_w, cell_h) * self.rng.uniform(0.62, 0.82) * scale

                for i in range(n):
                    t = i / max(1, n - 1)
                    angle = start_angle + t * spread + self.rng.uniform(-0.05, 0.05)
                    length = max_len * self.rng.uniform(0.55, 1.0)
                    width_petal = length * self.rng.uniform(0.14, 0.24)
                    self._draw_spore_petal(draw, bx, by, angle, length, width_petal, ss)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    def _draw_spore_petal(self, draw, base_x, base_y, angle, length, width_petal, ss):
        """Menggambar satu bentuk 'spora' (kapsul memanjang) berisi stipple dots
        dengan outline tinta, meniru gaya referensi organik radiate."""
        # Bangun outline kapsul (2 busur di ujung, garis lurus di sisi) via parametrik
        steps = 24
        pts_outline = []
        for k in range(steps + 1):
            u = k / steps  # 0..1 sepanjang badan kapsul
            # profil lebar: menyempit di pangkal & ujung (mirip biji)
            w_profile = math.sin(u * math.pi) ** 0.6
            half_w = (width_petal / 2) * w_profile
            along = u * length
            # koordinat lokal (sepanjang sumbu petal = x_local, tegak = y_local)
            x_local, y_local = along, half_w
            pts_outline.append(self._rotate(x_local, y_local, angle, base_x, base_y))
        for k in range(steps, -1, -1):
            u = k / steps
            w_profile = math.sin(u * math.pi) ** 0.6
            half_w = (width_petal / 2) * w_profile
            along = u * length
            x_local, y_local = along, -half_w
            pts_outline.append(self._rotate(x_local, y_local, angle, base_x, base_y))

        draw.polygon(pts_outline, outline=0, width=max(1, 2 * ss), fill=None)

        # Isi dengan stipple dots mengikuti profil kapsul (kepadatan lebih tinggi di tengah)
        n_dots = int((length * width_petal) / (28 * ss * ss)) + 12
        dot_r = max(1, int(1.6 * ss))
        for _ in range(n_dots):
            u = self.rng.betavariate(1.6, 1.6)
            w_profile = math.sin(u * math.pi) ** 0.6
            half_w = (width_petal / 2) * w_profile * self.rng.uniform(0.0, 0.92)
            side = self.rng.choice([-1, 1])
            along = u * length
            x_local, y_local = along, side * half_w
            px, py = self._rotate(x_local, y_local, angle, base_x, base_y)
            draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], fill=0)

    @staticmethod
    def _rotate(x, y, angle, ox, oy):
        ca, sa = math.cos(angle), math.sin(angle)
        return (ox + x * ca - y * sa, oy + x * sa + y * ca)

    # ------------------------------------------------------------------
    # 2. CONCENTRIC ORGANIC CELLS (serat kayu / pebble mosaic)
    # ------------------------------------------------------------------
    def generate_concentric_cells(self, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        cells = self._pack_circles(W, H, r_min=min(W, H) * 0.05, r_max=min(W, H) * 0.16, tries=600)

        for (cx, cy, r) in cells:
            self._draw_wobble_rings(draw, cx, cy, r, ss)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    def _pack_circles(self, W, H, r_min, r_max, tries=500):
        """Packing sederhana ala Poisson-disc: coba tempatkan lingkaran acak,
        terima jika tidak menumpuk berlebihan dengan yang sudah ada."""
        placed = []
        for _ in range(tries):
            r = self.rng.uniform(r_min, r_max)
            cx = self.rng.uniform(r, W - r)
            cy = self.rng.uniform(r, H - r)
            ok = True
            for (ex, ey, er) in placed:
                if math.hypot(cx - ex, cy - ey) < (r + er) * 0.62:
                    ok = False
                    break
            if ok:
                placed.append((cx, cy, r))
        return placed

    def _draw_wobble_rings(self, draw, cx, cy, r, ss):
        """Gambar cincin konsentris dengan tepi organik (noise sudut),
        bukan lingkaran sempurna, agar terasa hand-drawn / serat kayu."""
        n_rings = self.rng.randint(3, 6)
        # noise tetap (phase acak per sel) supaya semua ring dalam 1 sel selaras bentuknya
        wobble_freq = self.rng.uniform(3, 7)
        wobble_amp = r * self.rng.uniform(0.05, 0.13)
        phase = self.rng.uniform(0, math.tau)

        for ring_i in range(n_rings, 0, -1):
            ring_r = r * (ring_i / n_rings)
            # wobble_freq dibulatkan ke integer agar sin(0) == sin(tau*freq):
            # loop menutup persis tanpa jahitan, berapapun radiusnya.
            freq_int = max(3, round(wobble_freq))
            pts = circle_points(cx, cy, ring_r,
                                 wobble_amp=wobble_amp * (ring_i / n_rings),
                                 wobble_freq=freq_int, phase=phase)
            draw_precise_polyline(draw, pts, fill=0, width=max(1, int(1.4 * ss)), closed=True)
        # titik pusat kecil
        cr = max(1, int(1.6 * ss))
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=0)

    # ------------------------------------------------------------------
    # 3. REACTION-DIFFUSION INK BLOB (motif percabangan organik otentik)
    # ------------------------------------------------------------------
    def generate_reaction_diffusion_blob(self, sim_size: int = 170, n_particles: int = None, max_steps: int = 260) -> Image.Image:
        """Motif percabangan organik otentik via Diffusion-Limited Aggregation
        (DLA): partikel berjalan acak (random walk) dan menempel begitu
        menyentuh struktur yang sudah ada, menghasilkan pola dendritik /
        karang / kristal es -- fenomena fisik nyata di balik motif organik
        semacam ini, bukan noise yang dipalsukan.

        Blob dibuat mengikuti RASIO ASPEK kanvas asli (bukan grid n x n
        persegi lalu diregangkan) dan radiusnya nyaris menyentuh keempat
        tepi -- full-bleed sesuai bidang gambar, bukan satu motif kecil
        terisolasi di tengah kanvas kosong seperti sebelumnya. Jumlah
        partikel diskalakan otomatis terhadap luas area blob supaya
        kepadatan cabang tetap konsisten (tidak jadi encer) di ukuran
        kanvas berapapun.
        """
        # Grid simulasi mengikuti rasio aspek kanvas asli, sisi terpanjang
        # dipatok ke sim_size -- supaya blob organik memenuhi bidang gambar
        # persis (bukan lingkaran digepengkan tak wajar).
        if self.w >= self.h:
            sim_w = sim_size
            sim_h = max(60, round(sim_size * self.h / self.w))
        else:
            sim_h = sim_size
            sim_w = max(60, round(sim_size * self.w / self.h))

        mask = self._organic_blob_mask(sim_w, sim_h, r_frac=self.rng.uniform(0.45, 0.48))
        ys, xs = np.where(mask)
        if len(xs) == 0:
            return Image.new("RGB", (self.w, self.h), (0, 0, 0))
        mask_cells = list(zip(ys.tolist(), xs.tolist()))
        n_mask = len(mask_cells)

        # Kepadatan partikel diskalakan terhadap luas mask -- disetel supaya
        # cabang dendritik tetap terlihat renggang & "terbaca" strukturnya
        # (bukan jenuh jadi bidang solid berlubang-lubang kecil).
        n_particles = n_particles or int(n_mask * 0.30)

        grid = np.zeros((sim_h, sim_w), dtype=bool)
        cx, cy = int(xs.mean()), int(ys.mean())
        grid[cy, cx] = True
        # Titik nukleasi tersebar merata (grid kasar) di seluruh area blob,
        # supaya cabang tumbuh menjalar ke semua bagian -- bukan menumpuk
        # di satu-dua kelompok saja.
        spacing = max(10, min(sim_w, sim_h) // 9)
        for gy in range(0, sim_h, spacing):
            for gx in range(0, sim_w, spacing):
                if mask[gy, gx] and self.rng.random() < 0.6:
                    grid[gy, gx] = True

        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for _ in range(n_particles):
            y, x = mask_cells[self.rng.randrange(n_mask)]
            for _ in range(max_steps):
                stuck = False
                for dy, dx in offsets:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < sim_h and 0 <= nx < sim_w and grid[ny, nx]:
                        stuck = True
                        break
                if stuck:
                    grid[y, x] = True
                    break
                dy, dx = offsets[self.rng.randrange(8)]
                ny, nx = y + dy, x + dx
                if 0 <= ny < sim_h and 0 <= nx < sim_w and mask[ny, nx]:
                    y, x = ny, nx

        # Render: titik-titik yang menempel digambar sebagai lingkaran kecil
        # (bukan 1px) supaya cabangnya terlihat tegas & clean saat di-upscale.
        scale = 4
        big = Image.new("L", (sim_w * scale, sim_h * scale), 0)
        draw = ImageDraw.Draw(big)
        stuck_ys, stuck_xs = np.where(grid)
        dot_r = 2.0
        for yy, xx in zip(stuck_ys.tolist(), stuck_xs.tolist()):
            cxp, cyp = xx * scale + scale / 2, yy * scale + scale / 2
            draw.ellipse([cxp - dot_r * scale / 2, cyp - dot_r * scale / 2,
                          cxp + dot_r * scale / 2, cyp + dot_r * scale / 2], fill=255)

        img = big.resize((self.w, self.h), Image.LANCZOS).convert("RGB")

        # Blob organik/elips tidak pernah menjangkau SUDUT kanvas persegi
        # (hanya sisi tengahnya) -- 4-8 pecahan satelit kecil (mini-DLA)
        # disebar di zona sudut/tepi yang masih kosong supaya seluruh
        # bidang gambar tetap terasa terisi (full-bleed), bukan cuma satu
        # gumpalan di tengah dengan sudut-sudut kosong.
        canvas = img.convert("L")
        canvas_np = np.array(canvas)
        n_satellites = self.rng.randint(6, 10)
        for _ in range(n_satellites):
            frag = self._render_satellite_fragment()
            fw, fh = frag.size
            # Coba beberapa posisi, pilih yang benar-benar jatuh di area
            # KOSONG (gelap) kanvas -- supaya satelit terlihat mengisi
            # sudut/tepi yang bolong, bukan tertimbun di atas blob utama
            # yang sudah padat (jadi tak kelihatan).
            best_pos, best_brightness = None, 1e9
            for _try in range(10):
                edge_bias = self.rng.choice(["corner", "corner", "edge"])
                if edge_bias == "corner":
                    cx0 = self.rng.choice([0, self.w - fw])
                    cy0 = self.rng.choice([0, self.h - fh])
                else:
                    cx0 = self.rng.randint(0, max(1, self.w - fw))
                    cy0 = self.rng.randint(0, max(1, self.h - fh))
                cx0, cy0 = max(0, min(cx0, self.w - fw)), max(0, min(cy0, self.h - fh))
                region = canvas_np[cy0:cy0 + fh, cx0:cx0 + fw]
                brightness = region.mean() if region.size else 1e9
                if brightness < best_brightness:
                    best_brightness, best_pos = brightness, (cx0, cy0)
                if brightness < 4:  # sudah cukup gelap/kosong, langsung pakai
                    break
            if best_pos is not None:
                canvas.paste(frag, best_pos, frag)
                canvas_np = np.array(canvas)

        return canvas.convert("RGB")

    def _render_satellite_fragment(self):
        """Pecahan dendritik kecil (mini-DLA) untuk mengisi sudut/tepi
        kanvas yang tak terjangkau blob utama -- skala & kepadatan lebih
        kecil, gaya tetap konsisten (bagian dari 'karang' yang sama)."""
        n = self.rng.randint(30, 46)
        mask = np.ones((n, n), dtype=bool)
        grid = np.zeros((n, n), dtype=bool)
        grid[n // 2, n // 2] = True
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        n_particles = int(n * n * 0.22)
        for _ in range(n_particles):
            y, x = self.rng.randrange(n), self.rng.randrange(n)
            for _ in range(80):
                stuck = False
                for dy, dx in offsets:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < n and 0 <= nx < n and grid[ny, nx]:
                        stuck = True
                        break
                if stuck:
                    grid[y, x] = True
                    break
                dy, dx = offsets[self.rng.randrange(8)]
                ny, nx = y + dy, x + dx
                if 0 <= ny < n and 0 <= nx < n:
                    y, x = ny, nx
        scale = 4
        big = Image.new("L", (n * scale, n * scale), 0)
        draw = ImageDraw.Draw(big)
        ys, xs = np.where(grid)
        for yy, xx in zip(ys.tolist(), xs.tolist()):
            cxp, cyp = xx * scale + scale / 2, yy * scale + scale / 2
            draw.ellipse([cxp - scale, cyp - scale, cxp + scale, cyp + scale], fill=255)
        target = self.rng.randint(int(min(self.w, self.h) * 0.09), int(min(self.w, self.h) * 0.16))
        return big.resize((target, target), Image.LANCZOS)

    def _organic_blob_mask(self, sim_w: int, sim_h: int, r_frac: float = 0.4) -> np.ndarray:
        """Membuat mask blob organik (bentuk amoeba) via superformula-ish
        radial noise mengikuti rasio aspek (sim_w x sim_h) -- radiusnya
        independen per sumbu x/y supaya blob mendekati keempat tepi bidang
        gambar rasio berapapun (bukan lingkaran yang digepengkan tak wajar
        saat kanvasnya persegi-panjang)."""
        cx, cy = sim_w / 2, sim_h / 2
        base_rx = sim_w * r_frac
        base_ry = sim_h * r_frac
        n_harm = self.rng.randint(3, 6)
        phases = [self.rng.uniform(0, math.tau) for _ in range(n_harm)]
        amps = [self.rng.uniform(0.06, 0.16) / (i + 1) for i in range(n_harm)]

        ys, xs = np.mgrid[0:sim_h, 0:sim_w]
        dx = xs - cx
        dy = ys - cy
        theta = np.arctan2(dy, dx)

        r_boundary_x = np.full_like(theta, base_rx)
        r_boundary_y = np.full_like(theta, base_ry)
        for h in range(n_harm):
            wobble = amps[h] * np.sin((h + 2) * theta + phases[h])
            r_boundary_x = r_boundary_x + base_rx * wobble
            r_boundary_y = r_boundary_y + base_ry * wobble

        # Persamaan elips ternormalisasi (x/rx)^2 + (y/ry)^2 < 1
        return (dx / np.maximum(r_boundary_x, 1e-6)) ** 2 + (dy / np.maximum(r_boundary_y, 1e-6)) ** 2 < 1
