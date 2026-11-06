"""Step 0: prove this harness reproduces the paper's Experiment 5 before swapping in Claude.

Checks per game:
  1. Parsing Astra's reply (answer.md) with our parser gives exactly their hand.npz.
  2. Scoring hand.npz with our scorer lands near their published mean.

Usage: python -I verify_original.py --logs ~/lm_understand-logs [--episodes 100]
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wsp  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--logs", required=True)
ap.add_argument("--episodes", type=int, default=100)
ap.add_argument("--games", default="breakout,seaquest,asterix")
a = ap.parse_args()

exp = pathlib.Path(a.logs).expanduser() / "exp5_write_from_scratch"
published = json.loads((exp / "eval" / "minatar_eval.json").read_text())

for game in a.games.split(","):
    answer = (exp / "runs" / game / "reply" / "answer.md").read_text()
    parsed, rep = wsp.apply_edits(answer)
    theirs = wsp.load_npz(str(exp / "networks" / game / "hand.npz"))
    diff = max(float(np.abs(parsed[k] - theirs[k]).max()) for k in wsp.SHAPES)
    print(f"[{game}] parse: {rep.applied}/{rep.statements} statements, {len(rep.errors)} errors, "
          f"max |ours - theirs| = {diff:.2e}")
    for e in rep.errors[:5]:
        print("   ", e)
    res = wsp.evaluate(theirs, game, episodes=a.episodes)
    pub = published[game]["hand"]["mean"]
    print(f"[{game}] score over {a.episodes} eps: {res['mean']:.1f} ± {res['se']:.1f}  "
          f"(published, 1000 eps: {pub:.1f}); mean length {res['mean_length']:.0f}")
