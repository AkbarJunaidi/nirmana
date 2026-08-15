import math
import numpy as np
from PIL import Image

from .flowfield import WarpField


class FlowContourGenerator:
    def __init__(self, width: int, height: int, seed: int = None):
        self.w = width
        self.h = height
        self.seed = seed
        import random
        self.rng = random.Random(seed)

    def generate(self, n_vortices: tuple = (8, 14), line_density: int = None,
                 supersample: int = 3) -> Image.Image:
        ss = supersample
        W, H = self.w * ss, self.h * ss

        field = WarpField(W, H, seed=self.seed)
        diag = math.hypot(W, H)
        field.randomize_anchors(
            n_min=n_vortices[0], n_max=n_vortices[1],
            radius_range=(diag * 0.10, diag * 0.22),
            strength_range=(1.1, 2.6),
            min_separation_factor=0.6,
        )

        xs = np.arange(W, dtype=np.float64)
        ys = np.arange(H, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys)
        Xw, Yw = field.apply(X, Y)

        tilt = self.rng.uniform(-0.1, 0.1)
        phase = Xw + Yw * tilt

        n_lines = line_density or self.rng.randint(24, 38)
        period = W / n_lines
        line_frac = self.rng.uniform(0.14, 0.20)

        t = (phase % period) / period
        edge = 0.05
        mask = np.clip((line_frac - t) / edge + 0.5, 0.0, 1.0)

        gray = ((1.0 - mask) * 255).astype(np.uint8)
        img = Image.fromarray(gray, mode="L").convert("RGB")

        if ss > 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img
