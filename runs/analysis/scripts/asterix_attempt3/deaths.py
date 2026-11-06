import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
which=sys.argv[1]
res = pickle.load(open(f"inst_{which}_200.pkl","rb"))
DY={0:0,1:0,2:-1,3:0,4:1,5:0}
cats=Counter(); speeds=Counter(); rows=Counter(); detail=[]
for R in res:
    if not R["done"]: continue
    s = R["log"][-1]; ents=s["ents"]; y0=s["py"]; ex=s["exec"]; a=s["a"]
    y1 = min(8,max(1,y0+DY[ex])); moved = y1!=y0
    em = s["move_timer"]==0
    killer=None
    for e in ents:
        if e is None or e[3] or e[1]!=y1: continue
        if e[0]==5: killer=("at5",e)
        elif em and ((e[0]==4 and e[2]) or (e[0]==6 and not e[2])): killer=("approach",e)
    # escape options from y0 in this step (ground truth with this step's move timer)
    def ok(r): return 1<=r<=8 and r!=y0 and not row_blocked(ents, r, em)
    esc_up = ok(y0-1); esc_dn = ok(y0+1)
    stay_safe = not row_blocked(ents, y0, em)
    sticky_changed = s["sticky"] and ex!=a
    p=s["p"]
    if not moved:
        if not (esc_up or esc_dn): c="stayed: no safe neighbour (trapped)"
        elif sticky_changed: c="stayed: sticky repeat overrode a dodge"
        else: c=f"stayed: policy sampled stay though escape open"
    else:
        if sticky_changed: c="moved into deadly row: sticky repeat"
        elif not stay_safe and not (esc_up or esc_dn): c="moved: all options deadly"
        else: c="moved into deadly row: policy choice"
    cats[c]+=1; speeds[s["move_speed"]]+=1; rows[y0]+=1
    detail.append(dict(seed=R["seed"], t=s["t"], y0=y0, a=a, ex=ex, sticky=s["sticky"], cat=c, killer=killer,
                       p=[round(v,3) for v in p], ms=s["move_speed"], ss=s["spawn_speed"], em=em,
                       esc_up=esc_up, esc_dn=esc_dn))
n=sum(cats.values())
print(which, "deaths:", n)
for k,v in cats.most_common(): print(f"  {v:4d} ({100*v/n:4.1f}%)  {k}")
print(" killer kind:", Counter(d["killer"][0] if d["killer"] else None for d in detail))
print(" move_speed at death:", sorted(speeds.items()))
print(" player row at death:", sorted(rows.items()))
print(" death step quantiles:", np.percentile([d['t'] for d in detail],[10,25,50,75,90]))
pickle.dump(detail, open(f"deaths_{which}.pkl","wb"))
for d in detail[:6]: print(d)
