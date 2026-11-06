import json, sys
from collections import Counter
import numpy as np

D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt3/refute/"


def summary(fn):
    R = json.load(open(D + fn))
    sc = np.array([r["score"] for r in R]); st = np.array([r["steps"] for r in R])
    print("=====", fn)
    print("episodes", len(R), "mean", sc.mean(), "se", sc.std(ddof=1) / np.sqrt(len(sc)), "capped", int((st == 10000).sum()),
          "min/max score", sc.min(), sc.max(), "total steps", int(st.sum()), "points/step", sc.sum() / st.sum())
    ral = [x for r in R for x in r["rallies"]]
    turn = [x for x in ral if not x["start_ep"]]
    miss = [x for x in ral if not x["caught"]]
    print("catch events (all rallies incl. episode-start descents)", len(ral), "| with a turn", len(turn),
          "| misses", len(miss), "| misses/rally (all)", len(miss) / len(ral), "| misses/turn-rally", len(miss) / max(1, len(turn)))
    print("misses that are episode-start descents", sum(x["start_ep"] for x in miss))
    print("turn rows (turn rallies):", sorted(Counter(x["turn_row"] for x in turn).items()))
    print("turn rows (all, start counted at its row):", sorted(Counter(x["turn_row"] for x in ral).items()))
    ud = Counter(x["up_diff"] for x in turn if x["up_diff"] is not None)
    print("last-rising-frame up-table target - x8 (true dx):", sorted(ud.items()), "n", sum(ud.values()))
    a = Counter(abs(k) for k in ud.elements())
    print("   |diff|:", sorted(a.items()))
    udr = Counter(x["up_diff_read"] for x in turn if x["up_diff_read"] is not None)
    print("last-rising-frame target - x8 (dx as read by net):", sorted(udr.items()))
    sl = Counter(x["slack"] for x in turn)
    print("slack = actions(turn..catch) - |p_turn - x8|, turn rallies:", sorted(sl.items()))
    print("   slack<3:", sum(v for k, v in sl.items() if k < 3), "of", len(turn))
    sl_all = Counter(x["slack"] for x in ral)
    print("   slack<3 incl start rallies:", sum(v for k, v in sl_all.items() if k < 3), "of", len(ral))
    print("walk c2->x8 in rally: all", sum(x["walk"] > 0 for x in ral), "of", len(ral), "| turn rallies", sum(x["walk"] > 0 for x in turn), "of", len(turn),
          "| walk by policy (non-sticky)", sum(x["walk_pol"] > 0 for x in ral))
    print("exits from catch set: sticky", sum(x["sticky_exit"] for x in ral), "policy", sum(x["policy_exit"] for x in ral))
    # miss classification
    cls = Counter()
    for m in miss:
        ev = m["events"]
        # walk followed (later) by a sticky exit
        wk = [e for e in ev if e[0] == "walk"]
        ex = [e for e in ev if e[0] == "exit"]
        walk_then_sticky = any(w[1] < x[1] and x[2] for w in wk for x in ex)
        if walk_then_sticky:
            cls[("walk+sticky_exit", "slack", m["slack"])] += 1
        else:
            cls[("other", "slack", m["slack"], "slack_set", m["slack_set"], "exits", len(ex), "walks", len(wk), "start_ep", m["start_ep"])] += 1
    for k, v in sorted(cls.items(), key=lambda kv: -kv[1]):
        print("   miss class", k, v)
    print("   walk+sticky total:", sum(v for k, v in cls.items() if k[0] == "walk+sticky_exit"))
    reps = [r["replay"] for r in R if r["replay"]]
    print("greedy no-sticky replays of missed rallies:", len(reps),
          "from rally start caught:", sum(1 for r in reps if r["rally_start"] is True),
          "from turn caught:", sum(1 for r in reps if r["turn"] is True),
          "nosnap:", sum(1 for r in reps if "nosnap" in r.values()))
    mis = Counter()
    for r in R:
        for k, v in r["mis"].items():
            mis[k] += v
    print("misread frames by (unit, frame type, ball row):", sorted(mis.items(), key=lambda kv: -kv[1]), "total", sum(mis.values()))
    return R


for fn in sys.argv[1:]:
    summary(fn)
