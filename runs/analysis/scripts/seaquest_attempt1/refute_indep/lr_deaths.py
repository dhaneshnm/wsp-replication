import os, pickle
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
A = ["noop", "left", "up", "right", "down", "fire"]
R = pickle.load(open(os.path.join(H, "roll_claude_200.pkl"), "rb"))
def cells(x, right): return frozenset((x - 1, x) if right else (x, x + 1))
cat = Counter()
for e in R:
    d = e["death"]
    if d is None or d["ea"] not in (1, 3): continue
    stay_ok = (not d["alt_terminal"][5]) or (not d["alt_terminal"][0])
    moved = cells(d["pre_x"], d["pre_right"]) != cells(d["post_x"], d["ea"] == 3)
    kind = "shift" if moved else ("turn" if d["pre_right"] != (d["ea"] == 3) else "noeffect")
    cat[(kind, "stay_survives" if stay_ok else "stay_dies")] += 1
    if not stay_ok:
        print(e["seed"], A[d["ea"]], "pre", (d["pre_y"], d["pre_x"], "R" if d["pre_right"] else "L"), "post x", d["post_x"],
              "alt_terminal", {A[k]: v for k, v in d["alt_terminal"].items()}, "fish", d["fish"], "subs", d["subs"], "bul", d["bul"])
print(sorted(cat.items()))
