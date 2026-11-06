import json
from collections import Counter
res = json.load(open("deaths_claude_200.json"))
col = [r for r in res if r["kind"] in ("fish","enemy_sub","bullet")]
mv = [r for r in col if r["moved_vert"]]
print("vertical deaths by (surf_req, ea, sticky):", Counter((r["surf_req"], r["ea"], r["sticky"]) for r in mv).most_common())
sel = [r for r in mv if r["surf_req"] and r["ea"]=="up" and not r["sticky"]]
print("n", len(sel), "kinds", Counter(r["kind"] for r in sel), "rows", Counter((r["prev_row"], r["row"]) for r in sel))
print("sampled", Counter(r["sampled"] for r in sel))
sr = [r for r in col if not r["moved_vert"]]
def cells(x, f): return frozenset((x, x + 1) if f == "L" else (x - 1, x))
lr = [r for r in sr if r["ea"] in ("left","right")]
print("same-row deaths with executed L/R:", len(lr), "sticky among them:", sum(r["sticky"] for r in lr), "sampled:", Counter(r["sampled"] for r in lr))
cat = Counter()
for r in lr:
    pre = r["last"][-1]; px, pf, ea = pre[2], pre[3], r["ea"]
    nf = "L" if ea=="left" else "R"; nx = max(0,px-1) if ea=="left" else min(9,px+1)
    k = "turn" if cells(nx,nf)==cells(px,pf) else "shift"
    cat[(k, r["facing_killer_pre"], r["killer_pre_col"]-px, r["sticky"])] += 1
for k,v in sorted(cat.items(), key=lambda kv:-kv[1]): print(v, k)
print("unknown seeds:", [(r["seed"], r["t"], r["row"]) for r in res if r["kind"]=="unknown"])
print("all kinds:", Counter(r["kind"] for r in res))
