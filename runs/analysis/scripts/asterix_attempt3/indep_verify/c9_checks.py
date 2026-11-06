# Layer-2 gates / output priorities on all real-play states (Claude, seeds 0..199) vs ground truth from entities,
# plus empty-board logits and how often the edge-spawn gold case occurs.
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
C = nets()["claude"]
NM = ["noop","left","up","right","down","fire"]
for pr in (5, 1, 8):
    a1, a2, z, p = layers(C, board(pr, []))
    print(f"empty board row {pr}: logits n/u/d = {z[0]:+.3f}/{z[2]:+.3f}/{z[4]:+.3f}  S={a2[pr-1]:+.4f} U={a2[7+pr]:+.3f} D={a2[15+pr]:+.3f} V={a2[23+pr]:+.3f}  p(n,u,d)={np.round(p[[0,2,4]],3)}")
res = pickle.load(open("my_inst_claude.pkl", "rb"))
X = []; Y = []; ENTS = []
for R in res:
    for s in R["log"]:
        g = type("G", (), {})(); g.player_y = s["py"]; g.player_x = s["px"]; g.entities = s["ents"]
        X.append(obs_from_game(g)); Y.append(s["py"]); ENTS.append(s["ents"])
X = np.stack(X); Y = np.array(Y)
A1 = np.tanh(X @ C["W1"] + C["b1"]); A2 = np.tanh(A1 @ C["W2"] + C["b2"]); Z = A2 @ C["W3"] + C["b3"]
P = np.exp(Z - Z.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
n = len(Y); print("real states:", n)
act = np.zeros((n, 32), bool)
for i, y in enumerate(Y): act[i, [y-1, 7+y, 15+y, 23+y]] = True
print("inactive L2 units: max", float(A2[~act].max()), "min", float(A2[~act].min()))
def truth(ents):
    T = np.zeros(10, bool); B = np.zeros(10, bool); G = np.zeros(10, bool); Gspawn = np.zeros(10, bool)
    for e in ents:
        if e is None: continue
        x, r, right, gold = e
        if gold:
            G[r] = x == 5 or (right and x < 5) or ((not right) and x > 5)
            Gspawn[r] = (right and x == 0) or ((not right) and x == 9)
        else:
            T[r] = (right and x in (3, 4)) or ((not right) and x in (6, 7))
            B[r] = x == 5 or (right and x == 4) or ((not right) and x == 6)
    return T, B, G, Gspawn
mis = dict(T=0, Bk=0, G=0, G_spawn_cases=0, U=0, D=0, S_sign=0)
pri = dict(enter_blocked_maxp=0.0, threat_free_neighbour_noop_maxp=0.0, steps_with_spawn_gold=0)
for i in range(n):
    T, B, G, Gs = truth(ENTS[i]); y = Y[i]
    mis["T"] += int(((A1[i, 8:16] > 0) != T[1:9]).sum())
    mis["Bk"] += int(((A1[i, 16:24] > 0) != B[1:9]).sum())
    gm = (A1[i, 24:32] > 0) != G[1:9]
    mis["G"] += int(gm.sum()); mis["G_spawn_cases"] += int((gm & Gs[1:9]).sum())
    pri["steps_with_spawn_gold"] += int(Gs.any())
    upb = (y == 1) or B[y-1]; dnb = (y == 8) or B[y+1]
    mis["U"] += int((A2[i, 7+y] > 0) != upb); mis["D"] += int((A2[i, 15+y] > 0) != dnb)
    s = A2[i, y-1]; want = 1 if T[y] else (-1 if G[y] else 0)
    mis["S_sign"] += int((want == 1 and s < 0.5) or (want == -1 and s > -0.5) or (want == 0 and abs(s) > 0.5))
    if y > 1 and B[y-1]: pri["enter_blocked_maxp"] = max(pri["enter_blocked_maxp"], P[i, 2])
    if y < 8 and B[y+1]: pri["enter_blocked_maxp"] = max(pri["enter_blocked_maxp"], P[i, 4])
    if T[y] and ((y > 1 and not B[y-1]) or (y < 8 and not B[y+1])):
        pri["threat_free_neighbour_noop_maxp"] = max(pri["threat_free_neighbour_noop_maxp"], P[i, 0])
print("mismatches (state x row) vs answer.md rules:", mis)
print("priorities:", {k: (round(float(v), 4) if isinstance(v, float) else v) for k, v in pri.items()}, "of", n, "states")
