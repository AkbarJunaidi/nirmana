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

### 7. Gestur Emosional (Abstrak Ekspresif -- Tanpa Objek, Tanpa Makna)
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

### 8. Garis Tebal-Tipis (Line Weight Hierarchy) — Uji Presisi Desainer [BARU]
`generators/line_hierarchy.py`

Tugas paling klasik di studio DKV: membangun *value* (gelap-terang) dan
ritme komposisi semata-mata dari tebal-tipis garis dan jarak antar-garis —
tanpa bidang isi, tanpa tekstur, tanpa objek. Dipakai dosen/art director
untuk menilai jam terbang mata seorang desainer: konsistensi skala
ketebalan, presisi spasi, kontrol lengkung, dan keseimbangan komposisi.

- **Parallel Families** — beberapa "keluarga" garis nyaris tegak, tiap
  keluarga dikunci ke satu zona kolom kanvas dengan tangga ketebalan
  geometris bertahap (bukan linear, supaya kontras antar-tingkat lebih
  tegas) dan spasi presisi eksak, sehingga hierarki tiap keluarga tetap
  terbaca jelas — tidak lebur jadi anyaman kacau lintas-keluarga.
- **Concentric Taper** — cincin-cincin konsentris presisi dengan ketebalan
  meruncing dari pusat ke tepi (atau sebaliknya); showcase langsung dari
  jaminan "garis pada lingkaran selalu tersambung mulus, setipis atau
  setebal apapun".
- **Radial Taper** — jari-jari dari titik pusat dengan ketebalan meruncing
  terhadap jarak, disilang beberapa busur konsentris tipis — melatih
  presisi perpotongan garis lurus × lengkung.

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

### 11. Empat Nirmana Klasik DKV (Fondasi) [BARU]
`generators/classic_nirmana.py`

Melengkapi empat tugas nirmana paling dasar di kurikulum DKV semester awal
yang sebelumnya belum ada di sistem ini (yang lain lebih condong ke
eksplorasi garis/tekstur/ilusi kedalaman tingkat lanjut):

- **Nirmana Bidang (Figure-Ground)** -- komposisi murni dari hubungan
  bidang positif-negatif TANPA garis sama sekali. Dibangun lewat teknik
  klasik "overlap bidang transparan ber-XOR": tiap bidang baru yang
  tumpang tindih dengan bidang sebelumnya membalik warnanya -- persis
  menumpuk lembar kalkir tembus pandang, menghasilkan bentuk baru dari
  pertemuan bidang lama yang tak pernah digambar eksplisit (ambiguitas
  figure-ground otentik, bukan simulasi).
- **Nirmana Kontras Value** -- grid presisi 9 tingkat value abu-abu
  (putih murni s/d hitam murni, terbagi rata & eksak), disusun via
  constraint sederhana sehingga tak ada dua sel bertetangga langsung
  dengan value sama -- melatih kalibrasi mata terhadap tangga tonal.
  Ukuran sel grid sengaja dibuat tidak seragam (gaya Mondrian) untuk
  nilai komposisi tambahan.
- **Nirmana Irama** -- tiga varian terpisah sesuai tiga jenis irama
  visual klasik: **Repetitif** (elemen identik, interval & ukuran tetap
  presisi), **Progresif** (ukuran/rotasi berubah bertahap menyusuri
  baris, membentuk efek "crescendo"), dan **Oposisi** (dua motif
  berselang-seling AB/AAB membentuk pola "ketukan").
- **Nirmana Keseimbangan Asimetris** -- bukan cuma "kelihatan seimbang":
  titik berat visual dihitung SECARA AKTUAL dari sebaran tinta di piksel
  hasil render (bobot = tingkat kegelapan), lalu elemen penyeimbang kecil
  ditambahkan secara algoritmik di sisi berlawanan pada jarak jauh dari
  pusat (prinsip tuas: massa kecil x jarak jauh menyeimbangkan massa
  besar x jarak dekat) sampai titik berat mendekati pusat kanvas.

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

## Sistem Presisi (Anti-Patahan) & Kesiapan Cetak/Digital

### Full-Bleed (komposisi memenuhi seluruh bidang gambar)

Beberapa teknik sempat punya masalah "tidak penuh halaman" -- komposisi
hanya mengisi sebagian kecil kanvas, menyisakan margin/bidang kosong luas
yang tidak seimbang secara nirmana. Root cause-nya bermacam-macam dan
semua sudah diperbaiki:

- **Dipatok ke sisi terpendek, bukan diagonal** (`arrow_burst`,
  `dot_gradient_x`, `shape_cross`, `wireframe_mesh`) -- motif radial yang
  radiusnya dibatasi `min(W,H)` secara matematis TIDAK PERNAH bisa
  menjangkau sudut kanvas (jarak ke sudut = setengah diagonal, ~1.4x lebih
  jauh). Diperbaiki dengan memakai `hypot(W,H)/2` sebagai batas radius,
  plus kepadatan elemen diskalakan mengikuti penambahan panjang supaya
  tidak jadi renggang. `shape_cross` khususnya ditambah lapisan lengan
  ketiga (tersier, dengan jitter halus) di antara lengan utama & sekunder
  supaya kepadatan meluruh mulus dari pusat ke tepi tanpa "pita kosong" --
  lalu laju pembesaran bentuknya dikalibrasi ulang supaya di ujung lengan
  bentuk-bentuknya tetap terbaca satu-satu (bukan menyatu jadi blok solid
  akibat kepadatan berlebihan).
- **Blob/cluster terlalu sedikit & terlalu kecil** (`organik_burst`,
  `organik_branching`, `anaglyph_relief`) -- diperbaiki dengan pola
  grid+jitter adaptif terhadap luas kanvas (kepadatan otomatis menyesuaikan
  ukuran render), memastikan tiap kuadran kanvas kebagian motif.
- **Bidang objek yang secara geometris tak mungkin menyentuh sudut**
  (`wireframe_mesh` dengan bentuk bola) -- ditambal aksen garis radiasi
  tipis ala blueprint yang konsisten dengan tema teknik tsb.
- **Proporsi tinggi/lebar terlalu kecil** (`lsystem_branching`) -- tinggi
  tanaman dinaikkan dari 62-78%/30-48% jadi 84-94%/55-78% dari kanvas,
  jumlah rumpun mengikuti lebar kanvas.
- **Mosaik Voronoi merender teknik di ukuran KANVAS PENUH lalu memotongnya
  ke sel** -- ini salah secara konsep: banyak teknik nirmana sengaja
  dipusatkan (bola, ledakan radial), jadi kalau dipotong ke sel yang jauh
  dari tengah kanvas, yang muncul cuma potongan acak yang terlihat
  berantakan. Diperbaiki dengan merender tiap teknik PAS di bounding box
  sel-nya sendiri, sehingga tiap sel menampilkan motif utuh & proporsional.

### Anti-Patahan — `precision.py` (garis & lengkung selalu tersambung mulus)

Akar masalah teknis "garis pada lingkaran/poligon yang patah" bukan cuma
soal jumlah titik sampel, tapi bug rendering nyata di Pillow:

- `ImageDraw.line(pts, width>1)` tidak mengisi sudut sambungan antar-segmen
  dengan mulus kalau sudutnya tajam (lingkaran ber-wobble, garis
  bergerigi, dsb) — muncul celah segitiga kecil di tiap sambungan.
- `ImageDraw.polygon(outline=.., width>1)` bahkan **tidak mengisi sama
  sekali** sudut simpul poligon — jadi tessellasi kubus isometrik, frame
  lorong perspektif, dsb selalu bercelah kalau outline-nya tebal.

`draw_precise_polyline()` menambal tiap titik sambungan dengan "dab" bundar
seukuran lebar garis (setara *round-join* di software vektor) — solusi ini
menutup celah untuk sudut setajam apapun, di skala resolusi berapapun.
`circle_points()` menghasilkan titik lingkaran dengan kerapatan sampel
ADAPTIF terhadap radius (makin besar radius/makin besar file cetak, makin
rapat sampelnya) dan menjamin titik awal = titik akhir persis (tanpa
jahitan 1px di titik penutupan). Dipakai di semua teknik yang menggambar
cincin/poligon tebal: `organic_patterns.py`, `geometric_patterns.py`,
`depth_illusion.py`, `stratum.py`, `line_hierarchy.py`.

### DPI presisi fisik untuk segala media

Preset resolusi (`main.py: ASPECT_RATIOS`) sekarang membawa metadata DPI
yang benar secara fisik, bukan cuma jumlah piksel -- ditanam ke chunk pHYs
file PNG saat disimpan, supaya file yang sama terbaca ukuran fisik yang
tepat baik dibuka di software cetak (InDesign/Illustrator/percetakan)
maupun dipakai di media digital (Instagram, web, presentasi):

| Preset | Ukuran piksel | DPI | Ukuran fisik |
|---|---|---|---|
| 1:1 Instagram Post | 1600×1600 | digital (72/96) | — |
| 4:5 Feed Sosmed | 1350×1687 | digital | — |
| 9:16 Story/Reels | 1080×1920 | digital | — |
| 16:9 Landscape/Banner | 1920×1080 | digital | — |
| A4 Potrait | 2480×3508 | 300 | 21 × 29.7 cm |
| A3 Potrait | 3508×4961 | 300 | 29.7 × 42 cm |
| Kartu Nama (+bleed) | 1110×650 | 300 | 9.4 × 5.5 cm |
| Poster Besar | 3543×5315 | 150 | 60 × 90 cm |
| Kanvas Cetak Persegi | 4724×4724 | 300 | 40 × 40 cm |
| 4K Ultra HD | 3840×2160 | digital | layar/wallpaper |

Preset digital sengaja tidak dipaksa DPI tertentu (biar software default
72/96 dpi -- itu memang benar untuk layar), sementara semua preset cetak
memakai DPI industri standar (300 untuk cetak detail/kartu nama/kanvas,
150 untuk format poster besar supaya ukuran file tetap wajar tanpa
mengorbankan ketajaman baca dari jarak pandang normal).

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

## Sistem "Acak" yang Benar-Benar Acak (Shuffle Bag)

Mode teknik "acak" (dan mode acak-per-karya untuk warna) sebelumnya memilih
lewat `random.choice()` independen tiap karya -- secara probabilitas murni,
dengan ~30 teknik dan batch pendek (3-6 karya), peluang ada teknik yang
terulang di batch yang sama cukup tinggi (>25%), dan itu terasa "kok
itu-itu lagi" di mata pengguna walau matematis valid.

Sekarang dipakai **shuffle bag** (sampling tanpa pengembalian): semua
teknik diacak urutannya lalu dipakai satu-satu sampai habis, baru
"kantung" diisi ulang & diacak lagi. Ini menjamin tidak ada teknik yang
terulang sebelum semua teknik lain kebagian giliran dulu -- hasilnya
terasa jauh lebih adil dan variatif untuk mata, terutama pada batch
sedang (5-15 karya) yang paling sering dipakai orang.

## Struktur Proyek

```
nirmana/
├── main.py                       # CLI orchestrator
├── generators/
│   ├── flowfield.py               # Mesin distorsi vortex (dipakai bersama)
│   ├── precision.py               # [BARU] Jaminan garis/lengkung anti-patahan (dipakai bersama)
│   ├── line_nirmana.py           # Teknik 1: Nirmana Garis
│   ├── organic_patterns.py       # Teknik 2: Nirmana Organik (3 varian)
│   ├── geometric_patterns.py     # Teknik 3: Nirmana Geometrik (3 varian)
│   ├── depth_illusion.py         # Teknik 4: Depth Illusion (3 varian)
│   ├── advanced_depth.py         # Teknik 5: Advanced Depth (3 varian)
│   ├── depth_explorations.py     # Teknik 6: Depth Exploration (3 varian)
│   ├── emotive.py                # Teknik 7: Gestur Emosional (abstrak ekspresif)
│   ├── line_hierarchy.py         # Teknik 8: Garis Tebal-Tipis (3 varian)
│   ├── classic_nirmana.py        # [BARU] Teknik 11: 4 Nirmana Klasik DKV (6 varian)
│   ├── radial_motif.py           # Teknik 9: Motif Radial (4 varian)
│   ├── composition.py            # Teknik 10: Mosaik Voronoi
│   ├── stratum.py                # Sedimen / Kekosongan / Patahan (kedalaman formal)
│   ├── flow_contours.py          # Kontur Alir (paisley/fingerprint)
│   ├── dot_nirmana.py            # Nirmana Titik (halftone dot grid)
│   ├── registry.py               # Satu sumber kebenaran semua teknik dasar
│   ├── quality.py                # Evaluator kualitas & best-of-N sampling
│   ├── gallery.py                # Generator galeri HTML kontak-sheet
│   ├── presets.py                # Preset kurasi teknik+warna siap pakai
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
