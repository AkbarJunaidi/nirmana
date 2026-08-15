import math
import random
import numpy as np
from PIL import Image, ImageDraw


class DotNirmanaGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed
        self.rng = random.Random(seed)
        self.nprng = np.random.default_rng(seed)

    def _field(self, W, H):
        xs = np.linspace(0, 1, W)
        ys = np.linspace(0, 1, H)
        X, Y = np.meshgrid(xs, ys)
        field = np.zeros((H, W))

        n_blobs = self.rng.randint(3, 6)
        for _ in range(n_blobs):
            bx = self.rng.uniform(0.15, 0.85)
            by = self.rng.uniform(0.15, 0.85)
            br = self.rng.uniform(0.12, 0.30)
            amp = self.rng.uniform(0.6, 1.0)
            d2 = (X - bx) ** 2 + (Y - by) ** 2
            field += amp * np.exp(-d2 / (2 * br * br))

        field -= field.min()
        if field.max() > 0:
            field /= field.max()
        return field

    def generate(self, grid_n: int = None, supersample: int = 2,
                 invert: bool = False) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss

        cols = grid_n or self.rng.randint(26, 40)
        rows = round(cols * H / W)

        field = self._field(W, H)

        img = Image.new("L", (W, H), 255)
        draw = ImageDraw.Draw(img)

        cell_w = W / cols
        cell_h = H / rows
        min_r = cell_w * 0.03
        max_r = cell_w * 0.46

        for row in range(rows):
            for col in range(cols):
                px = (col + 0.5) * cell_w
                py = (row + 0.5) * cell_h
                fx = min(W - 1, int(px))
                fy = min(H - 1, int(py))
                v = field[fy, fx]
                if invert:
                    v = 1 - v
                r = min_r + (max_r - min_r) * v
                if r < 0.6:
                    continue
                draw.ellipse([px - r, py - r, px + r, py + r], fill=0)

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert("RGB")
