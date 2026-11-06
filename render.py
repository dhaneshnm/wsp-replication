"""Step 3: demo visual. Side-by-side GIF of networks playing the same game with the same seed.

Usage:
  python -I render.py --game breakout --seed 7 --steps 400 \
      --net "zero weights=zero" \
      --net "Astra (GPT-6)=~/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz" \
      --net "Claude=runs/claude-opus-5-5/breakout/attempt1/net.npz" \
      --out breakout_side_by_side.gif
"""
import argparse
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wsp  # noqa: E402

# player, danger, reward, projectile, trail, gauge
COLORS = np.array([[80, 200, 255], [240, 70, 70], [250, 200, 60], [255, 255, 255], [120, 120, 140], [90, 220, 120]])
BG, CELL, PAD, HEAD = (18, 18, 24), 24, 12, 36

ap = argparse.ArgumentParser()
ap.add_argument("--game", default="breakout")
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--steps", type=int, default=400)
ap.add_argument("--net", action="append", required=True, help='"Label=path.npz" or "Label=zero"')
ap.add_argument("--out", default="side_by_side.gif")
a = ap.parse_args()


def run(spec):
    label, path = spec.split("=", 1)
    net = wsp.zero_net() if path == "zero" else wsp.load_npz(str(pathlib.Path(path).expanduser()))
    env = wsp._make_env(a.game, a.seed)
    obs = wsp.make_obs_fn(env, a.game)
    rng = np.random.default_rng(a.seed + 1_000_003)
    frames, scores, score, done = [], [], 0.0, False
    for _ in range(a.steps):
        if not done:
            x = obs()
            z = wsp.logits(net, x)
            p = np.exp(z - z.max()); p /= p.sum()
            r, done = env.act(int(rng.choice(6, p=p)))
            score += r
        frames.append(x.reshape(10, 10, 6)); scores.append((score, done))
    return label, frames, scores


def draw_grid(g):
    img = np.zeros((10, 10, 3)) + BG
    for c in [4, 5, 2, 1, 0, 3]:  # paint order: trail first, projectile last
        img[g[..., c] > 0] = COLORS[c]
    return np.kron(img, np.ones((CELL, CELL, 1))).astype(np.uint8)


panels = [run(s) for s in a.net]
W = len(panels) * (10 * CELL + PAD) + PAD
H = HEAD + 10 * CELL + PAD
gif = []
for t in range(a.steps):
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    for i, (label, frames, scores) in enumerate(panels):
        x0 = PAD + i * (10 * CELL + PAD)
        canvas.paste(Image.fromarray(draw_grid(frames[t])), (x0, HEAD))
        s, done = scores[t]
        d.text((x0, 4), label, fill=(230, 230, 230))
        d.text((x0, 18), f"score {s:.0f}" + ("  GAME OVER" if done else ""), fill=(250, 200, 60))
    gif.append(canvas)
gif[0].save(a.out, save_all=True, append_images=gif[1:], duration=60, loop=0)
print(f"wrote {a.out} ({a.steps} frames)")
