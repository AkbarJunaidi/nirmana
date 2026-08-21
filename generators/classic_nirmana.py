"""
classic_nirmana.py
====================
Empat tugas nirmana paling dasar & klasik di kurikulum DKV semester awal,
yang sebelumnya belum ada di sistem ini (yang sudah ada lebih condong ke
eksplorasi garis/tekstur/ilusi kedalaman tingkat lanjut). Modul ini
melengkapi fondasinya:

1. NIRMANA BIDANG (Figure-Ground) -- komposisi murni dari hubungan bidang
   positif-negatif TANPA garis sama sekali. Mengetes kepekaan bahwa ruang
   kosong (ground) adalah elemen desain yang sama pentingnya dengan bentuk
   berisi (figure). Dibangun lewat teknik klasik "overlap bidang transparan
   ber-XOR": tiap bidang baru yang tumpang tindih dengan bidang sebelumnya
   MEMBALIK warnanya -- persis seperti menumpuk lembar kalkir tembus
   pandang, menghasilkan bentuk-bentuk baru dari pertemuan bidang lama
   yang tak pernah digambar eksplisit (ambiguitas figure-ground otentik).

2. NIRMANA KONTRAS VALUE (9-Value Grid) -- grid presisi berisi 9 tingkat
   value abu-abu (dari putih murni sampai hitam murni, terbagi rata),
   disusun sehingga TIDAK ADA dua sel bertetangga langsung dengan value
   sama. Ini melatih kalibrasi mata terhadap tangga tonal yang presisi,
   sekaligus dasar sebelum belajar shading/rendering.

3. NIRMANA IRAMA (Rhythm) -- tiga jenis irama visual klasik, masing-masing
   sub-teknik terpisah supaya bisa dipelajari satu-satu:
   - Repetitif : elemen identik pada interval/ukuran/rotasi tetap.
   - Progresif : elemen berubah bertahap (ukuran/rotasi) menyusuri baris.
   - Oposisi   : dua motif berselang-seling membentuk pola "ketukan".

4. NIRMANA KESEIMBANGAN ASIMETRIS -- satu massa visual besar & tegas di
   satu sisi, diimbangi beberapa elemen kecil di sisi berlawanan yang
   ditempatkan JAUH dari pusat (prinsip tuas/lever: massa kecil x jarak
   jauh = massa besar x jarak dekat). Bukan cuma "kelihatan seimbang" --
   titik berat visual (dihitung dari sebaran tinta hitam secara aktual di
   piksel) benar-benar dikoreksi secara algoritmik mendekati pusat kanvas.
"""

import math
import random
import numpy as np
from PIL import Image, ImageDraw

from .svg_export import SVGCanvas


class ClassicNirmanaGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # Utilitas bersama
    # ------------------------------------------------------------------
    def _rot_rect(self, cx, cy, hw, hh, angle):
        ca, sa = math.cos(angle), math.sin(angle)
        pts = []
        for (sx, sy) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            lx, ly = sx * hw, sy * hh
            pts.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
        return pts

    def _stamp_shape(self, draw, cx, cy, size, angle, shape, color=0):
        """Satu elemen bidang solid (bukan outline) -- dipakai di teknik
        irama & keseimbangan. Karena selalu FILL (bukan stroke bertepi
        tipis), tidak berisiko patahan seperti outline width>1."""
        if shape == "circle":
            r = size / 2
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        elif shape == "square":
            pts = self._rot_rect(cx, cy, size / 2, size / 2, angle)
            draw.polygon(pts, fill=color)
        elif shape == "triangle":
            r = size / 2
            pts = [(cx + r * math.cos(angle + k * math.tau / 3),
                     cy + r * math.sin(angle + k * math.tau / 3)) for k in range(3)]
            draw.polygon(pts, fill=color)
        else:  # "bar" -- dash tebal, dipakai varian repetitif
            pts = self._rot_rect(cx, cy, size / 2, size * 0.16, angle)
            draw.polygon(pts, fill=color)

    def _partition(self, n: int, rng: random.Random = None) -> list:
        """n pecahan acak positif berjumlah 1 -- dipakai untuk grid dengan
        ukuran sel bervariasi (gaya Mondrian) tapi tetap grid orthogonal
        penuh (full-bleed otomatis karena partisi selalu menutup 0..1).
        rng opsional supaya versi SVG bisa memakai rng lokal terpisah
        (paritas komposisi persis dengan versi raster untuk seed sama)."""
        rng = rng or self.rng
        raw = [rng.uniform(0.6, 1.7) for _ in range(n)]
        s = sum(raw)
        return [x / s for x in raw]

    def _shape_area(self, size: float, shape: str) -> float:
        """Luas analitik tiap bentuk (bukan hasil hitung piksel) -- dipakai
        versi SVG dari Keseimbangan Asimetris untuk menghitung titik berat
        SECARA MATEMATIS EKSAK, bukan aproksimasi rasterisasi. Ini bahkan
        lebih presisi daripada versi raster yang menjumlahkan piksel."""
        if shape == "circle":
            r = size / 2
            return math.pi * r * r
        elif shape == "square":
            return size * size
        elif shape == "triangle":
            r = size / 2
            return (3 * math.sqrt(3) / 4) * r * r
        else:  # "bar"
            return size * (size * 0.32)

    def _stamp_shape_svg(self, svg: SVGCanvas, cx, cy, size, angle, shape, fill="#000000") -> None:
        """Padanan SVG dari `_stamp_shape` -- geometri identik (lewat
        `_rot_rect` yang sama), cuma dituliskan sebagai elemen vektor."""
        if shape == "circle":
            svg.circle(cx, cy, size / 2, fill=fill)
        elif shape == "square":
            svg.polygon(self._rot_rect(cx, cy, size / 2, size / 2, angle), fill=fill)
        elif shape == "triangle":
            r = size / 2
            pts = [(cx + r * math.cos(angle + k * math.tau / 3),
                     cy + r * math.sin(angle + k * math.tau / 3)) for k in range(3)]
            svg.polygon(pts, fill=fill)
        else:  # "bar"
            svg.polygon(self._rot_rect(cx, cy, size / 2, size * 0.16, angle), fill=fill)

    # ==================================================================
    # 1. NIRMANA BIDANG (Figure-Ground via overlap XOR)
    # ==================================================================
    def generate_figure_ground(self, n_shapes: int = None, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        mask = np.zeros((H, W), dtype=bool)
        diag = math.hypot(W, H)

        # Bidang besar & tegas (bukan banyak bidang kecil) -- prinsip
        # nirmana bidang klasik: sedikit bentuk BESAR lebih kuat daripada
        # banyak bentuk kecil. Ukuran & posisi sengaja melampaui tepi
        # kanvas (bleed) supaya full-page terjamin tanpa perlu tambalan.
        n_shapes = n_shapes or self.rng.randint(5, 8)
        for _ in range(n_shapes):
            shape_type = self.rng.choice(["circle", "rect", "triangle"])
            size = diag * self.rng.uniform(0.30, 0.58)
            cx = self.rng.uniform(W * 0.05, W * 0.95)
            cy = self.rng.uniform(H * 0.05, H * 0.95)
            angle = self.rng.uniform(0, math.tau)

            temp = Image.new("L", (W, H), 0)
            td = ImageDraw.Draw(temp)
            if shape_type == "circle":
                r = size / 2
                td.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
            elif shape_type == "rect":
                hw, hh = size / 2, size * self.rng.uniform(0.35, 0.9) / 2
                td.polygon(self._rot_rect(cx, cy, hw, hh, angle), fill=255)
            else:
                r = size / 2
                pts = [(cx + r * math.cos(angle + k * math.tau / 3),
                         cy + r * math.sin(angle + k * math.tau / 3)) for k in range(3)]
                td.polygon(pts, fill=255)

            # XOR: area yang tumpang tindih dengan bidang sebelumnya
            # BERBALIK warna -- inilah yang menghasilkan bentuk baru "tak
            # sengaja" di pertemuan dua bidang, ciri khas nirmana
            # figure-ground otentik (bukan cuma tumpuk-tindih fill biasa).
            mask ^= (np.array(temp) > 127)

        gray = np.where(mask, 0, 255).astype(np.uint8)
        img = Image.fromarray(gray, mode="L")
        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ==================================================================
    # 2. NIRMANA KONTRAS VALUE (Grid 9 Tingkat, tak ada tetangga sama)
    # ==================================================================
    def generate_value_grid(self, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        n_cols = self.rng.randint(5, 7)
        n_rows = self.rng.randint(5, 7)
        col_fracs = self._partition(n_cols)
        row_fracs = self._partition(n_rows)
        xs = [0.0]
        for f in col_fracs:
            xs.append(xs[-1] + f)
        ys = [0.0]
        for f in row_fracs:
            ys.append(ys[-1] + f)
        xs = [x * W for x in xs]
        ys = [y * H for y in ys]

        # 9 tingkat value presisi, terbagi rata & eksak dari 0 s/d 255
        values = [round(i * 255 / 8) for i in range(9)]

        grid_vals = [[None] * n_cols for _ in range(n_rows)]
        for r in range(n_rows):
            for c in range(n_cols):
                candidates = list(values)
                self.rng.shuffle(candidates)
                neighbor_vals = set()
                if c > 0:
                    neighbor_vals.add(grid_vals[r][c - 1])
                if r > 0:
                    neighbor_vals.add(grid_vals[r - 1][c])
                chosen = next((v for v in candidates if v not in neighbor_vals), candidates[0])
                grid_vals[r][c] = chosen
                draw.rectangle([xs[c], ys[r], xs[c + 1], ys[r + 1]], fill=chosen)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ==================================================================
    # 3a. IRAMA REPETITIF -- elemen identik, interval & ukuran presisi tetap
    # ==================================================================
    def generate_rhythm_repetition(self, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        shape = self.rng.choice(["circle", "square", "triangle", "bar"])
        n_cols = self.rng.randint(8, 13)
        cell = W / n_cols
        n_rows = max(1, round(H / cell))
        cell_h = H / n_rows
        size = min(cell, cell_h) * self.rng.uniform(0.5, 0.66)
        angle = self.rng.uniform(0, math.tau)
        stagger = self.rng.choice([True, False])

        for r in range(n_rows):
            for c in range(n_cols):
                cx = (c + 0.5) * cell + (cell / 2 if stagger and r % 2 == 1 else 0)
                cy = (r + 0.5) * cell_h
                self._stamp_shape(draw, cx, cy, size, angle, shape)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ==================================================================
    # 3b. IRAMA PROGRESIF -- ukuran/rotasi berubah bertahap menyusuri baris
    # ==================================================================
    def generate_rhythm_progression(self, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        shape = self.rng.choice(["circle", "square", "triangle"])
        n_rows = self.rng.randint(5, 8)
        row_h = H / n_rows

        for r in range(n_rows):
            cy_base = (r + 0.5) * row_h
            n_elems = self.rng.randint(9, 15)
            reverse = self.rng.choice([True, False])
            wave_amp = row_h * self.rng.uniform(0.0, 0.18)
            rot_sweep = self.rng.uniform(0, math.pi * 1.6)
            for i in range(n_elems):
                t = i / max(1, n_elems - 1)
                tt = (1 - t) if reverse else t
                size = row_h * (0.16 + 0.66 * tt)
                cx = (i + 0.5) * (W / n_elems)
                cy = cy_base + math.sin(t * math.pi) * wave_amp
                angle = t * rot_sweep
                self._stamp_shape(draw, cx, cy, size, angle, shape)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ==================================================================
    # 3c. IRAMA OPOSISI -- dua motif berselang-seling, pola "ketukan"
    # ==================================================================
    def generate_rhythm_transition(self, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        shapes_pair = self.rng.sample(["circle", "square", "triangle", "bar"], 2)
        n_rows = self.rng.randint(5, 8)
        row_h = H / n_rows

        for r in range(n_rows):
            cy = (r + 0.5) * row_h
            n_elems = self.rng.randint(10, 17)
            base_size = row_h * self.rng.uniform(0.5, 0.66)
            pattern_len = self.rng.choice([2, 2, 3])  # AB atau AAB
            row_angle = self.rng.uniform(0, math.tau)
            for i in range(n_elems):
                cx = (i + 0.5) * (W / n_elems)
                is_accent = (i % pattern_len == 0)
                shape = shapes_pair[0] if is_accent else shapes_pair[1]
                size_mult = 1.0 if is_accent else 0.6
                self._stamp_shape(draw, cx, cy, base_size * size_mult, row_angle, shape)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ==================================================================
    # 4. NIRMANA KESEIMBANGAN ASIMETRIS (torsi visual dikoreksi algoritmik)
    # ==================================================================
    def generate_asymmetric_balance(self, supersample: int = 2) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss
        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)
        cxc, cyc = W / 2, H / 2

        # Satu massa visual besar & tegas dekat pusat, condong ke satu sisi.
        big_size = min(W, H) * self.rng.uniform(0.30, 0.40)
        side = self.rng.choice([-1, 1])
        big_x = cxc + side * W * self.rng.uniform(0.16, 0.26)
        big_y = cyc + self.rng.uniform(-H * 0.1, H * 0.1)
        big_shape = self.rng.choice(["circle", "square", "triangle"])
        self._stamp_shape(draw, big_x, big_y, big_size, self.rng.uniform(0, math.tau), big_shape)

        # Beberapa elemen kecil pendukung tersebar acak (belum tentu
        # menyeimbangkan sempurna -- akan dikoreksi lewat perhitungan
        # titik berat aktual di bawah).
        n_small = self.rng.randint(2, 4)
        for _ in range(n_small):
            s = min(W, H) * self.rng.uniform(0.04, 0.09)
            x = cxc + self.rng.uniform(-W * 0.36, W * 0.36)
            y = cyc + self.rng.uniform(-H * 0.4, H * 0.4)
            shape = self.rng.choice(["circle", "square", "triangle"])
            self._stamp_shape(draw, x, y, s, self.rng.uniform(0, math.tau), shape)

        # Hitung titik berat visual AKTUAL dari piksel yang sudah digambar
        # (bobot = tingkat kegelapan tinta) -- bukan tebakan geometris,
        # betul-betul diukur dari hasil render.
        arr = 255.0 - np.asarray(img, dtype=np.float32)
        total = arr.sum()
        if total > 0:
            ys_idx, xs_idx = np.mgrid[0:H, 0:W]
            cx_mass = float((arr * xs_idx).sum() / total)
            cy_mass = float((arr * ys_idx).sum() / total)
        else:
            cx_mass, cy_mass = cxc, cyc

        dx, dy = cx_mass - cxc, cy_mass - cyc
        imbalance = math.hypot(dx, dy)

        # Prinsip tuas: massa kecil DITEMPATKAN JAUH dari pusat di sisi
        # BERLAWANAN dari arah titik berat, supaya (massa x jarak) di
        # kedua sisi saling mendekati setara -- inilah "keseimbangan
        # asimetris" yang sesungguhnya, bukan cuma kesan visual kasar.
        if imbalance > min(W, H) * 0.01:
            ux, uy = -dx / imbalance, -dy / imbalance
            n_correction = self.rng.randint(2, 3)
            for k in range(n_correction):
                dist = min(W, H) * self.rng.uniform(0.36, 0.47)
                s = min(W, H) * self.rng.uniform(0.055, 0.12)
                x = cxc + ux * dist + self.rng.uniform(-W * 0.05, W * 0.05)
                y = cyc + uy * dist + self.rng.uniform(-H * 0.05, H * 0.05)
                x = max(s, min(W - s, x))
                y = max(s, min(H - s, y))
                shape = self.rng.choice(["circle", "square", "triangle"])
                self._stamp_shape(draw, x, y, s, self.rng.uniform(0, math.tau), shape)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")

    # ==================================================================
    # VERSI SVG (vektor murni) -- paritas komposisi persis dengan versi
    # raster untuk seed yang sama (rng lokal fresh dari self.seed, urutan
    # pemanggilan random disamakan persis dengan versi raster di atas).
    # ==================================================================

    def generate_figure_ground_svg(self, n_shapes: int = None) -> str:
        """XOR raster diganti fill-rule="evenodd" pada SATU <path> gabungan
        -- padanan vektor EKSAK (bukan aproksimasi): area yang tertutup
        jumlah ganjil sub-path terisi, genap kosong, prinsip identik XOR
        tapi presisi matematis sempurna di tepi bentuk."""
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        diag = math.hypot(W, H)
        n_shapes = n_shapes or rng.randint(5, 8)

        shapes = []
        for _ in range(n_shapes):
            shape_type = rng.choice(["circle", "rect", "triangle"])
            size = diag * rng.uniform(0.30, 0.58)
            cx = rng.uniform(W * 0.05, W * 0.95)
            cy = rng.uniform(H * 0.05, H * 0.95)
            angle = rng.uniform(0, math.tau)
            if shape_type == "circle":
                shapes.append({"type": "circle", "cx": cx, "cy": cy, "r": size / 2})
            elif shape_type == "rect":
                hw, hh = size / 2, size * rng.uniform(0.35, 0.9) / 2
                shapes.append({"type": "polygon", "pts": self._rot_rect(cx, cy, hw, hh, angle)})
            else:
                r = size / 2
                pts = [(cx + r * math.cos(angle + k * math.tau / 3),
                         cy + r * math.sin(angle + k * math.tau / 3)) for k in range(3)]
                shapes.append({"type": "polygon", "pts": pts})

        svg = SVGCanvas(W, H, background="#ffffff")
        svg.path_evenodd(shapes, fill="#000000")
        return svg.to_string()

    def generate_value_grid_svg(self) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background=None)  # grid selalu menutup penuh, bg tak perlu

        n_cols = rng.randint(5, 7)
        n_rows = rng.randint(5, 7)
        col_fracs = self._partition(n_cols, rng=rng)
        row_fracs = self._partition(n_rows, rng=rng)
        xs = [0.0]
        for f in col_fracs:
            xs.append(xs[-1] + f)
        ys = [0.0]
        for f in row_fracs:
            ys.append(ys[-1] + f)
        xs = [x * W for x in xs]
        ys = [y * H for y in ys]

        values = [round(i * 255 / 8) for i in range(9)]
        grid_vals = [[None] * n_cols for _ in range(n_rows)]
        for r in range(n_rows):
            for c in range(n_cols):
                candidates = list(values)
                rng.shuffle(candidates)
                neighbor_vals = set()
                if c > 0:
                    neighbor_vals.add(grid_vals[r][c - 1])
                if r > 0:
                    neighbor_vals.add(grid_vals[r - 1][c])
                chosen = next((v for v in candidates if v not in neighbor_vals), candidates[0])
                grid_vals[r][c] = chosen
                svg.rect(xs[c], ys[r], xs[c + 1] - xs[c], ys[r + 1] - ys[r],
                          fill=f"#{chosen:02x}{chosen:02x}{chosen:02x}")

        return svg.to_string()

    def generate_rhythm_repetition_svg(self) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#ffffff")

        shape = rng.choice(["circle", "square", "triangle", "bar"])
        n_cols = rng.randint(8, 13)
        cell = W / n_cols
        n_rows = max(1, round(H / cell))
        cell_h = H / n_rows
        size = min(cell, cell_h) * rng.uniform(0.5, 0.66)
        angle = rng.uniform(0, math.tau)
        stagger = rng.choice([True, False])

        for r in range(n_rows):
            for c in range(n_cols):
                cx = (c + 0.5) * cell + (cell / 2 if stagger and r % 2 == 1 else 0)
                cy = (r + 0.5) * cell_h
                self._stamp_shape_svg(svg, cx, cy, size, angle, shape)

        return svg.to_string()

    def generate_rhythm_progression_svg(self) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#ffffff")

        shape = rng.choice(["circle", "square", "triangle"])
        n_rows = rng.randint(5, 8)
        row_h = H / n_rows

        for r in range(n_rows):
            cy_base = (r + 0.5) * row_h
            n_elems = rng.randint(9, 15)
            reverse = rng.choice([True, False])
            wave_amp = row_h * rng.uniform(0.0, 0.18)
            rot_sweep = rng.uniform(0, math.pi * 1.6)
            for i in range(n_elems):
                t = i / max(1, n_elems - 1)
                tt = (1 - t) if reverse else t
                size = row_h * (0.16 + 0.66 * tt)
                cx = (i + 0.5) * (W / n_elems)
                cy = cy_base + math.sin(t * math.pi) * wave_amp
                angle = t * rot_sweep
                self._stamp_shape_svg(svg, cx, cy, size, angle, shape)

        return svg.to_string()

    def generate_rhythm_transition_svg(self) -> str:
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#ffffff")

        shapes_pair = rng.sample(["circle", "square", "triangle", "bar"], 2)
        n_rows = rng.randint(5, 8)
        row_h = H / n_rows

        for r in range(n_rows):
            cy = (r + 0.5) * row_h
            n_elems = rng.randint(10, 17)
            base_size = row_h * rng.uniform(0.5, 0.66)
            pattern_len = rng.choice([2, 2, 3])
            row_angle = rng.uniform(0, math.tau)
            for i in range(n_elems):
                cx = (i + 0.5) * (W / n_elems)
                is_accent = (i % pattern_len == 0)
                shape = shapes_pair[0] if is_accent else shapes_pair[1]
                size_mult = 1.0 if is_accent else 0.6
                self._stamp_shape_svg(svg, cx, cy, base_size * size_mult, row_angle, shape)

        return svg.to_string()

    def generate_asymmetric_balance_svg(self) -> str:
        """Titik berat dihitung ANALITIK dari luas & posisi tiap bentuk
        (bukan menjumlahkan piksel seperti versi raster) -- untuk bentuk
        simetris beraturan (lingkaran/persegi/segitiga sama sisi) yang
        semuanya dipusatkan di (cx,cy), titik berat gabungan = rata-rata
        posisi tertimbang luas. Ini lebih presisi daripada versi raster,
        bukan aproksimasi ulang."""
        rng = random.Random(self.seed)
        W, H = self.w, self.h
        svg = SVGCanvas(W, H, background="#ffffff")
        cxc, cyc = W / 2, H / 2

        big_size = min(W, H) * rng.uniform(0.30, 0.40)
        side = rng.choice([-1, 1])
        big_x = cxc + side * W * rng.uniform(0.16, 0.26)
        big_y = cyc + rng.uniform(-H * 0.1, H * 0.1)
        big_shape = rng.choice(["circle", "square", "triangle"])
        big_angle = rng.uniform(0, math.tau)
        self._stamp_shape_svg(svg, big_x, big_y, big_size, big_angle, big_shape)
        mass = [(big_x, big_y, self._shape_area(big_size, big_shape))]

        n_small = rng.randint(2, 4)
        for _ in range(n_small):
            s = min(W, H) * rng.uniform(0.04, 0.09)
            x = cxc + rng.uniform(-W * 0.36, W * 0.36)
            y = cyc + rng.uniform(-H * 0.4, H * 0.4)
            shape = rng.choice(["circle", "square", "triangle"])
            angle = rng.uniform(0, math.tau)
            self._stamp_shape_svg(svg, x, y, s, angle, shape)
            mass.append((x, y, self._shape_area(s, shape)))

        total_area = sum(a for _, _, a in mass)
        cx_mass = sum(x * a for x, y, a in mass) / total_area
        cy_mass = sum(y * a for x, y, a in mass) / total_area
        dx, dy = cx_mass - cxc, cy_mass - cyc
        imbalance = math.hypot(dx, dy)

        if imbalance > min(W, H) * 0.01:
            ux, uy = -dx / imbalance, -dy / imbalance
            n_correction = rng.randint(2, 3)
            for k in range(n_correction):
                dist = min(W, H) * rng.uniform(0.36, 0.47)
                s = min(W, H) * rng.uniform(0.055, 0.12)
                x = cxc + ux * dist + rng.uniform(-W * 0.05, W * 0.05)
                y = cyc + uy * dist + rng.uniform(-H * 0.05, H * 0.05)
                x = max(s, min(W - s, x))
                y = max(s, min(H - s, y))
                shape = rng.choice(["circle", "square", "triangle"])
                angle = rng.uniform(0, math.tau)
                self._stamp_shape_svg(svg, x, y, s, angle, shape)

        return svg.to_string()
