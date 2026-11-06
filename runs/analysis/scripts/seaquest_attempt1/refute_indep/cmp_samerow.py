import json, pickle, os
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
for name in ("claude", "astra"):
    mine = pickle.load(open(f"{H}/roll_{name}_200.pkl", "rb"))
    theirs = {r["seed"]: r for r in json.load(open(f"{H}/../deaths_{name}_200.json"))}
    diff = Counter()
    ex = []
    for e in mine:
        d = e["death"]
        if d is None: continue
        if d["pre_y"] > 0 and d["post_y"] == 0 and d["pre_dc"] == 0: mk = "empty"
        elif d["pre_oxy"] <= 0: mk = "oxygen"
        else: mk = "same" if d["post_y"] == d["pre_y"] else "vert"
        tr = theirs[e["seed"]]
        tk = tr["kind"]
        if tk in ("fish", "enemy_sub", "bullet"): tk = "vert" if tr["moved_vert"] else "same"
        diff[(mk, tk)] += 1
        if mk != tk and len(ex) < 12: ex.append((e["seed"], mk, tk, d["pre_y"], d["post_y"], d["pre_x"], d["post_x"], d["ea"], d["fish"], d["subs"], d["bul"], d["post_fish"], d["post_subs"]))
    print(name, sorted(diff.items()))
    for x in ex: print("  ", x)
