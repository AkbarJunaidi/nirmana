"""
quality.py
===========
Evaluator kualitas komposisi otomatis -- BUKAN cuma penilai angka, tapi
"asisten kritik" yang memberi umpan balik tekstual spesifik & bisa
ditindaklanjuti, seperti art director yang mengomentari tugas mahasiswa.

Dua fungsi utama:

1. generate_best_of() -- karena semua teknik di sistem ini memakai elemen
   ACAK, tidak semua seed menghasilkan komposisi yang enak dipandang.
   Fungsi ini merender N kandidat dengan seed berbeda, menilai tiap
   kandidat dengan metrik objektif, lalu mengembalikan yang skornya
   tertinggi ("best-of-N sampling", prinsip yang sama dipakai banyak tool
   generative art profesional).

2. generate_critique() -- menganalisis SATU citra (kandidat manapun, tidak
   harus dari best-of) dan menghasilkan poin-poin kritik berbahasa
   Indonesia yang konkret & bisa ditindaklanjuti, bukan cuma angka mentah.

Metrik yang dipakai (semua dihitung langsung dari piksel citra, generik
untuk latar terang MAUPUN gelap -- tidak mengasumsikan latar putih):

1. Ink ratio & coverage balance -- proporsi piksel "berisi tinta" (beda
   jauh dari warna latar dominan) sebaiknya tidak terlalu ekstrem.
2. Area kosong tersambung terbesar (largest connected blank region) --
   metrik BARU yang secara langsung menangkap masalah "tidak full-page"
   (satu kuadran/sudut kosong besar) yang sebelumnya cuma ketahuan lewat
   inspeksi visual manual satu-satu.
3. Keseimbangan kuadran (kiri-kanan, atas-bawah) -- bobot visual (massa
   tinta) yang terlalu condong ke satu sisi ditandai secara spesifik sisi
   mana yang berat.
4. Contrast (std dev grayscale) -- makin tinggi biasanya makin "hidup".
5. Edge density -- kepadatan tepi/garis, menangkap kekayaan detail
   struktural.
6. Centering -- seberapa jauh titik berat visual melenceng dari tengah
   kanvas (bukan berarti harus persis di tengah -- nirmana keseimbangan
   asimetris sengaja melenceng -- tapi tetap metrik informatif).

Skor akhir adalah kombinasi tertimbang, dinormalisasi ke 0-100.
"""

import random
from typing import Callable, List, Tuple

import numpy as np
from PIL import Image, ImageFilter

try:
    from scipy import ndimage
    _HAS_SCIPY = True
except ImportError:  # pragma: no cover - scipy ada di environment produksi
    _HAS_SCIPY = False


def _background_value(gray_small: np.ndarray) -> float:
    """Estimasi warna latar dominan lewat puncak histogram -- generik
    untuk latar putih, hitam, ATAU abu-abu (mis. teknik value_grid,
    sedimen) tanpa mengasumsikan latar selalu terang."""
    hist, edges = np.histogram(gray_small, bins=40, range=(0.0, 1.0))
    peak_bin = int(np.argmax(hist))
    return float((edges[peak_bin] + edges[peak_bin + 1]) / 2)


def _largest_blank_region_frac(gray: np.ndarray, bg_value: float,
                                downsample: int = 110, tol: float = 0.08) -> float:
    """Fraksi kanvas yang ditempati SATU region kosong (latar) tersambung
    terbesar -- inilah metrik yang langsung menangkap masalah "komposisi
    tidak penuh halaman" (satu sudut/kuadran kosong luas), yang sebelumnya
    cuma ketahuan lewat audit visual manual satu teknik per satu teknik.
    Dianalisis di resolusi kecil (downsample) karena yang dicari adalah
    area kosong MAKRO, bukan celah kecil antar-elemen."""
    small_img = Image.fromarray((gray * 255).astype(np.uint8)).resize(
        (downsample, downsample), Image.BOX)
    small = np.asarray(small_img, dtype=np.float64) / 255.0
    blank_mask = np.abs(small - bg_value) < tol

    if not blank_mask.any():
        return 0.0

    if _HAS_SCIPY:
        structure = np.ones((3, 3), dtype=int)  # konektivitas-8 (termasuk diagonal)
        labeled, num = ndimage.label(blank_mask, structure=structure)
        if num == 0:
            return 0.0
        sizes = np.bincount(labeled.ravel())[1:]
        largest = sizes.max()
    else:
        # Fallback tanpa scipy: flood-fill manual sederhana (BFS)
        visited = np.zeros_like(blank_mask, dtype=bool)
        largest = 0
        H, W = blank_mask.shape
        for sy in range(H):
            for sx in range(W):
                if blank_mask[sy, sx] and not visited[sy, sx]:
                    stack = [(sy, sx)]
                    visited[sy, sx] = True
                    size = 0
                    while stack:
                        y, x = stack.pop()
                        size += 1
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                ny, nx = y + dy, x + dx
                                if 0 <= ny < H and 0 <= nx < W and blank_mask[ny, nx] and not visited[ny, nx]:
                                    visited[ny, nx] = True
                                    stack.append((ny, nx))
                    largest = max(largest, size)

    return float(largest / blank_mask.size)


def _quadrant_balance(gray: np.ndarray, bg_value: float) -> dict:
    """Bobot visual (massa tinta) kiri vs kanan & atas vs bawah -- dipakai
    untuk memberi kritik SPESIFIK sisi mana yang terlalu berat/kosong,
    bukan cuma 'komposisi kurang seimbang' yang generik."""
    H, W = gray.shape
    ink = np.abs(gray - bg_value)
    total = ink.sum()
    if total < 1e-6:
        return {"lr_imbalance": 0.0, "tb_imbalance": 0.0, "heavy_side": None}

    left = ink[:, :W // 2].sum()
    right = ink[:, W // 2:].sum()
    top = ink[:H // 2, :].sum()
    bottom = ink[H // 2:, :].sum()

    lr_imbalance = abs(left - right) / total
    tb_imbalance = abs(top - bottom) / total

    heavy_parts = []
    if lr_imbalance > 0.15:
        heavy_parts.append("kanan" if right > left else "kiri")
    if tb_imbalance > 0.15:
        heavy_parts.append("bawah" if bottom > top else "atas")

    return {
        "lr_imbalance": float(lr_imbalance),
        "tb_imbalance": float(tb_imbalance),
        "heavy_side": "-".join(heavy_parts) if heavy_parts else None,
    }


def _ink_bbox_coverage(gray: np.ndarray, bg_value: float, downsample: int = 110) -> float:
    """Seberapa luas bounding-box elemen berisi tinta MEMBENTANG di kanvas
    (lebar x tinggi bounding box, dibagi luas kanvas). Metrik ini membedakan
    dua situasi yang sama-sama punya 'area kosong tersambung besar' tapi
    maknanya beda total:
      - Elemen jarang tapi MEMBENTANG sampai ke semua tepi (mis. motif
        radial, grid titik renggang) -> bbox coverage tinggi -> area kosong
        di antaranya cuma "napas" gaya sparse, BUKAN masalah.
      - Elemen menggerombol di satu area & menyisakan satu sisi/sudut
        benar-benar kosong -> bbox coverage rendah -> ini masalah nyata.
    """
    small_img = Image.fromarray((gray * 255).astype(np.uint8)).resize(
        (downsample, downsample), Image.BOX)
    small = np.asarray(small_img, dtype=np.float64) / 255.0
    ink = np.abs(small - bg_value) > 0.12
    ys, xs = np.where(ink)
    if len(xs) < 5:
        return 0.0
    w_cov = (xs.max() - xs.min() + 1) / downsample
    h_cov = (ys.max() - ys.min() + 1) / downsample
    return float(w_cov * h_cov)


def _score_image(img: Image.Image, sparse_ok: bool = False) -> dict:
    """sparse_ok=True untuk teknik yang MEMANG sengaja jarang/berongga
    sebagai prinsip desain (mis. Keseimbangan Asimetris yang sengaja
    menyisakan ruang negatif luas, atau motif radial/titik yang jarang
    secara gaya) -- melunakkan penalti area-kosong & target kepadatan
    tinta supaya evaluator tidak memberi kritik yang salah konteks."""
    gray = np.asarray(img.convert("L"), dtype=np.float64) / 255.0
    H, W = gray.shape

    small_for_bg = np.asarray(
        Image.fromarray((gray * 255).astype(np.uint8)).resize((110, 110), Image.BOX),
        dtype=np.float64) / 255.0
    bg_value = _background_value(small_for_bg)

    # 1. Ink ratio (generik latar terang/gelap): proporsi piksel yang
    #    berbeda jauh dari warna latar dominan.
    ink_mask = np.abs(gray - bg_value) > 0.12
    ink_ratio = float(ink_mask.mean())
    target = 0.14 if sparse_ok else 0.30
    if ink_ratio < 0.02 or ink_ratio > 0.95:
        coverage_score = 0.05
    else:
        coverage_score = max(0.0, 1.0 - abs(ink_ratio - target) / 0.5)

    # 2. Area kosong tersambung terbesar -- metrik anti "tidak full-page".
    #    Dilunakkan kalau elemen sudah membentang sampai tepi (bbox_coverage
    #    tinggi) ATAU teknik memang sparse_ok by design.
    largest_blank_frac = _largest_blank_region_frac(gray, bg_value)
    bbox_coverage = _ink_bbox_coverage(gray, bg_value)
    if sparse_ok:
        blank_threshold = 0.80
    elif bbox_coverage > 0.80:
        blank_threshold = 0.65  # elemen sudah menjangkau semua tepi -> longgar
    else:
        blank_threshold = 0.35
    blank_region_score = max(0.0, 1.0 - max(0.0, largest_blank_frac - blank_threshold) / 0.45)

    # 3. Keseimbangan kuadran kiri-kanan / atas-bawah
    quad = _quadrant_balance(gray, bg_value)
    quadrant_balance_score = max(0.0, 1.0 - (quad["lr_imbalance"] + quad["tb_imbalance"]) / 2 / 0.5)

    # 4. Contrast
    contrast_score = min(1.0, float(gray.std()) / 0.32)

    # 5. Edge density (kekayaan detail struktural)
    edges = np.asarray(img.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float64) / 255.0
    edge_density = float(edges.mean())
    edge_score = min(1.0, edge_density / 0.10)

    # 6. Centering: bandingkan centroid massa tinta vs pusat kanvas
    ys, xs = np.where(ink_mask)
    if len(xs) > 50:
        cx, cy = xs.mean() / W, ys.mean() / H
        dist_from_center = ((cx - 0.5) ** 2 + (cy - 0.5) ** 2) ** 0.5
        centering_score = max(0.0, 1.0 - dist_from_center / 0.5)
    else:
        centering_score = 0.3

    total = (coverage_score * 0.20 + blank_region_score * 0.25 +
             quadrant_balance_score * 0.15 + contrast_score * 0.15 +
             edge_score * 0.15 + centering_score * 0.10) * 100

    return {
        "total": total,
        "dark_ratio": ink_ratio,  # nama dipertahankan demi kompatibilitas pemanggil lama
        "ink_ratio": ink_ratio,
        "bg_value": bg_value,
        "largest_blank_frac": largest_blank_frac,
        "blank_threshold": blank_threshold,
        "bbox_coverage": bbox_coverage,
        "sparse_ok": sparse_ok,
        "lr_imbalance": quad["lr_imbalance"],
        "tb_imbalance": quad["tb_imbalance"],
        "heavy_side": quad["heavy_side"],
        "contrast": float(gray.std()),
        "edge_density": edge_density,
        "centering": centering_score,
    }


def generate_critique(img: Image.Image, sparse_ok: bool = False) -> List[str]:
    """Menganalisis SATU citra dan mengembalikan daftar poin kritik
    berbahasa Indonesia, urut dari yang paling penting -- seperti catatan
    singkat art director, bukan cuma angka mentah. Bisa dipanggil untuk
    citra manapun (tidak harus lewat generate_best_of).

    sparse_ok=True untuk teknik yang memang sengaja jarang/berongga
    sebagai prinsip desain (mis. Keseimbangan Asimetris) -- supaya
    kritiknya tidak salah konteks menyebut ruang negatif yang disengaja
    sebagai 'belum penuh'."""
    info = _score_image(img, sparse_ok=sparse_ok)
    poin = []

    # -- Area kosong besar (paling sering jadi masalah "kurang full-page") --
    # Ambang disesuaikan otomatis: kalau elemen sudah membentang sampai ke
    # tepi kanvas (bbox_coverage tinggi) atau teknik ini memang sparse_ok,
    # area kosong besar dianggap wajar (ruang napas gaya), bukan cacat.
    bf = info["largest_blank_frac"]
    bt = info["blank_threshold"]
    if bf > bt + 0.15:
        poin.append(f"Ada satu area kosong besar tersambung (~{bf*100:.0f}% bidang kanvas) -- "
                     "komposisi terasa belum penuh. Pertimbangkan menambah elemen di area itu "
                     "atau perbesar/perbanyak motif utama.")
    elif bf > bt:
        poin.append(f"Ada area kosong cukup luas (~{bf*100:.0f}% kanvas) di salah satu sisi -- "
                     "masih wajar sebagai ruang napas, tapi bisa dipadatkan sedikit lagi kalau "
                     "targetnya full-bleed.")

    # -- Keseimbangan kuadran --
    if info["heavy_side"] and not sparse_ok:
        poin.append(f"Bobot visual condong ke sisi {info['heavy_side']} -- kalau bukan "
                     "kesengajaan (mis. nirmana keseimbangan asimetris), pertimbangkan "
                     "menambah elemen penyeimbang di sisi berlawanan.")

    # -- Kepadatan tinta --
    ir = info["ink_ratio"]
    low_ink_threshold = 0.015 if sparse_ok else 0.04
    if ir < low_ink_threshold:
        poin.append(f"Kanvas sangat kosong (elemen berisi cuma ~{ir*100:.1f}% bidang) -- "
                     "komposisi terasa lemah/kurang berani secara visual.")
    elif ir > 0.85:
        poin.append(f"Kanvas nyaris penuh tinta (~{ir*100:.0f}%) -- kalau dicetak fisik ini "
                     "boros tinta, dan secara visual bisa terasa sesak tanpa ruang istirahat mata.")

    # -- Kontras tonal --
    if info["contrast"] < 0.12:
        poin.append("Kontras tonal rendah, permukaan terasa agak datar -- coba perbesar "
                     "rentang gelap-terang antar-elemen.")

    # -- Detail struktural --
    if info["edge_density"] < 0.02:
        poin.append("Detail struktural minim, permukaan terasa polos/kosong dari tepi.")

    if not poin:
        poin.append("Komposisi sudah seimbang: sebaran elemen memenuhi bidang gambar dengan "
                     "baik, tidak ada area kosong dominan, dan kontras tonalnya cukup hidup.")

    # Info kepadatan tinta selalu disertakan di akhir sebagai catatan
    # praktis (relevan kalau nirmananya akan dicetak fisik).
    poin.append(f"[Info] Estimasi kepadatan tinta: {ir*100:.1f}% dari bidang kanvas.")

    return poin


def generate_best_of(render_fn: Callable[[int], Image.Image], n_candidates: int = 4,
                      seed_base: int = None, verbose: bool = True,
                      sparse_ok: bool = False) -> Tuple[Image.Image, int, dict]:
    """Merender n_candidates kandidat (seed berbeda-beda, diturunkan dari
    seed_base) lewat render_fn(seed) -> PIL.Image, menilai tiap kandidat,
    lalu mengembalikan (image_terbaik, seed_terbaik, info_skor).
    render_fn cukup menerima satu argumen seed -- resolusi/parameter lain
    sebaiknya sudah di-bind lebih dulu (mis. lewat lambda/functools.partial)
    supaya evaluator ini tetap generik untuk teknik apapun.

    sparse_ok=True untuk teknik yang memang sengaja jarang/berongga
    sebagai prinsip desain (lihat SPARSE_BY_DESIGN di registry.py) --
    diteruskan ke _score_image supaya kandidat tidak dihukum keliru
    karena ruang negatif yang disengaja."""
    rng = random.Random(seed_base)
    candidates: List[Tuple[Image.Image, int, dict]] = []

    for i in range(n_candidates):
        seed = rng.randint(1, 999999)
        img = render_fn(seed)
        info = _score_image(img, sparse_ok=sparse_ok)
        candidates.append((img, seed, info))
        if verbose:
            print(f"    Kandidat {i + 1}/{n_candidates} (seed={seed}): skor={info['total']:.1f} "
                  f"[tinta={info['ink_ratio']:.2f} kosong_terbesar={info['largest_blank_frac']:.2f} "
                  f"kontras={info['contrast']:.2f} detail={info['edge_density']:.3f}]")

    best = max(candidates, key=lambda c: c[2]["total"])
    if verbose:
        print(f"    -> Terpilih: seed={best[1]} dengan skor tertinggi {best[2]['total']:.1f}")
    return best
