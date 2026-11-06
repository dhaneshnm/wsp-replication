import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import pickle, collections
import numpy as np
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/"
for which in sys.argv[1:]:
    eps = pickle.load(open(D + f"eps_{which}_200.pkl", "rb"))
    print("=====", which, "episodes", len(eps))
    sc = np.array([e["score"] for e in eps]); ln = np.array([e["steps"] for e in eps])
    print("score mean %.2f median %.1f; len mean %.1f median %.1f; quantiles len 10/25/50/75/90:" % (sc.mean(), np.median(sc), ln.mean(), np.median(ln)),
          np.percentile(ln, [10, 25, 50, 75, 90]).round())
    print("died:", sum(e["died"] for e in eps), "timeouts:", sum(not e["died"] for e in eps))
    print("columns ever occupied:", collections.Counter(tuple(e["cols"]) for e in eps))
    rows = sum(e["rows"] for e in eps); print("row occupancy share 1..8:", (rows[1:9] / rows.sum()).round(3))
    print("gold per 100 steps: %.2f" % (100 * sc.sum() / ln.sum()))
    dead = [e for e in eps if e["died"]]
    C = [e["cls"] for e in dead]
    cnt = lambda f: collections.Counter(f(c) for c in C)
    print("mechanism:", cnt(lambda c: c["mech"]))
    print("move_speed at death:", sorted(cnt(lambda c: c["move_speed"]).items()))
    print("spawn_speed at death:", sorted(cnt(lambda c: c["spawn_speed"]).items()))
    print("enemies on board at death:", sorted(cnt(lambda c: c["n_enemies"]).items()))
    print("sticky (effective != chosen):", cnt(lambda c: c["sticky"]))
    print("chosen action fatal:", cnt(lambda c: c["chosen_fatal"]))
    def cat(c):
        if c["sticky"] and not c["chosen_fatal"]:
            return "sticky repeat of previous action killed (chosen action was safe)"
        if not c["safe_vert"]:
            return "trapped: no safe vertical action at death step"
        return "policy sampled a fatal action while a safe vertical one existed"
    print("category:", cnt(cat))
    tr = [c for c in C if not c["safe_vert"]]
    print("  trapped: horizontal move would have saved:", collections.Counter(bool(c["safe_any"]) for c in tr))
    print("  trapped: vertical escape existed 1 step earlier:", collections.Counter(c["look"].get(1) for c in tr))
    print("  trapped: vertical escape existed 2 steps earlier:", collections.Counter(c["look"].get(2) for c in tr))
    print("  trapped: vertical escape existed 3 steps earlier:", collections.Counter(c["look"].get(3) for c in tr))
    print("  trapped: any(5-action) escape existed 3 steps earlier:", collections.Counter(c["look"].get("3_any") for c in tr))
    pol = [c for c in C if cat(c).startswith("policy")]
    print("  policy-sampled deaths: p_fatal quantiles", np.percentile([c["p_fatal"] for c in pol], [10,50,90]).round(3) if pol else None,
          "chosen:", collections.Counter(c["chosen"] for c in pol))
    st = [c for c in C if cat(c).startswith("sticky")]
    print("  sticky deaths: (repeated, chosen) pairs:", collections.Counter((c["eff"], c["chosen"]) for c in st))
    print("player col at death:", collections.Counter(c["player"][1] for c in C))
