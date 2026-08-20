"""
precision.py
=============
Utilitas presisi geometris dipakai BERSAMA oleh semua generator, supaya
seluruh sistem punya satu jaminan kualitas render yang sama: garis, lengkung,
dan lingkaran HARUS selalu tersambung mulus -- tidak boleh ada patahan/notch
di titik sambungan (joint), sekecil apapun radiusnya atau setajam apapun
sudutnya.

Kenapa ini perlu (akar masalah teknis):
- `ImageDraw.line(pts, width=W)` pada Pillow menggambar tiap segmen sebagai
  persegi panjang independen. Kalau W > 1 dan sudut antar-segmen tajam
  (misal poligon bersudut, atau lingkaran ber-wobble dengan sample rendah),
  akan muncul CELAH SEGITIGA KECIL di titik sambungan -- ini sumber paling
  umum "garis pada lingkaran yang putus-putus" pada nirmana garis tebal.
- `ImageDraw.polygon(pts, outline=C, width=W)` bahkan LEBIH parah: Pillow
  tidak mengisi sudut outline poligon sama sekali untuk width > 1, jadi
  setiap simpul poligon (mis. tessellasi kubus isometrik, frame lorong
  perspektif) selalu bercelah kalau outline-nya tebal.

Solusi presisi: setiap simpul (dan tiap sambungan segmen) ditambal dengan
"dab" lingkaran berdiameter = lebar garis. Ini bukan trik kosmetik -- secara
matematis dab bundar berdiameter W di titik sambungan SELALU menutup penuh
celah segitiga yang terbentuk antar dua segmen selebar W, untuk sudut
berapapun. Hasilnya setara round-join/round-cap vektor sungguhan (seperti
stroke-linejoin: round di SVG/Illustrator), presisi di semua skala resolusi.
"""

import math
from typing import List, Sequence, Tuple

Point = Tuple[float, float]


def draw_precise_polyline(draw, pts: Sequence[Point], fill, width: int,
                           closed: bool = False) -> None:
    """Menggambar polyline (atau loop tertutup, mis. lingkaran/ring) yang
    DIJAMIN tersambung mulus di setiap titik -- tanpa patahan di sudut
    setajam apapun, dan tanpa jahitan (seam) di titik penutupan loop.

    - closed=True: titik akhir otomatis ditarik balik ke titik awal (dan
      dab penutup ditambahkan di sana juga), jadi lingkaran/cincin/poligon
      benar-benar menutup sempurna -- tidak ada celah 1px di titik jahitan
      seperti yang sering terjadi kalau titik awal != titik akhir karena
      pembulatan floating point.
    """
    pts = list(pts)
    if len(pts) < 2:
        return
    if closed and pts[0] != pts[-1]:
        pts = pts + [pts[0]]

    w = max(1, int(round(width)))

    if w <= 1:
        # Garis rambut (hairline): sambungan 1px nyaris tidak pernah bercelah,
        # dab tidak diperlukan -- hemat waktu render.
        draw.line(pts, fill=fill, width=1)
        return

    # joint="curve" sudah membantu Pillow membulatkan sambungan internal di
    # banyak versi, tapi TIDAK dijamin di semua versi/platform -- dab manual
    # di bawah ini adalah jaring pengaman presisi yang tidak bergantung versi.
    try:
        draw.line(pts, fill=fill, width=w, joint="curve")
    except TypeError:
        draw.line(pts, fill=fill, width=w)

    r = w / 2.0
    for (px, py) in pts:
        draw.ellipse([px - r, py - r, px + r, py + r], fill=fill)


def draw_precise_polygon_outline(draw, pts: Sequence[Point], fill, width: int) -> None:
    """Outline poligon tertutup presisi (pengganti draw.polygon(outline=..,
    width=..) yang punya celah di setiap simpul kalau width > 1)."""
    draw_precise_polyline(draw, pts, fill, width, closed=True)


def circle_points(cx: float, cy: float, r: float, steps: int = None,
                   wobble_amp: float = 0.0, wobble_freq: float = 0.0,
                   phase: float = 0.0) -> List[Point]:
    """Menghasilkan titik-titik lingkaran (atau lingkaran ber-wobble organik)
    dengan kerapatan sampel ADAPTIF terhadap radius -- supaya lingkaran besar
    (mis. dicetak di kanvas ukuran poster/A3) tetap terlihat mulus, bukan
    kaku bersegi seperti pada sample rate tetap. Titik pertama & terakhir
    dijamin identik (loop benar-benar menutup, tidak butuh penambalan lain).
    """
    if steps is None:
        # minimal 48 segmen, tambah 1 segmen tiap ~3.5px keliling supaya
        # kelengkungan tetap presisi di resolusi cetak besar sekalipun.
        steps = max(48, int((2 * math.pi * max(r, 1.0)) / 3.5))
    pts = []
    for k in range(steps + 1):
        th = (k / steps) * math.tau
        rr = r
        if wobble_amp:
            rr = r + math.sin(th * wobble_freq + phase) * wobble_amp
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    pts[-1] = pts[0]  # penutupan eksak, hilangkan drift floating-point
    return pts
