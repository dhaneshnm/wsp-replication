import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import pickle
from instr import run
res = pickle.load(open("episodes_claude_200.pkl", "rb"))
cap = [r for r in res if not r["done"]]
net = nets()["claude"]
for r in cap[:4]:
    full = run((net, r["seed"], True))
    t0, t1 = full["loop"]
    tr = full["trace"]
    print(f"seed {r['seed']} score {full['score']} loop first seen t={t0}, repeated t={t1}, last reward t={full['rewards_t'][-1]}, bricks left {full['bricks_end']}")
    seg = tr[t1:t1 + 36]
    print("  (row,col,dir)p<paddle> per step over one period:")
    print("  ", " ".join(f"({s['by']},{s['bx']},{s['d']})p{s['pos']}" for s in seg))
    print("   executed actions:", [s['exec'] for s in seg])
    # steps in the loop with non-noop executed actions over the remaining episode
    rest = tr[t1:]
    print("   after loop start: frac steps with executed move", np.mean([s['exec'] in (1,3) for s in rest]).round(4),
          " frac where sampled action != argmax", np.mean([s['a'] != s['amax'] for s in rest]).round(4))
