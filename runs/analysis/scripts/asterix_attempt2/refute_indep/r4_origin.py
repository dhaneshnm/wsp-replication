"""Claim 4 follow-up: for each sticky-vertical death (from run_claude_200.pkl), replay to step T-1 and record
the status of the row the player moved INTO at T-1, and whether approaching gold existed on that side.
Also claim 10 follow-up: p on fatal pairs that had a safe alternative, by squeeze type (seeds 0..99 logs)."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep")
import pickle, collections
import numpy as np
import wsp
from r2_runner import own_row_status, NETS

D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep/"
C = pickle.load(open(D + "run_claude_200.pkl", "rb"))
net = wsp.load_npz(NETS["claude"])

tgt = collections.Counter(); gold_side = collections.Counter(); combo = collections.Counter()
for r in C:
    s = r["last3"][-1]
    if not (s["eff"] != s["a"] and s["eff"] in (2, 4) and not s["F"][s["a"]]):
        continue
    T = s["t"]
    env = wsp._make_env("asterix", r["seed"]); inner = env.env; obsf = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(r["seed"] + 1_000_003)
    for t in range(T):
        z = wsp.logits(net, obsf()); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if t == T - 1:
            y = inner.player_y
            mv = r["last3"][-2]["eff"]
            ty = max(1, y - 1) if mv == 2 else min(8, y + 1)
            tst = own_row_status(inner, ty)
            side = range(1, y) if mv == 2 else range(y + 1, 9)
            g = any(own_row_status(inner, rr) == "gold_approach" for rr in side)
            tgt[tst] += 1
            gold_side["approaching gold on the side moved toward" if g else "no approaching gold on that side"] += 1
            combo[(r["last3"][-2]["st"], tst)] += 1
        env.act(a)
print("sticky-vertical deaths analysed:", sum(tgt.values()))
print("status of row entered at T-1:", sorted(tgt.items(), key=lambda kv: -kv[1]))
print("gold on side moved toward at T-1:", dict(gold_side))
print("(own row, entered row) at T-1, top:", combo.most_common(8))

# claim 10 follow-up
print("\nfatal pairs WITH a safe vertical alternative (seeds 0..99): policy prob distribution")
vals = collections.defaultdict(list)
for r in C[:100]:
    for s in r["log"]:
        safe = [b for b in (0, 2, 4) if not s["F"][b]]
        if not safe:
            continue
        for b in (0, 2, 4):
            if s["F"][b]:
                pr = s["p"][b] + (s["p"][5] if b == 0 else 0.0)
                key = ("edge" if s["y"] in (1, 8) else "mid") + ("/own-flagged" if s["u"][0] > 0.3 else "/own-clear")
                vals[key].append(pr)
for k, v in sorted(vals.items()):
    v = np.array(v)
    print(f"  {k:18s} n={len(v):5d} median {np.median(v):.5f} p99 {np.percentile(v,99):.4f} max {v.max():.4f} share>0.007 {(v>0.007).mean():.4f} n>0.042 {(v>0.042).sum()}")
