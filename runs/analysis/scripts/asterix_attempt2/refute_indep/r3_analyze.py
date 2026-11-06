"""Analyse run_*.pkl from r2_runner.py for claims 2,3,4,8,10."""
import pickle, collections
import numpy as np

D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep/"
C = pickle.load(open(D + "run_claude_200.pkl", "rb"))
A = pickle.load(open(D + "run_astra_200.pkl", "rb"))
NM = "nlurdf"

# ---------------- claim 2: detection on real states, seeds 0..99 ----------------
print("=== claim 2: one-step danger detection, Claude seeds 0..99 ===")
cnt = collections.Counter(); pf = []; sq = collections.Counter()
for r in C[:100]:
    for s in r["log"]:
        for i, b in enumerate((0, 2, 4)):
            fat = s["F"][b]
            u = s["u"][i]
            cnt[(fat, u > 0.9)] += 1
            if fat:
                pr = s["p"][b] + (s["p"][5] if b == 0 else 0.0)
                pf.append(pr)
                if pr > 0.01:
                    y = s["y"]
                    own_near = s["u"][0] > 0.3  # own-row (stay) unit at near-danger level or above
                    sq[("edge" if y in (1, 8) else "mid", "own_row_flagged" if own_near else "own_row_clear")] += 1
pf = np.array(pf)
print("states:", sum(len(r["log"]) for r in C[:100]), "pairs:", sum(cnt.values()))
print("(fatal, unit>0.9):", dict(cnt))
print("recall %d/%d" % (cnt[(True, True)], cnt[(True, True)] + cnt[(True, False)]),
      "false alarms %d/%d = %.4f" % (cnt[(False, True)], cnt[(False, True)] + cnt[(False, False)], cnt[(False, True)] / (cnt[(False, True)] + cnt[(False, False)])))
print("policy prob on fatal pairs: median %.6f mean %.5f p90 %.5f max %.4f share>0.01 %.4f (n>0.01 = %d)" % (
    np.median(pf), pf.mean(), np.percentile(pf, 90), pf.max(), (pf > 0.01).mean(), (pf > 0.01).sum()))
print("fatal pairs with p>0.01 by (edge row?, own-row stay unit>0.3?):", dict(sq))
# min unit value among fatal pairs
mins = [s["u"][i] for r in C[:100] for s in r["log"] for i, b in enumerate((0, 2, 4)) if s["F"][b]]
print("min gated-unit value on a fatal pair: %.4f" % min(mins))

# ---------------- claim 3: death causes, Claude seeds 0..199 ----------------
print("\n=== claim 3: death causes, Claude seeds 0..199 ===")
dead = [r for r in C if r["died"]]
print("died", len(dead), "of", len(C))
cat = collections.Counter(); sticky_vert = []
pol_pf = []
for r in dead:
    s = r["last3"][-1]
    a, eff, last = s["a"], s["eff"], s["last"]
    chosen_fatal = s["F"][a]
    if eff != a:  # sticky fired and changed the action (eff == last)
        assert eff == last
        if not chosen_fatal:
            k = "sticky repeat of %s, chosen %s safe" % (NM[eff], NM[a])
            if eff in (2, 4):
                sticky_vert.append(r)
        else:
            k = "sticky changed action but chosen also fatal"
    else:
        safe_alt = [b for b in (0, 2, 4) if not s["F"][b]]
        k = "executed == chosen (policy sampled fatal), safe vertical alt exists=%s" % bool(safe_alt)
        pol_pf.append((r["seed"], s["t"], NM[a], float(sum(s["p"][b] for b in range(6) if s["F"][b])), s["y"], s["st"]))
    cat[k] += 1
for k, v in sorted(cat.items(), key=lambda kv: -kv[1]):
    print(f"  {v:4d}  {k}")
print("sticky repeats of a vertical move with safe chosen action:", len(sticky_vert), "/", len(dead))
# was the repeated move itself the previous step's executed action? (by definition yes) -- check prev step eff
ok = sum(1 for r in sticky_vert if r["last3"][-2]["eff"] == r["last3"][-1]["eff"])
print("  of these, previous step's executed action equals repeated action:", ok)
print("expected deaths (sum over steps): sticky %.1f, policy %.1f, total %.1f vs %d deaths" % (
    sum(r["es"] for r in C), sum(r["ep"] for r in C), sum(r["es"] + r["ep"] for r in C), len(dead)))
print("policy-sampled deaths (seed, t, action, P(fatal set), row, own-row status):")
for x in pol_pf:
    print("   ", x[0], x[1], x[2], "%.4f" % x[3], x[4], x[5])

# ---------------- claim 4: origin of the repeated move ----------------
print("\n=== claim 4: step T-1 before sticky-vertical deaths ===")
orig = collections.Counter(); vol = collections.Counter(); pm = []; stay_safe = collections.Counter()
for r in sticky_vert:
    prev = r["last3"][-2]
    mv = r["last3"][-1]["eff"]
    assert prev["eff"] == mv
    orig[prev["st"]] += 1
    vol["voluntary (chosen==executed at T-1)" if prev["a"] == prev["eff"] else "itself sticky at T-1"] += 1
    pm.append(prev["p"][mv])
    stay_safe["noop at T-1 safe" if not prev["F"][0] else "noop at T-1 fatal"] += 1
print("own-row status at T-1:", sorted(orig.items(), key=lambda kv: -kv[1]))
print("voluntary?", dict(vol))
print("noop safe at T-1?", dict(stay_safe))
pm = np.array(pm)
print("P(policy picks that move) at T-1: median %.3f quartiles %s" % (np.median(pm), np.percentile(pm, [25, 75]).round(3)))
safe_rows = orig["empty"] + orig["enemy_passed"] + orig.get("gold_passed", 0)
print("from empty: %d, from passed-enemy: %d, from passed-gold: %d, total %d" % (orig["empty"], orig["enemy_passed"], orig.get("gold_passed", 0), len(sticky_vert)))
both = sum(1 for r in sticky_vert if r["last3"][-2]["st"] in ("empty", "enemy_passed") and r["last3"][-2]["a"] == r["last3"][-2]["eff"])
print("voluntary AND from empty/passed-enemy row:", both)

# ---------------- claim 8: episode lengths ----------------
print("\n=== claim 8: lengths ===")
for name, R in (("claude", C), ("astra", A)):
    ln = np.array([r["steps"] for r in R])
    print(f"{name}: mean len {ln.mean():.1f}; steps>205 {int((ln > 205).sum())}; steps>=205 {int((ln >= 205).sum())}; "
          f"steps>=817 {int((ln >= 817).sum())}; steps>817 {int((ln > 817).sum())}; median {np.median(ln):.0f}; deaths {sum(r['died'] for r in R)}")

# ---------------- claim 10: seed 9 ----------------
print("\n=== claim 10: seed 9 last steps ===")
r9 = C[9]
print("seed 9 steps", r9["steps"], "died", r9["died"])
for s in r9["log"][-4:]:
    print(f"  t={s['t']} row {s['y']} own {s['st']} P(n,u,d)=({s['p'][0]:.3f},{s['p'][2]:.3f},{s['p'][4]:.3f}) F(n,u,d)={[s['F'][b] for b in (0,2,4)]} "
          f"units(s,u,d)={tuple(round(v,2) for v in s['u'])} chosen {NM[s['a']]} executed {NM[s['eff']]}")
