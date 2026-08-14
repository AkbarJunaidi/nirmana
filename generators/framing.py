"""
framing.py
===========
Membungkus hasil generate dengan bingkai presentasi ala tugas kuliah DKV --
persis format pada foto referensi awal ("Putri Marcella Azzizah //
2810011364 // Nirmana Garis"): margin putih di sekeliling karya, garis
tepi tipis, dan caption nama/NIM/judul teknik di bagian bawah.

Ini murni kosmetik presentasi (tidak mengubah komposisi nirmana itu
sendiri sama sekali) -- berguna kalau hasilnya mau langsung dipakai
sebagai lampiran tugas / dicetak / diunggah.
"""

from typing import Optional
from PIL import Image, ImageDraw, ImageFont


def add_presentation_frame(
    img: Image.Image,
    technique_label: str,
    name: Optional[str] = None,
    nim: Optional[str] = None,
    margin_ratio: float = 0.055,
    caption_ratio: float = 0.065,
    bg_color=(255, 255, 255),
    text_color=(15, 15, 15),
    border_color=(15, 15, 15),
) -> Image.Image:
    """Menempatkan img di tengah kanvas putih dengan margin, garis tepi
    tipis mengelilingi karya, dan baris caption di bagian bawah berformat
    "Nama // NIM // Judul Teknik" (bagian yang kosong otomatis dilewati)."""
    w, h = img.size
    margin = int(min(w, h) * margin_ratio)
    caption_h = int(min(w, h) * caption_ratio)

    canvas_w = w + margin * 2
    canvas_h = h + margin * 2 + caption_h

    canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
    canvas.paste(img.convert("RGB"), (margin, margin))

    draw = ImageDraw.Draw(canvas)
    border_w = max(1, int(min(w, h) * 0.002))
    draw.rectangle([margin, margin, margin + w - 1, margin + h - 1],
                    outline=border_color, width=border_w)

    parts = [p for p in [name, nim, technique_label] if p]
    caption = "  //  ".join(parts) if parts else technique_label

    try:
        font = ImageFont.load_default(size=int(caption_h * 0.34))
    except TypeError:
        font = ImageFont.load_default()

    text_y = margin + h + caption_h / 2
    draw.text((margin, text_y), caption, fill=text_color, font=font, anchor="lm")

    return canvas
