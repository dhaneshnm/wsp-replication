import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stay_deaths import build_obs, res, det, fwd, NET, ACT
from astra_deaths import board
ds=[d for d in det if d["cat"]=="stayed: sticky repeat overrode a dodge"][:2]
for d in ds:
    L=res[d["seed"]]["log"]
    for s in L[-3:]:
        h1,h2,z,p=fwd(NET,build_obs(s["py"],s["ents"]))
        y=s["py"]-1
        print(f"seed {d['seed']} t={s['t']} py={s['py']} move_timer={s['move_timer']} sampled={ACT[s['a']]} exec={ACT[s['exec']]} sticky={s['sticky']} S={h2[y]:+.2f} T_row={h1[8+y]:+.2f} p={[round(v,3) for v in s['p']]}")
        print(board(s["py"],[e for e in s["ents"]]))
