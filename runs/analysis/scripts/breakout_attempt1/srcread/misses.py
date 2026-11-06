import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import pickle
from collections import Counter
DIRV = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}
MOVE = {0: 0, 1: -1, 2: 0, 3: 1, 4: 0, 5: 0}

def net_target(net, s):
    """paddle columns where argmax action is no-op, for the step's observation"""
    out = []
    for p in range(10):
        x = make_obs((s["by"], s["bx"]), (s["ly"], s["lx"]), p)
        h1, h2, z, pr = forward(net, x)
        if int(np.argmax(pr)) == 0: out.append(p)
    return out

def feasible(pos, C, k):
    return min(abs(pos - c) for c in C) <= k

which = sys.argv[1]
net = nets()[which]
res = pickle.load(open(f"episodes_{which}_200.pkl", "rb"))
cls = Counter(); details = []
gate_err_at_dec = Counter(); lastflight = Counter()
for r in [r for r in res if r["done"]]:
    tr = r["trace"]
    # per-step catch set and steps remaining
    for s in tr:
        bx8, nx, k = s["land"]
        s["C"] = {bx8, nx}; s["k"] = k
    fin = tr[-1]
    assert fin["k"] == 1, fin
    # walk back to last feasible step
    tstar = None
    for i in range(len(tr) - 1, -1, -1):
        if feasible(tr[i]["pos"], tr[i]["C"], tr[i]["k"]):
            tstar = i; break
    if tstar is None or tr[tstar]["C"] != fin["C"]:
        # infeasible since start of this flight
        # find first step of this flight
        j = len(tr) - 1
        while j > 0 and tr[j - 1]["C"] == fin["C"] and tr[j-1]["k"] == tr[j]["k"] + 1: j -= 1
        cls["infeasible from start of flight"] += 1
        details.append((r["seed"], "infeasible-from-flight-start", tr[j]))
        continue
    s = tr[tstar]
    k = s["k"]; C = s["C"]; pos = s["pos"]
    def keeps(a):
        p2 = min(9, max(0, pos + MOVE[a]))
        return feasible(p2, C, k - 1) if k > 1 else (p2 in C)
    vx, vy = DIRV[s["d"]]
    gH_ok = np.sign(s["h1"][4]) == vx; gV_ok = np.sign(s["h1"][5]) == vy
    T = net_target(net, s)
    if keeps(s["amax"]) and not keeps(s["a"]):
        c = "sampling (sampled action != argmax)"
    elif keeps(s["a"]) and not keeps(s["exec"]):
        c = "sticky action repeated previous move"
    elif not keeps(s["amax"]):
        if not (gH_ok and gV_ok):
            c = "net argmax wrong: direction gate misread (" + ("gH" if not gH_ok else "") + ("gV" if not gV_ok else "") + ")"
        elif not (set(T) & C):
            c = "net argmax wrong: gates right but target not a catch column"
        else:
            c = "net argmax wrong: other"
    else:
        c = "other"
    cls[c] += 1
    details.append((r["seed"], c, dict(t=s["t"], ball=(s["by"], s["bx"]), trail=(s["ly"], s["lx"]), dir=s["d"], pos=pos, C=sorted(C), k=k, a=s["a"], amax=s["amax"], exec=s["exec"], T=T, gH=float(s["h1"][4]), gV=float(s["h1"][5]))))
    lastflight[k] += 1
print(which, "miss episodes:", sum(cls.values()))
for c, n in cls.most_common(): print(f"  {n:4d}  {c}")
print("  steps-to-landing k at the decisive step:", sorted(lastflight.items()))
pickle.dump(details, open(f"miss_details_{which}.pkl", "wb"))
for d in details[:12]: print("  ", d)
