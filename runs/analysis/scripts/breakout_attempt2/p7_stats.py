import json, numpy as np, sys
from collections import Counter
for tag in sys.argv[1:]:
    res=json.load(open(f"eps_{tag}.json"))
    lands=[l for r in res for l in r["lands"]]
    caught=[l for l in lands if l["caught"]]; miss=[l for l in lands if not l["caught"]]
    sc=np.array([r["score"] for r in res]); st=np.array([r["steps"] for r in res])
    print(f"== {tag}: eps {len(res)} mean {sc.mean():.1f} capped {sum(r['capped'] for r in res)} mean_len {st.mean():.0f}")
    print(f"  landings {len(lands)}  misses {len(miss)}  miss rate/landing {len(miss)/len(lands):.4f}  steps/landing {st.sum()/len(lands):.2f}  bricks/step {sc.sum()/st.sum():.4f}")
    capped=[r for r in res if r['capped']]
    if capped: print("  capped-episode score mean", np.mean([r['score'] for r in capped]), "min",min(r['score'] for r in capped),"max",max(r['score'] for r in capped))
    print("  reversal catches fraction of catches", np.mean([l["reversal"] for l in caught]).round(4))
    # classify misses
    cls=Counter()
    for l in miss:
        feas = l["d_any"] <= l["n_act"]
        feas_s = l["d_straight"] <= l["n_act"]
        cls[("feasible_any" if feas else "INFEASIBLE", "sticky_in_descent>0" if l["sticky_desc"]>0 else "no_sticky_in_descent")]+=1
    print("  miss classes:",dict(cls))
    # final-step info for misses
    fin=Counter()
    for l in miss:
        off=l["final_pos"]-l["x8"]
        side = "behind(opposite dx)" if np.sign(off)==-l["dx"] else "ahead(dx side)"
        fin[(off*l["dx"], "last-step sticky" if l["exec"]!=l["a"] else "last-step as chosen", "chosen a=%d exec=%d"%(l["a"],l["exec"]))]+=1
    print("  miss final offset (signed by dx; -1=one behind, +2=two ahead) x last-step:",)
    for k,v in sorted(fin.items(), key=lambda kv:-kv[1])[:12]: print("     ",k,v)
    print("  ascent top row before final descent, misses:",dict(sorted(Counter(l["asc_top"] for l in miss).items())))
    print("  ascent top row, all landings:",dict(sorted(Counter(l["asc_top"] for l in lands).items())))
    print("  miss rate by ascent top row:",{h: round(sum(1 for l in miss if l['asc_top']==h)/max(1,sum(1 for l in lands if l['asc_top']==h)),4) for h in sorted(set(l['asc_top'] for l in lands))})
    print("  descent-start slack (n_act - d_straight) at misses:",dict(sorted(Counter(l["n_act"]-l["d_straight"] for l in miss).items())))
    print("  descent-start slack (n_act - d_straight) at all landings:",dict(sorted(Counter(l["n_act"]-l["d_straight"] for l in lands).items())))
    print("  sticky steps fraction of steps:", sum(r['sticky_steps'] for r in res)/st.sum())
