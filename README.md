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

### 4. Depth Illusion (Kesan Kedalaman ala Prinsip Gestalt)
`generators/depth_illusion.py`

Terinspirasi studi "Gestalt principles – depth" (proximity, closure,
continuity, common fate, pragnanz): garis yang menciut ke satu titik
menipu mata jadi melihat ruang 3D, retakan yang membentuk bidang tertutup
menipu mata jadi melihat pecahan kaca solid.

- **Perspective Tunnel** — grid & spoke yang memusat ke satu vanishing
  point dengan spasi non-linear (mengecil eksponensial), band antar-frame
  diisi pola dot/hatch/solid berselang agar terasa gradasi cahaya lorong.
- **Shatter Web** — retakan radial + cincin patah-patah dari titik
  tumbukan (seperti kaca pecah), sebagian sel di-flood-fill hitam pekat
  supaya otak "menutup" bidang jadi solid (prinsip *closure*).
- **Spiral Hatch Burst** — ribuan guratan tinta pendek mengikuti medan
  spiral, rapat di pusat dan renggang ke tepi, dimodulasi jadi pola
  pinwheel N-lengan — mengeksploitasi *similarity* & *pragnanz*.

### 5. Advanced Depth (Eksplorasi Kedalaman Lanjutan)
`generators/advanced_depth.py`

Tiga pendekatan kedalaman yang berbeda secara fundamental dari teknik lain:

- **Moire Interference** — dua kisi periodik (radial/linear) ditumpuk pada
  sudut/pusat sedikit berbeda lalu di-XOR. Ini bukan ilusi optik yang
  "dibuat-buat" — ini fenomena interferensi fisik nyata (sama seperti pada
  kain tenun atau screen printing), menghasilkan pola fringe yang seolah
  berdenyut/bergerak.
- **Wireframe Mesh 3D** — permukaan matematis sungguhan (bidang gelombang,
  bola, atau saddle) diproyeksikan dari 3D ke 2D lewat rotasi & perspective
  divide yang benar (bukan pseudo-3D). Kedalaman diperkuat lewat
  painter's-algorithm sederhana: garis yang lebih dekat ke "kamera"
  digambar lebih tebal & lebih gelap.
- **Droste Zoom** — rekursi Droste sungguhan: kanvas ditempel ulang
  (di-scale + rotate) ke dalam dirinya sendiri berkali-kali, menghasilkan
  efek "tak berhingga" asli. Bisa dipakai di atas pola nirmana manapun
  sebagai base image (mode CLI otomatis memilih base acak dari teknik lain
  supaya hasilnya selalu kaya).

### 6. Depth Exploration (Jelajah Lebih Dalam)
`generators/depth_explorations.py`

Tiga pendekatan lagi, makin jauh dari "ilusi di atas kertas" menuju
mekanisme kedalaman yang genuinely berbeda:

- **Anaglyph Relief** — stereoskopi sungguhan. Tiap "bukit" digambar
  sebagai kontur cincin konsentris pada dua kanvas mata kiri/kanan dengan
  pusat digeser proporsional terhadap tinggi lokalnya, lalu digabung jadi
  citra merah-cyan. Dipakai kacamata 3D anaglyph, kedalamannya benar-benar
  terlihat — bukan cuma trik gambar di kertas datar.
- **L-System Branching** — Lindenmayer System: tata bahasa string
  rewriting yang sama persis dipakai memodelkan pertumbuhan tanaman secara
  matematis (bukan random walk seperti DLA). Bounding box dihitung dulu
  (dry-run pass) baru diskalakan supaya selalu memenuhi kanvas secara
  proporsional.
- **Parallax Silhouette** — beberapa lapis siluet organik ditumpuk dengan
  gradasi value & skala (aerial/atmospheric perspective): elemen dekat
  gelap & besar di depan, elemen jauh terang & kecil di belakang — cara
  paling primal otak manusia membaca kedalaman lewat oklusi.

### 8. Gestur Emosional (Abstrak Ekspresif -- Tanpa Objek, Tanpa Makna)
`generators/emotive.py`

> *"Nirmana adalah jeritan sunyi yang terperangkap di antara persimpangan
> garis dan lengkung; ia tidak merekam rupa, melainkan mengendapkan
> denyut emosi yang terlalu telanjang untuk dijelaskan oleh kata-kata."*

Semua teknik lain di sistem ini bekerja dari kepastian matematis (simetri,
distorsi terkontrol, tessellasi presisi). Teknik ini justru bekerja dari
ketidakpastian yang disengaja -- tidak merepresentasikan objek apapun.
Tiga elemen dikomposisikan bersama:

- **Gesture strokes** — sapuan panjang lahir dari random-walk bermomentum
  (bukan kurva matematis rapi), lebar garis naik-turun mengikuti fungsi
  "denyut" (pulse envelope, bukan gradasi linear) -- seperti tekanan
  tangan yang gemetar, menebal di titik tertekan, menipis saat melepas.
- **Severing lines** — garis lurus tajam yang menyayat/memotong gestur,
  representasi visual dari "persimpangan garis dan lengkung" yang
  disebut dalam kalimat; sebagian sengaja terputus di tengah (jeda,
  ketidaktuntasan).
- **Tension knots** — simpul kusut acak di titik-titik tekanan tertentu,
  tempat "jeritan" mengendap dan tak lagi bisa mengalir keluar.

Semua elemen dikomposit dengan alpha blending (bukan flat fill) di atas
wash tonal sangat halus, sehingga persilangan goresan menumpuk jadi lebih
gelap secara alami -- seperti tinta asli yang menyerap berulang di kertas.

### 9. Motif Radial (Repetisi & Simetri Klasik)
`generators/radial_motif.py`

Prinsip nirmana paling fundamental: satu motif dasar diulang dengan simetri
di sekeliling pusat, mengisi seluruh bidang. Empat varian:

- **Arrow Burst** — panah-panah tersegmentasi memancar dari pusat ke
  penjuru kanvas, dengan lingkaran target konsentris di titik pusat.
- **Dot Gradient X** — dua garis diagonal membentuk X, berisi lingkaran
  bergradasi ukuran (halftone klasik), dengan taburan titik latar halus.
- **Shape Cross** — 4 (atau lebih) lengan menyilang, tiap lengan berisi
  barisan bentuk geometris berselang-seling (segitiga, kotak, lingkaran)
  yang membesar dari pusat ke ujung.
- **Weave Stripes** — garis-garis diagonal berselang-seling arah,
  menciptakan ilusi anyaman/tenun optik.

### 10. Mosaik Voronoi (Kombinasi Multi-Layer)
`generators/composition.py`

Kanvas dipartisi jadi beberapa region organik (Voronoi cells dari titik
acak), tiap region diisi teknik nirmana yang berbeda lalu disatukan jadi
satu komposisi utuh dengan garis pembatas tipis antar-region. Mendekati
kompleksitas nirmana tekstur kaya (banyak motif berdampingan dalam satu
bidang). Otomatis membatasi resolusi kerja internal untuk kanvas besar
(cetak/4K) supaya tidak kehabisan memori.

## Sistem Warna

Tiga mode dipilih lewat CLI:

1. **Hitam-Putih** (default) — paling otentik secara kaidah nirmana klasik.
2. **Palet Kurasi** — 16 palet duotone siap pakai (`generators/palette.py`),
   dari editorial monokrom sampai neon/pastel.
3. **Acak Harmonis** — `generate_random_palette()` membangun sepasang warna
   di ruang HSL memakai teori warna (complementary / analogous / triadic /
   split-complementary / monochrome-tint), bukan RGB comot mentah, sehingga
   kontras & keserasian tetap terjaga. Tersedia sebagai "satu warna acak
   untuk semua karya" atau "acak berbeda tiap karya" dalam satu batch.

### Infrastruktur "Masterpiece" (Registry, Quality Evaluator, Galeri, Preset)

- **`registry.py`** — satu sumber kebenaran untuk semua teknik dasar.
  `main.py` dan `composition.py` (Mosaik Voronoi) memanggil
  `render_base_technique()` yang sama persis dari sini — begitu ada
  teknik baru ditambahkan, semua bagian sistem otomatis ikut punya akses.
- **`quality.py`** — evaluator kualitas otomatis (`generate_best_of`).
  Karena semua teknik memakai elemen acak, tidak semua seed menghasilkan
  komposisi enak dipandang. Fungsi ini merender N kandidat, menilai
  masing-masing lewat 4 metrik objektif (ink coverage balance, contrast,
  edge density, centering), lalu memilih otomatis yang skornya tertinggi
  — prinsip "best-of-N sampling" yang sama dipakai tool generative art
  profesional. Diaktifkan lewat CLI (masukkan jumlah kandidat > 1).
- **`gallery.py`** — setelah satu batch selesai, `main.py` otomatis
  membuat `outputs/galeri.html`: kontak-sheet portable (gambar di-embed
  base64, bisa dibuka/dibagikan sendirian) untuk melihat semua hasil
  batch sekaligus di browser tanpa buka file satu-satu.
- **`presets.py`** — 14 preset kurasi manual (kombinasi teknik + skema
  warna yang sudah dicoba & terlihat bagus) untuk yang tidak mau pusing
  memilih satu-satu lewat menu panjang. Preset tidak mengunci seed --
  tiap render tetap unik, yang dikurasi hanya kombinasi teknik & gayanya.

## Struktur Proyek

```
nirmana/
├── main.py                       # CLI orchestrator
├── generators/
│   ├── flowfield.py              # Mesin distorsi vortex (dipakai bersama)
│   ├── line_nirmana.py           # Teknik 1: Nirmana Garis
│   ├── organic_patterns.py       # Teknik 2: Nirmana Organik (3 varian)
│   ├── geometric_patterns.py     # Teknik 3: Nirmana Geometrik (3 varian)
│   ├── depth_illusion.py         # Teknik 4: Depth Illusion (3 varian)
│   ├── advanced_depth.py         # Teknik 5: Advanced Depth (3 varian)
│   ├── depth_explorations.py     # Teknik 6: Depth Exploration (3 varian)
│   ├── radial_motif.py           # Teknik 7: Motif Radial (4 varian)
│   ├── emotive.py                # Teknik 8: Gestur Emosional (abstrak ekspresif)
│   ├── composition.py            # Teknik 9: Mosaik Voronoi
│   ├── registry.py               # Satu sumber kebenaran semua teknik dasar
│   ├── quality.py                # Evaluator kualitas & best-of-N sampling
│   ├── gallery.py                # Generator galeri HTML kontak-sheet
│   ├── presets.py                # 14 preset kurasi teknik+warna siap pakai
│   └── palette.py                # Palet kurasi + generator warna acak
└── outputs/                      # Hasil render + galeri.html (dibuat otomatis)
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
