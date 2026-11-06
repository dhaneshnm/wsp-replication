"""Death-cause cross-tab, trapped-death sideways escape, rows, columns, p(left/right/fire),
repeat-fatal fraction, treasure capture -- from my own runner's pickles."""
import sys
HERE = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1/indep_verify"
import pickle
from collections import Counter
import numpy as np

ACT = ["noop", "left", "up", "right", "down", "fire"]
for which in ["claude01", "astra01", "claude00"]:
    res = pickle.load(open(f"{HERE}/main_{which}.pkl", "rb"))
    print(f"===== {which} =====")
    cols = sorted(set(c for r in res for c in r["cols"]))
    print("columns ever occupied (all steps, all episodes):", cols)
    print("max p(left|right|fire) over all visited states:", max(r["agg"]["pmax_lrf"] for r in res),
          " min:", min(r["agg"]["pmin_lrf"] for r in res))
    A = {k: sum(r["agg"][k] for r in res if isinstance(r["agg"][k], int)) for k in ["states", "rep_fatal", "prev_move", "prev_move_rep_fatal"]}
    print("states:", A["states"], "| repeat of last executed action fatal:", A["rep_fatal"],
          f"({A['rep_fatal']/A['states']:.4f})", "| states whose last action was up/down:", A["prev_move"],
          "| of those, repeat fatal:", A["prev_move_rep_fatal"],
          f"({A['prev_move_rep_fatal']/max(1,A['prev_move']):.4f})")
    gs = sum(r["gold_spawned"] for r in res); cap = sum(r["score"] for r in res)
    print(f"treasure spawned {gs}, captured {cap:.0f}, rate {cap/gs:.4f}")
    cause = Counter(); rows_by = {}
    trapped_lr_escape = 0; trapped_n = 0
    detail = Counter()
    for r in res:
        d = r["steps"][-1]
        f = d["fatal"]
        own = [0, 2, 4]
        all_own_fatal = all(f[b] for b in own)
        sticky_diff = d["fired"] and d["a_exec"] != d["a"]
        if sticky_diff and not f[d["a"]]:
            c = "sticky(repeat fatal, sampled action safe)"
        elif all_own_fatal:
            c = "trapped(noop/up/down all fatal)"
        elif sticky_diff:
            c = "sticky but sampled also fatal (not trapped)"
        else:
            c = "sampled fatal, a safe noop/up/down existed"
        cause[c] += 1
        rows_by.setdefault(c, Counter())[d["row"]] += 1
        detail[(c, ACT[d["prev"]], ACT[d["a"]], ACT[d["a_exec"]])] += 1
        if all_own_fatal:
            trapped_n += 1
            trapped_lr_escape += (not f[1]) or (not f[3])
    print("death causes:", dict(cause))
    for c, rc in rows_by.items():
        print("  rows for", c, dict(sorted(rc.items())))
    print(f"trapped deaths: {trapped_n}; of these, left or right would survive this step: {trapped_lr_escape}")
    print("detail (cause, prev executed, sampled, executed): count")
    for k, v in sorted(detail.items(), key=lambda kv: -kv[1]):
        print("   ", k, v)
