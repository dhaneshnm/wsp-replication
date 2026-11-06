"""Claim 10: up-logit contribution of each Up unit, logits in constructed row-2 states, and score with W3[1,2]=10."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep")
import numpy as np, wsp, myrun
net = wsp.load_npz(myrun.CLAUDE)
W3, b3 = net["W3"], net["b3"]
print("W3[0:8, 2] =", W3[0:8, 2], " W3[18,2] =", W3[18, 2], " b3 =", b3)
for j in range(8):
    h2 = -np.ones(32); h2[j] = 1.0
    print(f"  only Up unit {j} (sub row {j+1}) on, BLOCK off: up logit = {float(h2 @ W3[:, 2] + b3[2]):.1f}; down {float(h2 @ W3[:, 4] + b3[4]):.1f}; fire {float(h2 @ W3[:, 5] + b3[5]):.1f}")
h2 = -np.ones(32); h2[1] = 1; h2[10] = 1
z = h2 @ W3 + b3; p = np.exp(z - z.max()); p /= p.sum()
print("  Up_2 and Down_2 both on: logits", z.round(1), "p(up)", round(float(p[2]), 4), "p(down)", round(float(p[4]), 4))
env = wsp._make_env("seaquest", 0); E = env.env


def show(lab, **kw):
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen = 8, 2, False, kw.get("oxy", 150)
    E.diver_count = kw.get("d", 0)
    E.divers = kw.get("divers", []); E.e_fish = kw.get("fish", [])
    h1, h2, z = myrun.forward(net, myrun.obs_vec(E))
    p = np.exp(z - z.max()); p /= p.sum()
    print(f"  {lab}: Up_2 {h2[1]:+.2f} Down_2 {h2[10]:+.2f} logits(n,l,u,r,d,f) {np.round(z,1)} p(up) {p[2]:.3f}")


show("row 2, d=2 oxy 30 (SURF on), row 1 empty", d=2, oxy=30)
show("row 2, d=2 oxy 150, approaching diver row 1 col 3", d=2, divers=[[3, 1, True, 5]])
show("row 2, d=2, fish in own row col 9 (must leave), rows 1,3 empty", d=2, fish=[[9, 2, False, 5]])
if __name__ == "__main__" and len(sys.argv) > 1:
    v = {k: a.copy() for k, a in net.items()}; v["W3"][1, 2] = 10
    print("W3[1,2]=10 variant:", wsp.evaluate(v, "seaquest", episodes=200, workers=4))
