"""Weight-Space Programming replication core (Experiment 5, MinAtar).

Implements, from the spec in the original prompts:
  - the `edits` language parser (last ```edits block wins, bad statements skipped)
  - the 600 -> 32 -> 32 -> 6 tanh policy
  - the 6-channel observation built from MinAtar's own channels
  - scoring: mean score over N episodes, softmax-sampled actions,
    sticky actions 0.1 (inside MinAtar), episodes cut at 10,000 steps

Source spec: github.com/RikiyaT/lm_understand-logs, exp5_write_from_scratch (Nov 2026).
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

import numpy as np

SHAPES = {"W1": (600, 32), "b1": (32,), "W2": (32, 32), "b2": (32,), "W3": (32, 6), "b3": (6,)}

# How the network's 6 channels are built from each game's own channels (from each prompt's THE INPUT).
CHANNEL_MAP = {
    "breakout": [["paddle"], [], ["brick"], ["ball"], ["trail"], []],
    "asterix": [["player"], ["enemy"], ["gold"], [], ["trail"], []],
    "seaquest": [
        ["sub_front", "sub_back"],
        ["enemy_fish", "enemy_sub", "enemy_bullet"],
        ["enemy_fish", "enemy_sub", "diver"],
        ["friendly_bullet"],
        ["trail", "sub_back"],
        ["oxygen_guage", "diver_guage"],
    ],
}

MAX_STEPS = 10_000
STICKY = 0.1


# ---------------------------------------------------------------- edits parser
@dataclass
class ParseReport:
    statements: int = 0
    applied: int = 0
    errors: list[str] = field(default_factory=list)


_STMT = re.compile(r"^\s*(W1|b1|W2|b2|W3|b3)\s*\[(.*?)\]\s*(=|\*=|\+=|-=)\s*(.+?)\s*$", re.S)


def zero_net() -> dict[str, np.ndarray]:
    return {k: np.zeros(s, dtype=np.float32) for k, s in SHAPES.items()}


def last_edits_block(text: str) -> str | None:
    blocks = re.findall(r"```edits[ \t]*\n(.*?)```", text, re.S)
    return blocks[-1] if blocks else None


def _strip_comment(line: str) -> str:
    return line.split("#", 1)[0]


def _logical_statements(block: str) -> list[str]:
    """Join lines until brackets balance, so long lists can continue over lines."""
    out, buf, depth = [], "", 0
    for raw in block.splitlines():
        line = _strip_comment(raw).rstrip()
        if not line.strip() and depth == 0:
            continue
        buf = f"{buf} {line}" if buf else line
        depth = buf.count("[") - buf.count("]")
        if depth <= 0:
            out.append(buf.strip())
            buf, depth = "", 0
    if buf.strip():
        out.append(buf.strip())
    return out


def _parse_index(idx: str, ndim: int):
    parts = [p.strip() for p in idx.split(",")]
    if len(parts) != ndim:
        raise ValueError(f"expected {ndim} indices, got {len(parts)}")
    out = []
    for p in parts:
        if ":" in p:
            bits = [b.strip() for b in p.split(":")]
            if len(bits) > 3:
                raise ValueError(f"bad slice {p!r}")
            nums = [int(b) if b else None for b in bits]
            out.append(slice(*nums))
        else:
            out.append(int(p))
    return tuple(out)


def apply_edits(text: str, net: dict[str, np.ndarray] | None = None):
    """Apply the LAST ```edits block of `text`. Returns (net, report)."""
    net = net if net is not None else zero_net()
    rep = ParseReport()
    block = last_edits_block(text)
    if block is None:
        rep.errors.append("no ```edits block found")
        return net, rep
    for stmt in _logical_statements(block):
        rep.statements += 1
        try:
            m = _STMT.match(stmt)
            if not m:
                raise ValueError("unreadable statement")
            name, idx, op, val = m.groups()
            arr = net[name]
            key = _parse_index(idx, arr.ndim)
            value = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
            if not np.all(np.isfinite(value)) or np.any(np.abs(value) > 1e6):
                raise ValueError("value out of range")
            target = arr[key]
            if np.ndim(target) and value.ndim and value.shape != np.shape(target):
                value = value.reshape(np.shape(target))  # raises on size mismatch
            if op == "=":
                arr[key] = value
            elif op == "*=":
                arr[key] = target * value
            elif op == "+=":
                arr[key] = target + value
            else:
                arr[key] = target - value
            rep.applied += 1
        except Exception as e:  # spec: a statement that cannot be read is skipped
            rep.errors.append(f"{stmt[:80]!r}: {e}")
    return net, rep


def load_npz(path: str) -> dict[str, np.ndarray]:
    names = {
        "actor/dense1/kernel": "W1", "actor/dense1/bias": "b1",
        "actor/dense2/kernel": "W2", "actor/dense2/bias": "b2",
        "actor/logits/kernel": "W3", "actor/logits/bias": "b3",
    }
    d = np.load(path)
    return {names.get(k, k): d[k].astype(np.float32) for k in d.files}


def save_npz(net: dict[str, np.ndarray], path: str) -> None:
    np.savez(path, **{
        "actor/dense1/kernel": net["W1"], "actor/dense1/bias": net["b1"],
        "actor/dense2/kernel": net["W2"], "actor/dense2/bias": net["b2"],
        "actor/logits/kernel": net["W3"], "actor/logits/bias": net["b3"],
    })


# ---------------------------------------------------------------- policy + env
def logits(net, x: np.ndarray) -> np.ndarray:
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    return h2 @ net["W3"] + net["b3"]


def make_obs_fn(env, game: str):
    chans = env.env.channels
    idx = [[chans[n] for n in srcs] for srcs in CHANNEL_MAP[game]]

    def obs() -> np.ndarray:
        s = env.state()  # (10, 10, C) bool
        o = np.zeros((10, 10, 6), dtype=np.float32)
        for c, src in enumerate(idx):
            if src:
                o[..., c] = s[..., src].any(axis=-1)
        return o.reshape(600)  # i = (row*10 + col)*6 + channel

    return obs


def _make_env(game: str, seed: int):
    from minatar import Environment

    env = Environment(game, sticky_action_prob=STICKY)
    env.seed(seed)
    env.reset()
    return env


def play_episode(net, game: str, seed: int, record: bool = False):
    """One episode. Returns (score, steps, frames)."""
    env = _make_env(game, seed)
    obs = make_obs_fn(env, game)
    rng = np.random.default_rng(seed + 1_000_003)
    score, frames = 0.0, []
    for t in range(MAX_STEPS):
        x = obs()
        if record:
            frames.append(x.reshape(10, 10, 6).copy())
        z = logits(net, x)
        p = np.exp(z - z.max())
        p /= p.sum()
        a = int(rng.choice(6, p=p))
        r, done = env.act(a)
        score += r
        if done:
            return score, t + 1, frames
    return score, MAX_STEPS, frames


def _worker(args):
    net, game, seeds = args
    return [play_episode(net, game, s)[:2] for s in seeds]


def evaluate(net, game: str, episodes: int = 1000, base_seed: int = 0, workers: int = 0) -> dict:
    import os
    from concurrent.futures import ProcessPoolExecutor

    seeds = list(range(base_seed, base_seed + episodes))
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    chunks = [seeds[i::workers] for i in range(workers)]
    with ProcessPoolExecutor(workers) as ex:
        results = [r for part in ex.map(_worker, [(net, game, c) for c in chunks]) for r in part]
    scores = np.array([r[0] for r in results])
    lens = np.array([r[1] for r in results])
    return {
        "mean": float(scores.mean()),
        "se": float(scores.std(ddof=1) / np.sqrt(len(scores))) if len(scores) > 1 else 0.0,
        "episodes": len(scores),
        "max": float(scores.max()),
        "mean_length": float(lens.mean()),
    }
