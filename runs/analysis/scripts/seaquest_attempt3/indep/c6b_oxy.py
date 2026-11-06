"""Reconcile window-veto count: how many vetoed window steps also had the row's Down unit on; sub column on veto steps."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
IN = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep/"
sys.path.insert(0, IN)
import pickle
from collections import Counter
import myrun


def summ(net, r):
    log = r.pop("log")
    on = [s["h1"][26] > 0 for s in log]
    t = len(log) - 1
    while t > 0 and on[t - 1]:
        t -= 1
    c = Counter()
    for i, s in enumerate(log):
        row = s["row"]
        if not on[i] or row < 2 or s["h2"][row - 1] > 0 or s["h1"][16 + row - 1] <= 0:
            continue
        dn = row <= 7 and s["h2"][8 + row] > 0
        c["veto_all_col%d" % s["col"]] += 1
        if i >= t:
            c["win_veto"] += 1; c["win_veto_down_on"] += dn
    return dict(seed=r["seed"], c=c)


if __name__ == "__main__":
    base = pickle.load(open(IN + "claude_0.1.pkl", "rb"))
    seeds = [r["seed"] for r in base if r["cause"] == "oxygen" and r["d_at_death"] >= 1]
    res = myrun.run_many(myrun.CLAUDE, seeds, detail_fn=summ)
    print(dict(sum((r["c"] for r in res), Counter())))
