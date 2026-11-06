import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
import json
path=sys.argv[1]; tag=sys.argv[2]; nshow=int(sys.argv[3])
net=wsp.load_npz(path)
res=json.load(open(f"eps_{tag}.json"))
shown=0
for r in res:
    if r["capped"]: continue
    s=r["seed"]
    score,steps,L=run(net,s,log=True)
    # find last landing before the miss
    i=len(L)-1
    k=i-1
    while k>0 and not (L[k]["by"]==8 and DY[L[k]["dir"]]>0): k-=1
    print(f"--- seed {s} score {score} miss at t={L[i]['t']}  (previous landing t={L[k]['t']})")
    for m in range(k,i+1):
        x=L[m]; da=None
        class _E: pass
        e=_E(); e.ball_dir=x["dir"]; e.ball_x=x["bx"]; e.ball_y=x["by"]; e.pos=x["pos"]
        da,T=design_action(e)
        print(f"   t{x['t']} ball=({x['by']},{x['bx']}) dir={'UL UR DR DL'.split()[x['dir']]} trail=({x['ly']},{x['lx']}) pos={x['pos']} T={T} chose={x['a']} exec={x['exec']}{' STICKY' if x['exec']!=x['a'] else ''} -> pos {x['pos_after']}")
    shown+=1
    if shown>=nshow: break
