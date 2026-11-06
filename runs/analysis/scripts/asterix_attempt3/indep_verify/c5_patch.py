# Rebuild the analyst's described 'two-row lookahead' patch from scratch as edits statements
# (Bk and T of row y-2 into U_y, of row y+2 into D_y, weight w, bias +2w), then score seeds 0..199.
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from concurrent.futures import ProcessPoolExecutor
w = 1.25
lines = []
for y in range(1, 9):
    U, D = 7 + y, 15 + y           # U_y unit index, D_y unit index
    if y - 2 >= 1:
        lines += [f"W2[{15 + y - 2}, {U}] += {w}", f"W2[{7 + y - 2}, {U}] += {w}", f"b2[{U}] += {2*w}"]
    if y + 2 <= 8:
        lines += [f"W2[{15 + y + 2}, {D}] += {w}", f"W2[{7 + y + 2}, {D}] += {w}", f"b2[{D}] += {2*w}"]
text = "```edits\n" + "\n".join(lines) + "\n```"
base = nets()["claude"]
P, rep = wsp.apply_edits(text, copy.deepcopy(base))
nw = sum(1 for l in lines if l.startswith("W2")); nb = sum(1 for l in lines if l.startswith("b2"))
print("patch statements:", rep.statements, "applied", rep.applied, "errors", rep.errors, "| weights", nw, "biases", nb)
print("changed entries:", int((P['W2'] != base['W2']).sum()), "W2;", int((P['b2'] != base['b2']).sum()), "b2")
E_ = lambda r, c, d: dict(r=r, c=c, kind="E", dir=d); G_ = lambda r, c, d: dict(r=r, c=c, kind="G", dir=d)
for lab, it in (("gold r4 c3->, enemy r3 c5", [G_(4, 3, 1), E_(3, 5, 1)]), ("gold r4 c3-> only", [G_(4, 3, 1)]), ("empty", [])):
    print(f"  {lab:28s} orig p(n,u,d)={np.round(layers(base, board(5, it))[3][[0,2,4]], 3)} patched={np.round(layers(P, board(5, it))[3][[0,2,4]], 3)}")
def job(seed):
    o = episode(P, seed, sticky=0.1); return o["score"], o["steps"]
if __name__ == "__main__":
    with ProcessPoolExecutor(4) as ex:
        r = list(ex.map(job, range(200), chunksize=5))
    sc = np.array([x[0] for x in r]); L = np.array([x[1] for x in r])
    print(f"patched (my loop) seeds 0..199: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(200):.3f} mean_len {L.mean():.2f}")
    print("patched (wsp.evaluate):", wsp.evaluate(P, "asterix", episodes=200, workers=4))
