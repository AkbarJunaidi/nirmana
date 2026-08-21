"""
svg_export.py
===============
Utilitas ekspor SVG generik, dipakai teknik-teknik berbasis garis/bentuk
vektor murni (bukan noise/tekstur raster piksel). Kenapa SVG penting di
sini, bukan cuma "format tambahan":

- Presisi TAK TERBATAS di skala manapun -- garis tetap tajam dicetak
  poster 2 meter ataupun ditampilkan di layar HP, karena tidak ada piksel
  yang di-upscale. PNG resolusi berapapun akhirnya pecah kalau di-zoom
  cukup jauh; SVG tidak pernah.
- Sambungan garis/lengkung otomatis mulus lewat `stroke-linejoin="round"`
  & `stroke-linecap="round"` bawaan SVG -- renderer vektor sungguhan
  TIDAK punya bug "celah di sudut sambungan" seperti rasterizer Pillow
  (itu sebabnya `precision.py` perlu ada di sisi raster dengan trik dab
  manual; di sisi SVG masalah itu tidak muncul sama sekali, built-in).
- Lingkaran digambar sebagai elemen `<circle>` SVG asli (bukan pendekatan
  poligon N-titik seperti `precision.circle_points`) -- presisi matematis
  sempurna, bukan lagi soal sample rate.
- File langsung siap pakai di Adobe Illustrator/Inkscape/CorelDRAW, dan
  bisa langsung diimpor ke software cutting plotter atau laser cutter
  kalau nirmananya mau dipamerkan secara fisik (bukan cuma dicetak datar
  di kertas).
- Untuk komposisi yang didominasi garis/bentuk geometris sederhana,
  ukuran filenya jauh lebih kecil daripada PNG resolusi cetak.

Modul ini SENGAJA tidak dipakai untuk teknik berbasis noise/tekstur
piksel (organik burst, DLA branching, distorsi vortex, moire, dsb) --
itu secara fundamental raster (jutaan nilai piksel unik hasil simulasi),
SVG-nya justru akan jauh lebih besar & lebih lambat dibuka daripada PNG,
tanpa manfaat presisi tambahan (tidak ada garis/lengkung matematis murni
untuk direpresentasikan sebagai vektor).
"""

from typing import List, Optional, Sequence, Tuple

Point = Tuple[float, float]


def _pts_to_str(pts: Sequence[Point]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


class SVGCanvas:
    """Akumulator elemen SVG sederhana -- panggil `polyline`/`circle`/
    `rect`/`polygon`/`path_evenodd`, lalu `save(path)` atau `to_string()`
    di akhir. Tidak butuh supersample/anti-alias sama sekali (beda dari
    semua generator raster di sistem ini) -- renderer SVG menangani
    anti-aliasing secara native di sisi penampil (browser/Illustrator/
    printer RIP), presisi terjaga otomatis."""

    def __init__(self, width: float, height: float, background: Optional[str] = "#ffffff"):
        self.w = width
        self.h = height
        self.elements: List[str] = []
        if background:
            self.elements.append(
                f'<rect x="0" y="0" width="{width}" height="{height}" fill="{background}"/>')

    def polyline(self, pts: Sequence[Point], stroke: str = "#000000",
                 width: float = 1.0, closed: bool = False) -> None:
        """Garis/lengkung terbuka atau tertutup (loop) -- sambungan selalu
        dijamin mulus lewat stroke-linejoin="round", tanpa perlu trik dab
        manual seperti versi raster (precision.draw_precise_polyline)."""
        if len(pts) < 2:
            return
        tag = "polygon" if closed else "polyline"
        self.elements.append(
            f'<{tag} points="{_pts_to_str(pts)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width:.3f}" stroke-linejoin="round" stroke-linecap="round"/>')

    def circle(self, cx: float, cy: float, r: float, fill: Optional[str] = None,
               stroke: Optional[str] = None, width: float = 1.0) -> None:
        """Lingkaran SVG asli -- presisi matematis sempurna, bukan
        pendekatan poligon N-segmen seperti di sisi raster."""
        fill_attr = fill if fill else "none"
        parts = [f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{max(r, 0):.2f}" fill="{fill_attr}"']
        if stroke:
            parts.append(f' stroke="{stroke}" stroke-width="{width:.3f}"')
        parts.append('/>')
        self.elements.append("".join(parts))

    def rect(self, x: float, y: float, w: float, h: float, fill: str) -> None:
        self.elements.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"/>')

    def polygon(self, pts: Sequence[Point], fill: Optional[str] = None,
                stroke: Optional[str] = None, width: float = 1.0) -> None:
        fill_attr = fill if fill else "none"
        parts = [f'<polygon points="{_pts_to_str(pts)}" fill="{fill_attr}"']
        if stroke:
            parts.append(f' stroke="{stroke}" stroke-width="{width:.3f}" stroke-linejoin="round"')
        parts.append('/>')
        self.elements.append("".join(parts))

    def path_evenodd(self, shapes: Sequence[dict], fill: str = "#000000") -> None:
        """Satu elemen <path> gabungan berisi beberapa sub-path tertutup
        (lingkaran/poligon), dirender dengan fill-rule="evenodd" -- area
        yang tertutup oleh JUMLAH GANJIL sub-path terisi warna, jumlah
        GENAP kosong. Ini padanan vektor EKSAK dari operasi XOR raster
        yang dipakai `classic_nirmana.generate_figure_ground`: tiap
        overlap baru "membalik" area itu, prinsip identik, tapi di sini
        murni matematis (bukan piksel di-XOR) sehingga tepi shape selalu
        presisi sempurna di skala berapapun, tanpa jejak aliasing.
        shape dict: {"type": "circle", "cx","cy","r"} atau
                    {"type": "polygon", "pts": [(x,y), ...]}"""
        d_parts = []
        for shape in shapes:
            if shape["type"] == "circle":
                cx, cy, r = shape["cx"], shape["cy"], shape["r"]
                # SVG tidak punya perintah "circle" di dalam <path>; dibangun
                # dari dua busur (arc) setengah lingkaran yang saling menutup.
                d_parts.append(
                    f"M {cx - r:.2f},{cy:.2f} "
                    f"A {r:.2f},{r:.2f} 0 1,0 {cx + r:.2f},{cy:.2f} "
                    f"A {r:.2f},{r:.2f} 0 1,0 {cx - r:.2f},{cy:.2f} Z")
            elif shape["type"] == "polygon":
                pts = shape["pts"]
                if len(pts) >= 3:
                    d_parts.append("M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z")
        d = " ".join(d_parts)
        self.elements.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd"/>')

    def to_string(self) -> str:
        body = "\n  ".join(self.elements)
        return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" '
                f'height="{self.h:.0f}" viewBox="0 0 {self.w:.0f} {self.h:.0f}">\n'
                f'  {body}\n</svg>\n')

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_string())
