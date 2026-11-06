import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import pickle, collections, numpy as np
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/"
for w in ["claude","astra"]:
    eps = pickle.load(open(D+f"eps_{w}_200.pkl","rb"))
    ln = np.array([e["steps"] for e in eps])
    print(w, "n", len(eps), "seeds", eps[0]["seed"], eps[-1]["seed"], "mean len %.1f" % ln.mean(),
          "steps>205:", int((ln>205).sum()), "steps>=205:", int((ln>=205).sum()), "steps>=817:", int((ln>=817).sum()), "steps>817:", int((ln>817).sum()))
    C = [e["cls"] for e in eps if e["died"]]
    pol = [c for c in C if not (c["sticky"] and not c["chosen_fatal"]) and c["safe_vert"]]
    if w=="claude":
        print(" policy-sampled deaths n=%d p_fatal min %.4f max %.4f sorted %s" % (len(pol), min(c["p_fatal"] for c in pol), max(c["p_fatal"] for c in pol), sorted(round(c["p_fatal"],4) for c in pol)))
        print(" policy-death player rows:", [c["player"] for c in pol])
        st = [c for c in C if c["sticky"] and not c["chosen_fatal"]]
        print(" sticky deaths by repeated (effective) action:", collections.Counter(c["eff"] for c in st), " prev_last:", collections.Counter(c["prev_last"] for c in st))
