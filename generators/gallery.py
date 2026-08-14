"""
gallery.py
===========
Membuat satu file HTML kontak-sheet (contact sheet) dari kumpulan karya
yang baru di-generate dalam satu batch -- supaya hasilnya bisa dilihat
sekaligus di browser tanpa buka file satu-satu, cocok untuk portofolio.
"""

import base64
import html
import os
from typing import List, Tuple


def _embed_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def build_html_gallery(entries: List[Tuple[str, str, str]], output_path: str,
                        title: str = "Nirmana Generator -- Galeri Hasil") -> str:
    """entries: list of (filepath, technique_label, meta_string).
    Gambar di-embed langsung sebagai base64 supaya file HTML-nya portable
    (bisa dibuka/dibagikan sendirian tanpa perlu folder outputs menyertainya)."""
    cards = []
    for path, label, meta in entries:
        if not os.path.exists(path):
            continue
        b64 = _embed_as_base64(path)
        fname = html.escape(os.path.basename(path))
        cards.append(f"""
        <div class="card">
          <img src="{b64}" alt="{html.escape(label)}" loading="lazy" />
          <div class="meta">
            <div class="label">{html.escape(label)}</div>
            <div class="sub">{html.escape(meta)}</div>
            <div class="fname">{fname}</div>
          </div>
        </div>""")

    html_doc = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8" />
<title>{html.escape(title)}</title>
<style>
  :root {{
    --bg: #0d0d0f;
    --card-bg: #17171b;
    --text: #f2f2f2;
    --sub: #9a9aa2;
    --accent: #e8c874;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    padding: 40px 32px 80px;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 600;
    letter-spacing: 0.02em;
    margin: 0 0 6px;
  }}
  .subtitle {{
    color: var(--sub);
    font-size: 13px;
    margin-bottom: 32px;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 22px;
  }}
  .card {{
    background: var(--card-bg);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #26262c;
    transition: transform 0.15s ease, border-color 0.15s ease;
  }}
  .card:hover {{
    transform: translateY(-3px);
    border-color: var(--accent);
  }}
  .card img {{
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    display: block;
    background: #fff;
  }}
  .meta {{ padding: 12px 14px 14px; }}
  .label {{ font-size: 13px; font-weight: 600; margin-bottom: 3px; }}
  .sub {{ font-size: 11.5px; color: var(--accent); margin-bottom: 3px; }}
  .fname {{ font-size: 10.5px; color: var(--sub); word-break: break-all; }}
  footer {{ margin-top: 48px; color: var(--sub); font-size: 11px; text-align: center; }}
</style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="subtitle">{len(cards)} karya -- dibuat otomatis oleh Python Nirmana Generator</div>
  <div class="grid">
    {''.join(cards)}
  </div>
  <footer>Python Nirmana Generator &mdash; Sistem DKV Otentik</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return output_path
