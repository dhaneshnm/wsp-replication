"""Independent check of claim 1 / claim 9.
(a) Rebuild the net by exec-ing every edits statement as plain numpy code (no wsp parser), compare to net.npz read raw.
(b) Probe layer-1 / layer-2 units on observations built by the REAL MinAtar env (inner state set by hand, obs via wsp.make_obs_fn).
"""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import re
import numpy as np
import wsp

A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/"
txt = open(A + "answer.md").read()
blk = re.split(r"```edits\n", txt)[-1].split("```")[0]
ns = dict(W1=np.zeros((600, 32)), b1=np.zeros(32), W2=np.zeros((32, 32)), b2=np.zeros(32), W3=np.zeros((32, 6)), b3=np.zeros(6))
n_stmt = 0
for line in blk.splitlines():
    s = line.split("#")[0].strip()
    if not s:
        continue
    exec(s, {}, ns)
    n_stmt += 1
raw = np.load(A + "net.npz")
keymap = {"W1": "actor/dense1/kernel", "b1": "actor/dense1/bias", "W2": "actor/dense2/kernel",
          "b2": "actor/dense2/bias", "W3": "actor/logits/kernel", "b3": "actor/logits/bias"}
print("statements exec'd:", n_stmt, "raw npz keys:", sorted(raw.files))
for k, rk in keymap.items():
    d = np.abs(ns[k].astype(np.float32) - raw[rk]).max()
    print(f"{k}: shape {raw[rk].shape} max|exec - npz| = {d}")
print("nonzero weights (exec):", sum(int((ns[k] != 0).sum()) for k in ns))

net = {k: ns[k].astype(np.float32) for k in ns}

# ---------- probes via the real environment ----------
env = wsp._make_env("asterix", 0)
inner = env.env
obsf = wsp.make_obs_fn(env, "asterix")


def state(py, ents):
    """ents: list of (row, col, moving_right, gold)"""
    inner.player_x, inner.player_y = 5, py
    inner.entities = [None] * 8
    for (r, c, lr, g) in ents:
        inner.entities[r - 1] = [c, r, lr, g]
    x = obsf()
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    return h1, h2, z


# Layer 1, row 3 features; enemy in row 3 at various columns/directions
print("\nLayer 1 (row 3 entity; player in row 6). cols: H1_3=unit10 H2_3=unit18 G_3=unit26")
print(" kind  dir  col dist  |  H1     H2     G")
for g in (False, True):
    for lr in (True, False):
        for c in range(10):
            dist = (5 - c) if lr else (c - 5)
            h1, _, _ = state(6, [(3, c, lr, g)])
            print(f" {'gold ' if g else 'enemy'} {'R' if lr else 'L'}   {c}   {dist:+d}   | {h1[10]:+.3f} {h1[18]:+.3f} {h1[26]:+.3f}")
h1, _, _ = state(6, [])
print(" empty row 3: H1 %+.3f H2 %+.3f G %+.3f" % (h1[10], h1[18], h1[26]))
print(" P units with player row 6:", h1[0:8].round(3))

# Layer 2: stay unit for player row 4 (unit 3), up unit (unit 11, target row 3), down unit (unit 19, target row 5)
print("\nLayer 2 gated units, player row 4: stay_4=unit3 (own row 4), up_4=unit11 (row 3), down_4=unit19 (row 5)")
cases = {
    "neutral(empty)": None,
    "immediate enemy col4 R": (4, True, False),
    "immediate enemy col5 R": (5, True, False),
    "immediate enemy col6 L": (6, False, False),
    "near enemy col3 R (d2)": (3, True, False),
    "near enemy col2 R (d3)": (2, True, False),
    "near enemy col7 L (d2)": (7, False, False),
    "near enemy col8 L (d3)": (8, False, False),
    "far enemy col1 R (d4)": (1, True, False),
    "far enemy col0 R (d5)": (0, True, False),
    "far enemy col9 L (d4)": (9, False, False),
    "passed enemy col6 R": (6, True, False),
    "passed enemy col8 R": (8, True, False),
    "gold col3 R": (3, True, True),
    "gold col1 R": (1, True, True),
    "gold col5 R": (5, True, True),
    "passed gold col7 R": (7, True, True),
}
for name, spec in cases.items():
    row = []
    for tgt, unit in ((4, 3), (3, 11), (5, 19)):
        ents = [] if spec is None else [(tgt, spec[0], spec[1], spec[2])]
        _, h2, _ = state(4, ents)
        row.append(h2[unit])
    print(f" {name:26s} stay {row[0]:+.3f}  up {row[1]:+.3f}  down {row[2]:+.3f}")

_, h2, z = state(4, [])
print("\ninactive gated units (player row 4): stay units", np.delete(h2[0:8], 3).round(3), "up", np.delete(h2[8:16], 3).round(3))
print("gold-dir units, empty board, player row 4:", h2[24:32].round(4))
for py in range(1, 9):
    _, h2, z = state(py, [])
    print(f" empty board player row {py}: goldDir_active {h2[23+py]:+.4f} logits n {z[0]:.3f} u {z[2]:.3f} d {z[4]:.3f} l/r/f {z[1]:.1f}/{z[3]:.1f}/{z[5]:.1f}  d-u {z[4]-z[2]:+.4f}")
