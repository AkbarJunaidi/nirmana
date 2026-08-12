# Python Nirmana Generator — Sistem DKV Otentik

Generator nirmana yang benar-benar meniru **teknik & kaidah nirmana asli**
(dwimatra), bukan sekadar menaruh bentuk geometris acak di kanvas.
Setiap teknik di sini adalah algoritma/simulasi matematis yang memang jadi
dasar gaya visual tersebut di dunia nyata.

## Instalasi

```bash
pip install pillow numpy --break-system-packages
```

## Menjalankan

```bash
cd nirmana
python3 main.py
```

Ikuti prompt CLI: pilih rasio/resolusi, teknik nirmana, palet warna, dan
jumlah karya. Hasil tersimpan di folder `outputs/`.

## Teknik yang Tersedia

### 1. Nirmana Garis — Op-Art Flow Distortion
`generators/line_nirmana.py` + `generators/flowfield.py`

Beberapa titik "vortex" ditempatkan acak di kanvas, lalu seluruh **ruang
koordinat** kanvas didistorsi berputar mengelilingi titik-titik itu (swirl
warp — teknik yang sama dipakai filter "twirl" di software desain).
Garis-garis paralel digambar di atas ruang yang sudah terdistorsi ini,
menghasilkan pola mengalir seperti sidik jari/marmer cair.

### 2. Nirmana Organik
`generators/organic_patterns.py`

- **Hatching Burst** — bentuk-bentuk "spora" memanjang yang memancar dari
  satu titik pangkal, diisi stipple dots dan outline tinta.
- **Concentric Cells** — packing lingkaran acak (mirip Poisson-disc),
  tiap sel digambar sebagai cincin konsentris dengan tepi ber-wobble
  organik (bukan lingkaran sempurna) — mirip serat kayu / pebble mosaic.
- **DLA Branching** — **Diffusion-Limited Aggregation**: simulasi partikel
  yang random-walk lalu menempel begitu menyentuh struktur yang sudah ada.
  Ini adalah mekanisme fisik nyata di balik pola kristal es, karang, dan
  percabangan mineral — bukan noise yang dipalsukan jadi terlihat organik.

### 3. Nirmana Geometrik
`generators/geometric_patterns.py`

- **Isometric Cubes** — tessellasi kubus 3D klasik dari 3 belah ketupat
  (gelap/sedang/terang) yang disusun presisi secara matematis.
- **Spiral Checkerboard** — papan catur yang koordinatnya diremap ke ruang
  polar (radius + sudut), menghasilkan ilusi spiral optik.
- **Distorted Grid** — grid/graticule yang di-warp memakai mesin vortex
  yang sama dengan Nirmana Garis (mode garis tipis atau mode kotak
  catur/checkerboard).

### 4. Nirmana Kombinasi (Multi-Layer Composition)
`generators/composition.py`

- **Papan Studi (`StudyBoard`)** — grid perbandingan beberapa teknik
  sekaligus, berlabel per sel, kolom kiri "ORGANIK" / kolom kanan
  "GEOMETRIK" — mereplikasi persis format tugas nirmana di referensi
  foto 3 (papan eksplorasi/studi teknik).
- **Mosaik Voronoi (`VoronoiMosaic`)** — kanvas dipartisi jadi beberapa
  region organik (Voronoi cells dari titik acak), tiap region diisi
  teknik nirmana yang berbeda lalu disatukan jadi satu komposisi utuh
  dengan garis pembatas tipis antar-region. Mendekati kompleksitas
  nirmana tekstur kaya (banyak motif berdampingan dalam satu bidang).
  Otomatis membatasi resolusi kerja internal untuk kanvas besar
  (cetak/4K) supaya tidak kehabisan memori.

## Struktur Proyek

```
nirmana/
├── main.py                       # CLI orchestrator
├── generators/
│   ├── flowfield.py              # Mesin distorsi vortex (dipakai bersama)
│   ├── line_nirmana.py           # Teknik 1: Nirmana Garis
│   ├── organic_patterns.py       # Teknik 2: Nirmana Organik (3 varian)
│   ├── geometric_patterns.py     # Teknik 3: Nirmana Geometrik (3 varian)
│   └── palette.py                # Recolor duotone opsional
└── outputs/                      # Hasil render (dibuat otomatis)
```

## Menggunakan sebagai Library (tanpa CLI)

```python
from generators.line_nirmana import LineNirmanaGenerator
from generators.organic_patterns import OrganicNirmanaGenerator
from generators.geometric_patterns import GeometricNirmanaGenerator

# Nirmana Garis
gen = LineNirmanaGenerator(1600, 1600, seed=42)
img = gen.generate(band_count=24)
img.save("hasil.png")

# Nirmana Organik - DLA Branching
gen = OrganicNirmanaGenerator(1600, 1600, seed=42)
img = gen.generate_reaction_diffusion_blob()
img.save("hasil_organik.png")

# Nirmana Geometrik - Isometric Cubes
gen = GeometricNirmanaGenerator(1600, 1600, seed=42)
img = gen.generate_isometric_cubes()
img.save("hasil_geometrik.png")
```

## Rencana Pengembangan Lanjutan (belum diimplementasi)

- Quality evaluator otomatis (kontras, keseimbangan komposisi, rule of
  thirds) untuk memilih kandidat terbaik dari beberapa render, seperti
  arsitektur `NirBaru` di proyek asli — bisa diadaptasi ke sistem ini.
- Web/GUI viewer sederhana untuk preview cepat tanpa buka file satu-satu.
