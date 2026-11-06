"""Step 2: one table. PPO baselines and Astra (published), a zero-weight floor (measured), Claude (measured).

Usage: python -I scoreboard.py --logs ~/lm_understand-logs [--runs runs] [--episodes 1000]
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wsp  # noqa: E402

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", required=True)
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--episodes", type=int, default=1000)
    a = ap.parse_args()

    pub = json.loads((pathlib.Path(a.logs).expanduser() / "exp5_write_from_scratch/eval/minatar_eval.json").read_text())


    def best(game, prefix):
        keys = [k for k in pub[game] if k.startswith(prefix)]
        return max(pub[game][k]["mean"] for k in keys)


    cache = pathlib.Path(a.runs) / "zero_floor.json"
    floor = json.loads(cache.read_text()) if cache.exists() else {}

    rows = []
    for game in ["breakout", "seaquest", "asterix"]:
        if game not in floor:  # all-zero weights = uniform random actions
            floor[game] = wsp.evaluate(wsp.zero_net(), game, episodes=a.episodes)["mean"]
        claude, cut = {}, {}
        for f in sorted(pathlib.Path(a.runs).glob(f"**/{game}/attempt*/run.json")):
            if "analysis" in f.parts:  # analysis scratch copies, not editor runs
                continue
            r = json.loads(f.read_text())
            if r.get("valid_attempt") is False:  # cut off (max_tokens) or refused: not a capability sample
                cut[r["model"]] = cut.get(r["model"], 0) + 1
                continue
            claude.setdefault(r["model"], []).append(r["score"]["mean"])
        row = [game, floor[game], best(game, "ppo100"), best(game, "ppo500"), pub[game]["hand"]["mean"]]
        cl = "; ".join(f"{m}: best {max(v):.1f}, median {np.median(v):.1f}, all {sorted(round(x, 1) for x in v)} (n={len(v)}"
                       + (f", {cut[m]} cut off, excluded" if cut.get(m) else "") + ")" for m, v in claude.items())
        rows.append((row, cl or "not run yet"))

    pathlib.Path(a.runs).mkdir(exist_ok=True)
    cache.write_text(json.dumps(floor))

    print(f"{'game':<9} {'zero':>7} {'PPO100M':>8} {'PPO500M':>8} {'Astra':>7}  Claude")
    for (g, z, p1, p5, ast), cl in rows:
        print(f"{g:<9} {z:>7.1f} {p1:>8.1f} {p5:>8.1f} {ast:>7.1f}  {cl}")
    print("\nPPO and Astra: published 1,000-episode means (best seed). Zero and Claude: measured here.")


if __name__ == "__main__":  # required: macOS multiprocessing uses spawn
    main()
