import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, numpy as np
res = pickle.load(open("stats_claude_softmax_0.1_200.pkl", "rb"))
fs = np.array([r["first_drought_score"] for r in res]); fd = np.array([r["first_drought_t"] for r in res])
sc = np.array([r["score"] for r in res]); done = np.array([r["done"] for r in res]); ln = np.array([r["len"] for r in res])
print("first drought score counts:", dict(zip(*np.unique(fs, return_counts=True))))
m = fs == 21
print(f"episodes whose first >100-step drought began at score 21: {m.sum()}, their mean final score {sc[m].mean():.2f}, ended by miss {done[m].sum()}, at cap {(~done[m].astype(bool)).sum()}")
print(f"  of those, final score exactly 21: {(sc[m]==21).sum()}, >21: {(sc[m]>21).sum()}")
nod = fs < 0
print(f"episodes with no >100-step drought: {nod.sum()}, mean score {sc[nod].mean() if nod.any() else None}, mean len {ln[nod].mean() if nod.any() else None}")
