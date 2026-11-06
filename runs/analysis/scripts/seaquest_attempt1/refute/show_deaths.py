import json, sys
from collections import Counter
res = json.load(open(sys.argv[1]))
sel = [r for r in res if r["kind"] in ("fish","enemy_sub","bullet") and not r["moved_vert"] and r["ea"] == sys.argv[2]]
print(len(sel))
print("pre facing / killer side / killer col:", Counter((r["pre_facing"], r["killer_side"], r["killer_pre_col"]) for r in sel).most_common(12))
for r in sel[:int(sys.argv[3])]:
    print("seed", r["seed"], "t", r["t"], r["kind"], "row", r["row"], "pre_facing", r["pre_facing"], "killer col", r["killer_pre_col"], "side", r["killer_side"], "sampled", r["sampled"], "sticky", r["sticky"])
    for h in r["last"]:
        print("    t=%d row=%d front=%d face=%s act=%s shot=%d fish=%s esub=%s ebul=%s fbul=%s" % tuple(h))
