"""
presets.py
===========
Preset kurasi manual: kombinasi teknik + skema warna yang sudah dicoba dan
diuji terlihat bagus, untuk orang yang tidak mau pusing memilih satu-satu
lewat menu panjang. Cukup pilih satu nomor preset, sistem otomatis pakai
teknik + parameter + rekomendasi warna yang sudah pas.

Preset TIDAK mengunci seed -- tiap render tetap unik/acak, yang dikurasi
adalah KOMBINASI teknik & gaya warnanya saja.
"""

from typing import NamedTuple, Optional


class Preset(NamedTuple):
    label: str
    description: str
    technique: str
    palette_mode: str          # "hitam_putih" | "palette" | "acak_harmonis"
    palette_name: Optional[str]  # dipakai kalau palette_mode == "palette"


CURATED_PRESETS = {
    "1": Preset(
        label="Editorial Monokrom",
        description="Nirmana Garis klasik hitam-putih -- paling otentik, cocok cetak formal.",
        technique="garis",
        palette_mode="hitam_putih",
        palette_name=None,
    ),
    "2": Preset(
        label="Pusaran Dramatis",
        description="Spiral Hatch Burst dengan warna acak harmonis -- kesan pusaran tinta hidup.",
        technique="depth_spiral",
        palette_mode="acak_harmonis",
        palette_name=None,
    ),
    "3": Preset(
        label="Karang Organik",
        description="DLA Branching (motif karang) di atas nuansa hijau lumut -- alami & tekstural.",
        technique="organik_branching",
        palette_mode="palette",
        palette_name="forest_moss",
    ),
    "4": Preset(
        label="Lorong Senja",
        description="Perspective Tunnel dengan palet ember senja -- kedalaman dramatis, hangat.",
        technique="depth_tunnel",
        palette_mode="palette",
        palette_name="sunset_ember",
    ),
    "5": Preset(
        label="Kubus Emas Kerajaan",
        description="Isometric Cubes dengan palet emas kerajaan -- mewah, presisi, elegan.",
        technique="geometrik_kubus",
        palette_mode="palette",
        palette_name="royal_gold",
    ),
    "6": Preset(
        label="Interferensi Karang Laut",
        description="Moire Interference dengan nuansa terumbu karang -- optik, menyegarkan.",
        technique="moire",
        palette_mode="palette",
        palette_name="coral_reef",
    ),
    "7": Preset(
        label="Rekursi Tak Berhingga",
        description="Droste Zoom dengan warna acak -- efek tak berhingga yang selalu unik.",
        technique="droste",
        palette_mode="acak_harmonis",
        palette_name=None,
    ),
    "8": Preset(
        label="Pegunungan Senyap",
        description="Parallax Silhouette dengan nuansa indigo tinta -- tenang, atmosferik.",
        technique="parallax",
        palette_mode="palette",
        palette_name="ink_indigo",
    ),
    "9": Preset(
        label="Pertumbuhan Organik",
        description="L-System Branching dengan nuansa mawar plum -- puitis, botanikal.",
        technique="lsystem",
        palette_mode="palette",
        palette_name="plum_blossom",
    ),
    "10": Preset(
        label="Stereoskopi Klasik",
        description="Anaglyph Relief -- selalu merah-cyan (pakai kacamata 3D untuk efek penuh).",
        technique="anaglyph",
        palette_mode="hitam_putih",  # diabaikan; anaglyph selalu red-cyan
        palette_name=None,
    ),
    "11": Preset(
        label="Mosaik Maksimalis",
        description="Mosaik Voronoi -- banyak teknik menyatu jadi satu komposisi kaya, warna acak.",
        technique="mosaik_voronoi",
        palette_mode="acak_harmonis",
        palette_name=None,
    ),
    "12": Preset(
        label="Panah Radiasi Tegas",
        description="Arrow Burst hitam-putih -- ikon, presisi, langsung menarik perhatian.",
        technique="motif_arrow",
        palette_mode="hitam_putih",
        palette_name=None,
    ),
    "13": Preset(
        label="Gradasi Titik Silang",
        description="Dot Gradient X dengan nuansa slate monokrom -- halftone klasik, elegan.",
        technique="motif_dotx",
        palette_mode="palette",
        palette_name="monochrome_slate",
    ),
    "14": Preset(
        label="Anyaman Optik",
        description="Weave Stripes dengan warna acak -- ilusi tenun yang selalu unik.",
        technique="motif_weave",
        palette_mode="acak_harmonis",
        palette_name=None,
    ),
    "15": Preset(
        label="Jeritan Sunyi",
        description="Gestur Emosional hitam-putih murni -- abstrak ekspresif, tegang, tanpa objek.",
        technique="emosi",
        palette_mode="hitam_putih",
        palette_name=None,
    ),
    "16": Preset(
        label="Luka yang Mengendap",
        description="Gestur Emosional dengan nuansa crimson gelap -- lebih pekat, lebih menyayat.",
        technique="emosi",
        palette_mode="palette",
        palette_name="crimson_paper",
    ),
}
