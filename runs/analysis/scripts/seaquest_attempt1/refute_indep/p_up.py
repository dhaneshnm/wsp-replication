import os, pickle, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R = pickle.load(open(os.path.join(H, "roll_claude_200.pkl"), "rb"))
v = [e["steps"][-1]["pa"][2] for e in R if e["death"] and e["death"]["ea"] == 2 and e["death"]["a"] == 2 and e["death"]["pre_oxy"] < 60 and e["death"]["pre_dc"] >= 1]
print("n", len(v), "p(up)>=0.9:", sum(x >= 0.9 for x in v), " >=0.5:", sum(x >= 0.5 for x in v))
