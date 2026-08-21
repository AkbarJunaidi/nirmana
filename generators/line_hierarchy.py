"""
line_hierarchy.py
===================
Nirmana Garis Tebal-Tipis (Line Weight Hierarchy) -- tugas paling klasik
di studio DKV untuk mengetes "jam terbang mata" seorang desainer: apakah ia
bisa membangun VALUE (gelap-terang) dan RITME semata-mata dari tebal-tipis
garis dan jarak antar-garis -- tanpa bidang isi, tanpa tekstur, tanpa objek.
Yang dinilai dosen/art director dari tugas semacam ini:

  1. Skala ketebalan  -- apakah tangga tebal-tipisnya konsisten & bertahap
     rapi (bukan cuma "tipis" vs "tebal" tapi ada gradasi jelas), dan
     apakah kontras ekstrem (rambut vs tebal) dipakai secara sengaja.
  2. Presisi spasi     -- jarak antar-garis pada satu keluarga (family)
     harus konsisten secara matematis, bukan kira-kira -- mata terlatih
     langsung menangkap spasi yang goyah.
  3. Kontrol lengkung  -- begitu garis dibengkokkan jadi busur/lingkaran,
     ketebalannya harus tetap presisi tersambung di sepanjang lengkungan,
     tidak boleh menciut/melebar tak sengaja atau patah di sambungan.
  4. Keseimbangan komposisi -- densitas garis membentuk area terang/gelap
     yang menyeimbangkan bidang (prinsip figure-ground nirmana).

Karena presisi adalah INTI dari teknik ini, semua elemen kurva/lingkaran di
sini digambar lewat `precision.draw_precise_polyline` (sambungan dijamin
mulus, sesuai `precision.circle_points` yang sample rate-nya adaptif
terhadap radius) -- bukan pendekatan polyline mentah yang rawan bercelah.

Tiga varian:
1. parallel_families -> beberapa "keluarga" garis sejajar (sudut berbeda
   per keluarga) dengan tangga ketebalan bertahap (mis. 6 tingkat, dari
   rambut 1px sampai tebal), spasi presisi konsisten per keluarga.
2. concentric_taper   -> cincin-cincin konsentris presisi dengan ketebalan
   yang meruncing (taper) dari pusat ke tepi (atau sebaliknya) -- showcase
   langsung dari jaminan "garis pada lingkaran tetap nyambung, tak peduli
   setipis atau setebal apa".
3. radial_taper       -> jari-jari (spokes) dari titik pusat dengan
   ketebalan meruncing terhadap jarak, disilang beberapa busur konsentris
   tipis -- melatih presisi perpotongan garis lurus x lengkung.
"""

import math
import random
from typing import List, Tuple

from PIL import Image, ImageDraw

from .precision import draw_precise_polyline, circle_points
from .svg_export import SVGCanvas


class LineHierarchyGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # Skala ketebalan bertahap (tangga geometris, bukan linear -- kontras
    # antar-tingkat jadi lebih tegas & "terbaca" mata, khas skala tipografi)
    # ------------------------------------------------------------------
    def _weight_scale(self, n_steps: int, min_w: float, max_w: float, ss: int) -> List[float]:
        ratio = (max_w / min_w) ** (1 / max(1, n_steps - 1))
        return [min_w * (ratio ** i) * ss for i in range(n_steps)]

    # ------------------------------------------------------------------
    # 1. PARALLEL FAMILIES -- keluarga garis sejajar, tangga tebal-tipis
    # ------------------------------------------------------------------
    def generate_parallel_families(self, n_families: int = None,
                                    n_steps: int = 6, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("RGB", (W, H), (252, 251, 248))
        draw = ImageDraw.Draw(img)

        n_families = n_families or self.rng.randint(3, 5)
        weights = self._weight_scale(n_steps, 0.8, 9.0, ss)

        # Tiap keluarga dikunci ke satu ZONA KOLOM kanvas dan sudut nyaris
        # tegak (tilt kecil) supaya garis tidak menyimpang jauh ke kolom
        # tetangga -- hierarki tebal-tipis tiap keluarga jadi tetap terbaca
        # jelas terpisah, bukan lebur jadi anyaman kacau lintas-keluarga.
        band_w = W / n_families
        half_len = H * 0.6
        for fi in range(n_families):
            angle = self.rng.uniform(-0.06, 0.06)  # tilt halus, bukan diagonal ekstrem
            reverse = self.rng.choice([True, False])
            steps_here = weights if not reverse else list(reversed(weights))

            x0 = fi * band_w
            # spasi presisi: dihitung eksak supaya n garis pas memenuhi band,
            # bukan idekuran -- inilah yang diuji dari "presisi memilih jarak"
            n_lines = len(steps_here) * self.rng.randint(3, 5)
            spacing = band_w / n_lines
            ca, sa = math.cos(angle), math.sin(angle)

            for li in range(n_lines):
                w_idx = li % len(steps_here)
                lw = max(1, int(round(steps_here[w_idx])))
                cx = x0 + (li + 0.5) * spacing
                p0 = (cx - half_len * sa, H / 2 - half_len * ca)
                p1 = (cx + half_len * sa, H / 2 + half_len * ca)
                gray = 15 + int(10 * (w_idx / max(1, len(steps_here) - 1)))
                draw_precise_polyline(draw, [p0, p1], (gray, gray, gray), lw)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ------------------------------------------------------------------
    # 2. CONCENTRIC TAPER -- cincin presisi, tebal meruncing radial
    # ------------------------------------------------------------------
    def generate_concentric_taper(self, n_rings: int = None, supersample: int = 2,
                                   taper_out: bool = None) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("RGB", (W, H), (252, 251, 248))
        draw = ImageDraw.Draw(img)

        cx, cy = W * self.rng.uniform(0.42, 0.58), H * self.rng.uniform(0.42, 0.58)
        max_r = math.hypot(W, H) * 0.5 * self.rng.uniform(0.72, 0.9)
        n_rings = n_rings or self.rng.randint(26, 40)
        taper_out = self.rng.choice([True, False]) if taper_out is None else taper_out
        min_w, max_w = 0.7 * ss, 8.5 * ss

        # Spasi radial presisi non-linear: rapat di satu ujung, renggang di
        # ujung lain -- ini sengaja MENGIKUTI ketebalan (garis tebal butuh
        # napas/spasi lebih lebar supaya tidak dempet jadi bidang solid).
        for i in range(n_rings):
            t = i / max(1, n_rings - 1)  # 0 pusat -> 1 tepi
            r = max_r * (t ** 1.35)
            w_t = t if taper_out else (1 - t)
            lw = max(1, int(round(min_w + (max_w - min_w) * w_t)))
            shade = int(20 + 90 * (1 - w_t))
            pts = circle_points(cx, cy, r)
            draw_precise_polyline(draw, pts, (shade, shade, shade), lw, closed=True)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ------------------------------------------------------------------
    # 3. RADIAL TAPER -- jari-jari meruncing x busur tipis penyilang
    # ------------------------------------------------------------------
    def generate_radial_taper(self, n_spokes: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("RGB", (W, H), (252, 251, 248))
        draw = ImageDraw.Draw(img)

        cx, cy = W / 2, H / 2
        max_r = math.hypot(W, H) * 0.5 * 0.92
        n_spokes = n_spokes or self.rng.choice([18, 24, 32, 36])
        min_w, max_w = 0.7 * ss, 10.0 * ss

        # Jari-jari: tebal di pusat (tekanan visual), meruncing presisi ke
        # tepi -- digambar sebagai DUA segmen supaya taper terlihat jelas
        # (bukan satu lebar konstan), sambungan tengah tetap dijamin rapat.
        for k in range(n_spokes):
            a = (k / n_spokes) * math.tau + self.rng.uniform(-0.01, 0.01)
            x1, y1 = cx + max_r * math.cos(a), cy + max_r * math.sin(a)
            mid_t = self.rng.uniform(0.35, 0.55)
            xm, ym = cx + max_r * mid_t * math.cos(a), cy + max_r * mid_t * math.sin(a)
            w_inner = max(1, int(round(max_w * self.rng.uniform(0.85, 1.0))))
            w_outer = max(1, int(round(min_w)))
            draw_precise_polyline(draw, [(cx, cy), (xm, ym)], (18, 18, 18), w_inner)
            draw_precise_polyline(draw, [(xm, ym), (x1, y1)], (18, 18, 18), w_outer)

        # Busur-busur tipis penyilang (uji presisi perpotongan lurus x lengkung)
        n_arcs = self.rng.randint(4, 7)
        for ai in range(1, n_arcs + 1):
            r = max_r * (ai / (n_arcs + 1))
            pts = circle_points(cx, cy, r)
            draw_precise_polyline(draw, pts, (150, 150, 150), max(1, ss), closed=True)

        core_r = max_r * 0.02
        draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(18, 18, 18))

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img

    # ==================================================================
    # VERSI SVG (vektor murni) -- paritas komposisi persis dengan versi
    # raster di atas untuk seed yang sama (rng lokal fresh dari self.seed,
    # urutan pemanggilan random disamakan persis), tapi digambar sebagai
    # elemen <circle>/<polyline> SVG asli: presisi matematis sempurna di
    # skala berapapun, tanpa supersample & tanpa trik anti-patahan manual
    # (renderer vektor menangani sambungan mulus secara native).
    # ==================================================================

    def generate_parallel_families_svg(self, n_families: int = None, n_steps: int = 6) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#fcfbf8")

        n_families = n_families or rng.randint(3, 5)
        weights = self._weight_scale(n_steps, 0.8, 9.0, 1)

        band_w = W / n_families
        half_len = H * 0.6
        for fi in range(n_families):
            angle = rng.uniform(-0.06, 0.06)
            reverse = rng.choice([True, False])
            steps_here = weights if not reverse else list(reversed(weights))

            x0 = fi * band_w
            n_lines = len(steps_here) * rng.randint(3, 5)
            spacing = band_w / n_lines
            ca, sa = math.cos(angle), math.sin(angle)

            for li in range(n_lines):
                w_idx = li % len(steps_here)
                lw = steps_here[w_idx]
                cx = x0 + (li + 0.5) * spacing
                p0 = (cx - half_len * sa, H / 2 - half_len * ca)
                p1 = (cx + half_len * sa, H / 2 + half_len * ca)
                gray = 15 + int(10 * (w_idx / max(1, len(steps_here) - 1)))
                svg.polyline([p0, p1], stroke=f"#{gray:02x}{gray:02x}{gray:02x}", width=lw)

        return svg.to_string()

    def generate_concentric_taper_svg(self, n_rings: int = None, taper_out: bool = None) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#fcfbf8")

        cx, cy = W * rng.uniform(0.42, 0.58), H * rng.uniform(0.42, 0.58)
        max_r = math.hypot(W, H) * 0.5 * rng.uniform(0.72, 0.9)
        n_rings = n_rings or rng.randint(26, 40)
        taper_out = rng.choice([True, False]) if taper_out is None else taper_out
        min_w, max_w = 0.7, 8.5

        for i in range(n_rings):
            t = i / max(1, n_rings - 1)
            r = max_r * (t ** 1.35)
            w_t = t if taper_out else (1 - t)
            lw = min_w + (max_w - min_w) * w_t
            shade = int(20 + 90 * (1 - w_t))
            svg.circle(cx, cy, r, stroke=f"#{shade:02x}{shade:02x}{shade:02x}", width=lw)

        return svg.to_string()

    def generate_radial_taper_svg(self, n_spokes: int = None) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#fcfbf8")

        cx, cy = W / 2, H / 2
        max_r = math.hypot(W, H) * 0.5 * 0.92
        n_spokes = n_spokes or rng.choice([18, 24, 32, 36])
        min_w, max_w = 0.7, 10.0

        for k in range(n_spokes):
            a = (k / n_spokes) * math.tau + rng.uniform(-0.01, 0.01)
            x1, y1 = cx + max_r * math.cos(a), cy + max_r * math.sin(a)
            mid_t = rng.uniform(0.35, 0.55)
            xm, ym = cx + max_r * mid_t * math.cos(a), cy + max_r * mid_t * math.sin(a)
            w_inner = max_w * rng.uniform(0.85, 1.0)
            w_outer = min_w
            svg.polyline([(cx, cy), (xm, ym)], stroke="#121212", width=w_inner)
            svg.polyline([(xm, ym), (x1, y1)], stroke="#121212", width=w_outer)

        n_arcs = rng.randint(4, 7)
        for ai in range(1, n_arcs + 1):
            r = max_r * (ai / (n_arcs + 1))
            svg.circle(cx, cy, r, stroke="#969696", width=1.0)

        core_r = max_r * 0.02
        svg.circle(cx, cy, core_r, fill="#121212")

        return svg.to_string()
