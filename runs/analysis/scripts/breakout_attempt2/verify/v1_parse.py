import sys, re
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *

txt = open(ANSWER).read()
blocks = re.findall(r"```edits\n(.*?)```", txt, re.S)
print("edits blocks:", len(blocks))
code = blocks[-1]
# independent executor: the edits are valid numpy/Python statements -> exec them directly
ns = {k: np.zeros(s, np.float32) for k, s in wsp.SHAPES.items()}
exec(code, {}, ns)
net = wsp.load_npz(CLAUDE)
for k in ["W1", "b1", "W2", "b2", "W3", "b3"]:
    print(k, "exec==npz:", np.array_equal(ns[k], net[k]), "nonzero", int((net[k] != 0).sum()))
net2, rep = wsp.apply_edits(txt)
print("wsp.apply_edits statements", rep.statements, "applied", rep.applied, "errors", rep.errors)
print("apply_edits==npz all:", all(np.array_equal(net2[k], net[k]) for k in net))

W1 = net["W1"]
def ballw(u): return np.array([[W1[(r*10+c)*6+3, u] for c in range(10)] for r in range(10)])
def padw(u): return np.array([W1[(90+c)*6+0, u] for c in range(10)])
T = design_tables()
names = {0: ("D+", 1), 1: ("D+", -1), 2: ("D-", 1), 3: ("D-", -1), 4: ("U+", 1), 5: ("U+", -1), 6: ("U-", 1), 7: ("U-", -1)}
for u, (nm, sgn) in names.items():
    tab = ballw(u) / (10 * sgn)
    mism = int((tab[:9] != T[nm][:9]).sum())
    row9 = tab[9].astype(int).tolist()
    other = W1[:, u].copy()
    other[3::6] = 0; other[540::6][:10] = 0
    print(f"unit {u} {nm} sign {sgn:+d}: rows0-8 mismatches vs formula = {mism}; row9 = {row9}; formula row9 = {T[nm][9].tolist()}; "
          f"paddle w = {padw(u).astype(int).tolist()}; bias {net['b1'][u]}; other nonzero = {int((other!=0).sum())}")
