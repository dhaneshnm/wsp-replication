import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
res = pickle.load(open("inst_claude_200.pkl","rb"))
det = pickle.load(open("deaths_claude.pkl","rb"))
DY={0:0,1:0,2:-1,3:0,4:1,5:0}
# categories for 'stayed: sticky repeat overrode a dodge': executed action
print("sticky-stay deaths exec actions:", Counter(d["ex"] for d in det if d["cat"].startswith("stayed: sticky")))
print("sticky-stay deaths (exec,row):", Counter((d["ex"],d["y0"]) for d in det if d["cat"].startswith("stayed: sticky")))
print("trapped: sticky flag & exec!=a:", Counter((d["sticky"] and d["ex"]!=d["a"], d["ex"]) for d in det if d["cat"].startswith("stayed: no safe")))
# 169 cases
for R in res:
    if not R["done"]: continue
    L=R["log"]; s=L[-1]
    if not (s["sticky"] and s["exec"]!=s["a"] and s["exec"] in (2,4)): continue
    q=L[-2]; y=q["py"]; d=DY[q["exec"]]; r2=y+2*d
    moved_t = s["py_after"]!=s["py"]; moved_q = q["py_after"]!=q["py"]
    dang=any(e is not None and not e[3] and e[1]==r2 and (e[0]==5 or (e[2] and e[0] in (3,4)) or ((not e[2]) and e[0] in (6,7))) for e in q["ents"])
    if not dang or not moved_t or not moved_q:
        print("seed",R["seed"],"q.py",q["py"],"q.exec",q["exec"],"q.py_after",q["py_after"],"s.py",s["py"],"s.exec",s["exec"],"s.py_after",s["py_after"],"r2",r2,"dang",dang, "q sticky-changed", q["sticky"] and q["exec"]!=q["a"])
# among 169, how many t-1 moves were sticky themselves and did they have dang?
