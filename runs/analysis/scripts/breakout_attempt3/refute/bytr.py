import json, sys
from collections import Counter, defaultdict
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt3/refute/"
for fn in sys.argv[1:]:
    R = json.load(open(D + fn))
    ral = [x for r in R for x in r["rallies"] if not x["start_ep"]]
    by = defaultdict(Counter); sl = defaultdict(Counter)
    for x in ral:
        by[x["turn_row"]][abs(x["up_diff"])] += 1
        sl[x["turn_row"]][x["slack"]] += 1
    print("==", fn)
    for r in sorted(by):
        print(" turn row", r, "|up target - x8| :", sorted(by[r].items()), "| slack:", sorted(sl[r].items()))
    # slack<3: is the paddle at the turn where the up table pointed (p0 - x8 == up_diff)?
    lo = [x for x in ral if x["slack"] < 3]
    at = Counter((x["turn_row"], x["p0"] - x["x8"] == x["up_diff"]) for x in lo)
    print(" slack<3 rallies by (turn row, paddle at turn == last up target):", sorted(at.items()))
