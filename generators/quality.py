"""
quality.py
===========
Evaluator kualitas komposisi otomatis. Karena semua teknik di sistem ini
memakai elemen ACAK (posisi vortex, jumlah cabang, dsb), tidak semua seed
menghasilkan komposisi yang enak dipandang -- kadang kebetulan terlalu
kosong (didominasi satu warna), kadang terlalu ramai/berisik, kadang tidak
seimbang. generate_best_of() merender N kandidat dengan seed berbeda,
menilai tiap kandidat dengan beberapa metrik objektif, lalu mengembalikan
yang skornya paling tinggi -- prinsip yang sama dipakai banyak tool
generative art profesional ("best-of-N sampling").

Metrik yang dipakai (semua dihitung dari histogram grayscale citra):
1. Ink coverage balance -- proporsi piksel "gelap" vs "terang" sebaiknya
   tidak terlalu ekstrem (bukan nyaris kosong, bukan nyaris penuh hitam).
2. Contrast (std dev grayscale) -- makin tinggi biasanya makin "hidup".
3. Edge density -- kepadatan tepi/garis (via filter deteksi tepi),
   menangkap seberapa kaya detail strukturalnya.
4. Symmetry/centering bonus kecil -- komposisi yang massa visualnya tidak
   melenceng jauh dari tengah kanvas biasanya terasa lebih "mantap".

Skor akhir adalah kombinasi tertimbang dari keempatnya, dinormalisasi ke
0-100 supaya mudah dibaca di log CLI.
"""

import random
from typing import Callable, List, Tuple

import numpy as np
from PIL import Image, ImageFilter


def _score_image(img: Image.Image) -> dict:
    gray = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    H, W = gray.shape

    # 1. Ink coverage balance: proporsi piksel gelap (< 0.5)
    dark_ratio = float((gray < 0.5).mean())
    # Skor tertinggi kalau dark_ratio ada di rentang nyaman 0.12-0.55
    if dark_ratio < 0.03 or dark_ratio > 0.92:
        coverage_score = 0.05
    else:
        target = 0.28
        coverage_score = max(0.0, 1.0 - abs(dark_ratio - target) / 0.5)

    # 2. Contrast
    contrast_score = min(1.0, float(gray.std()) / 0.32)

    # 3. Edge density (kekayaan detail struktural)
    edges = np.asarray(img.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float64) / 255.0
    edge_density = float(edges.mean())
    edge_score = min(1.0, edge_density / 0.10)

    # 4. Centering: bandingkan centroid massa gelap vs pusat kanvas
    ys, xs = np.where(gray < 0.5)
    if len(xs) > 50:
        cx, cy = xs.mean() / W, ys.mean() / H
        dist_from_center = ((cx - 0.5) ** 2 + (cy - 0.5) ** 2) ** 0.5
        centering_score = max(0.0, 1.0 - dist_from_center / 0.5)
    else:
        centering_score = 0.3

    total = (coverage_score * 0.35 + contrast_score * 0.25 +
             edge_score * 0.25 + centering_score * 0.15) * 100

    return {
        "total": total,
        "dark_ratio": dark_ratio,
        "contrast": float(gray.std()),
        "edge_density": edge_density,
        "centering": centering_score,
    }


def generate_best_of(render_fn: Callable[[int], Image.Image], n_candidates: int = 4,
                      seed_base: int = None, verbose: bool = True) -> Tuple[Image.Image, int, dict]:
    """Merender n_candidates kandidat (seed berbeda-beda, diturunkan dari
    seed_base) lewat render_fn(seed) -> PIL.Image, menilai tiap kandidat,
    lalu mengembalikan (image_terbaik, seed_terbaik, info_skor).
    render_fn cukup menerima satu argumen seed -- resolusi/parameter lain
    sebaiknya sudah di-bind lebih dulu (mis. lewat lambda/functools.partial)
    supaya evaluator ini tetap generik untuk teknik apapun."""
    rng = random.Random(seed_base)
    candidates: List[Tuple[Image.Image, int, dict]] = []

    for i in range(n_candidates):
        seed = rng.randint(1, 999999)
        img = render_fn(seed)
        info = _score_image(img)
        candidates.append((img, seed, info))
        if verbose:
            print(f"    Kandidat {i + 1}/{n_candidates} (seed={seed}): skor={info['total']:.1f} "
                  f"[coverage={info['dark_ratio']:.2f} kontras={info['contrast']:.2f} "
                  f"detail={info['edge_density']:.3f}]")

    best = max(candidates, key=lambda c: c[2]["total"])
    if verbose:
        print(f"    -> Terpilih: seed={best[1]} dengan skor tertinggi {best[2]['total']:.1f}")
    return best
