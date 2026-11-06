import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from collections import Counter
d = pickle.load(open("miss_details_claude.pkl", "rb"))
early = [x for x in d if isinstance(x[2], dict) and x[2]["t"] < 166]
print("Claude misses decided before t=166:", len(early))
print(Counter((x[1], x[2]["k"]) for x in early))
for x in early[:10]: print("  ", x[0], x[1], {k: x[2][k] for k in ("t","ball","trail","pos","C","k","a","amax","exec","T")})
late = [x for x in d if isinstance(x[2], dict) and x[2]["t"] >= 166]
print("misses decided at t>=166:", len(late), Counter((x[1], x[2]["k"]) for x in late))
