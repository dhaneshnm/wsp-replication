# Does the reply's "at least 3 steps to spare" fail when the paddle HAS reached the up-phase target?
import pickle, collections
res = pickle.load(open("play_claude_200.pkl", "rb"))
Rl = [r for e in res for r in e["rallies"]]
tab = collections.Counter()
low_detail = collections.Counter()
for r in Rl:
    s = r["desc_len"] - abs(r["desc_pos"] - r["x8"])
    if r["fd"] == 0:
        key = "episode start (no rise)"
    elif r.get("up_target") is None:
        key = "net did not read last rising frame as rising"
    else:
        key = "paddle at up-target at turn" if r["desc_pos"] == r["up_target"] else "paddle NOT at up-target at turn"
    tab[(key, s < 3)] += 1
    if s < 3 and key == "paddle at up-target at turn":
        low_detail[(r["turn_row"], r["up_target"] - r["x8"], r["desc_len"], s)] += 1
for k in sorted(tab): print(k, tab[k])
print("slack<3 cases with paddle at up-target (turn_row, err, desc_len, slack):", dict(low_detail))
# minimum slack among rallies where the paddle sat at the up-target at the turn
m = collections.Counter(r["desc_len"] - abs(r["desc_pos"] - r["x8"]) for r in Rl if r.get("up_target") is not None and r["desc_pos"] == r["up_target"])
print("slack distribution when paddle at up-target:", sorted(m.items()))
# rally-start slack among the slack<3 rallies not at target
st = collections.Counter(min(r["slack0"], 12) for r in Rl if r["desc_len"] - abs(r["desc_pos"] - r["x8"]) < 3 and r.get("up_target") is not None and r["desc_pos"] != r["up_target"])
print("rally-start slack0 (vs catch set) of slack<3 rallies with paddle not at target:", sorted(st.items()))
